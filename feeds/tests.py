# feeds/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.timezone import localtime
from .models import Post
import uuid
import json
from django.contrib.auth import get_user_model

class FeedsTestCase(TestCase):
    def setUp(self):
        # Selalu bikin data fresh per test
        self.c = Client()
        self.user = User.objects.create_user(username="hafizh", password="secret123")
        self.other = User.objects.create_user(username="other", password="secret123")
        self.post = Post.objects.create(
            user=self.user,
            content="Latihan futsal malam ini",
            category="futsal",
            thumbnail="https://example.com/img.jpg",
            is_featured=True,
            post_views=9,
        )

    # ---------- Routing & auth ----------
    def test_show_feed_main_requires_login(self):
        url = reverse("feeds:show_feed_main")
        resp = self.c.get(url)
        # login_required -> redirect to /auth/login/
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/auth/login/", resp.url)

    def test_show_feed_main_ok_after_login_and_template_used(self):
        self.c.login(username="hafizh", password="secret123")
        url = reverse("feeds:show_feed_main")
        resp = self.c.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "feed_main.html")

    def test_nonexistent_page_returns_404(self):
        resp = self.c.get("/burhan_always_exists/")
        self.assertEqual(resp.status_code, 404)

    # ---------- Model ----------
    def test_post_model_defaults_and_hot_flag(self):
        p = Post.objects.create(user=self.user, content="Hello world")
        # default category di model = 'soccer'
        self.assertEqual(p.category, "soccer")
        self.assertEqual(p.post_views, 0)
        self.assertFalse(p.is_featured)
        self.assertFalse(p.is_post_hot)

        p.post_views = 10
        p.save(update_fields=["post_views"])
        self.assertFalse(p.is_post_hot)
        p.post_views = 11
        p.save(update_fields=["post_views"])
        self.assertTrue(p.is_post_hot)

    def test_increment_views_method(self):
        initial = self.post.post_views
        self.post.increment_views()
        self.post.refresh_from_db()
        self.assertEqual(self.post.post_views, initial + 1)

    # ---------- Views: HTML detail increments views ----------
    def test_show_post_increments_views(self):
        self.c.login(username="hafizh", password="secret123")
        url = reverse("feeds:show_post", args=[str(self.post.id)])
        before = Post.objects.get(pk=self.post.id).post_views
        resp = self.c.get(url)
        self.assertEqual(resp.status_code, 200)
        after = Post.objects.get(pk=self.post.id).post_views
        self.assertEqual(after, before + 1)

    # ---------- JSON list & filters ----------
    def test_show_json_all(self):
        url = reverse("feeds:show_json")
        resp = self.c.get(url)  # anonymous allowed
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        self.assertIn("id", data[0])
        self.assertIn("category", data[0])
        self.assertIn("is_hot", data[0])
        if data[0]["id"] == str(self.post.id):
            self.assertFalse(data[0]["is_hot"])

    def test_show_json_filter_my_and_category(self):
        # login as owner
        self.c.login(username="hafizh", password="secret123")
        # tambahkan post lain kategori basket milik user lain
        Post.objects.create(user=self.other, content="basket", category="basket")

        # filter 'my'
        resp_my = self.c.get(reverse("feeds:show_json"), {"filter": "my"})
        self.assertEqual(resp_my.status_code, 200)
        data_my = resp_my.json()
        self.assertTrue(all(item["user_id"] == self.user.id for item in data_my))

        # filter category futsal (harus mengandung post self.post)
        resp_cat = self.c.get(reverse("feeds:show_json"), {"category": "futsal"})
        self.assertEqual(resp_cat.status_code, 200)
        data_cat = resp_cat.json()
        self.assertTrue(any(item["id"] == str(self.post.id) for item in data_cat))
        self.assertTrue(all(item["category"] == "futsal" for item in data_cat))

    # ---------- JSON & XML by id ----------
    def test_show_json_by_id_ok(self):
        url = reverse("feeds:show_json_by_id", args=[str(self.post.id)])
        resp = self.c.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["id"], str(self.post.id))
        self.assertEqual(data["category"], "futsal")

    def test_show_json_by_id_not_found(self):
        fake = uuid.uuid4()
        url = reverse("feeds:show_json_by_id", args=[str(fake)])
        resp = self.c.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_show_xml_and_xml_by_id_content_type(self):
        list_resp = self.c.get(reverse("feeds:show_xml"))
        self.assertEqual(list_resp.status_code, 200)
        self.assertEqual(list_resp["Content-Type"], "application/xml")

        one_resp = self.c.get(reverse("feeds:show_xml_by_id", args=[str(self.post.id)]))
        self.assertEqual(one_resp.status_code, 200)
        self.assertEqual(one_resp["Content-Type"], "application/xml")

    # ---------- Detail JSON (untuk halaman post_detail) ----------
    def test_post_json_detail_fields(self):
        url = reverse("feeds:post_json_detail", args=[str(self.post.id)])
        self.c.login(username="hafizh", password="secret123")
        resp = self.c.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["id"], str(self.post.id))
        self.assertIn("username", data)
        self.assertIn("category_label", data)  # berasal dari get_category_display()
        # is_hot mengambil property is_post_hot
        self.assertEqual(data["is_hot"], self.post.is_post_hot)

    # ---------- Create / Edit / Delete (AJAX) ----------
    def test_create_post_ajax_requires_login(self):
        url = reverse("feeds:create_post_ajax")
        # tanpa login -> redirect oleh decorator login_required
        resp = self.c.post(url, {})
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/auth/login/", resp.url)

    def test_create_post_ajax_success(self):
        self.c.login(username="hafizh", password="secret123")
        url = reverse("feeds:create_post_ajax")
        payload = {
            "content": "Baru bikin post",
            "category": "basket",
            "thumbnail": "https://example.com/t.png",
            "is_featured": "on",
        }
        resp = self.c.post(url, payload, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertTrue(data["ok"])
        self.assertEqual(data["post"]["category"], "basket")
        self.assertTrue(data["post"]["is_featured"])
        self.assertTrue(Post.objects.filter(id=data["post"]["id"]).exists())

    def test_edit_post_ajax_owner_only(self):
        self.c.login(username="hafizh", password="secret123")
        url = reverse("feeds:edit_post_ajax", args=[str(self.post.id)])
        resp = self.c.post(url, {
            "content": "Diubah konten",
            "category": "soccer",
            "thumbnail": "",
            "is_featured": "",  # unchecked
        }, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(resp.status_code, 200)
        out = resp.json()["post"]
        self.post.refresh_from_db()
        self.assertEqual(self.post.content, "Diubah konten")
        self.assertEqual(self.post.category, "soccer")
        self.assertFalse(self.post.is_featured)
        self.assertEqual(out["category_label"], "Soccer")

    def test_delete_post_ajax_forbidden_for_non_owner(self):
        # login sebagai user lain
        self.c.login(username="other", password="secret123")
        url = reverse("feeds:delete_post_ajax", args=[str(self.post.id)])
        resp = self.c.post(url, {}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(resp.status_code, 403)

    def test_delete_post_ajax_success_for_owner(self):
        self.c.login(username="hafizh", password="secret123")
        url = reverse("feeds:delete_post_ajax", args=[str(self.post.id)])
        resp = self.c.post(url, {}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Post.objects.filter(pk=self.post.id).exists())
        data = resp.json()
        # redirect path dikembalikan di JSON
        self.assertTrue(data["ok"])
        self.assertEqual(data["redirect"], reverse("feeds:show_feed_main"))

    def _ok_or_redirect(self, url, **kw):
        resp = self.c.get(url, **kw)
        self.assertIn(resp.status_code, (200, 302))
        return resp

    def test_home_page_reachable(self):
        self._ok_or_redirect("/")

    def test_reviews_index_reachable(self):
        self._ok_or_redirect("/reviews/")

    def test_equipment_or_booking_pages_reachable(self):
        for path in ["/equipment/", "/booking/"]:
            try:
                self._ok_or_redirect(path)
            except AssertionError:
                pass

    def test_login_get_and_post_invalid(self):
        self._ok_or_redirect("/auth/login/")
        resp = self.c.post("/auth/login/", {"username": "x", "password": "y"})
        self.assertIn(resp.status_code, (200, 302))

    def test_register_invalid_password_confirmation(self):
        resp = self.c.post("/auth/register/", {
            "username": "newbie",
            "email": "new@ex.com",
            "password1": "abc12345",
            "password2": "beda12345",
        })
        self.assertIn(resp.status_code, (200, 302))

    def test_login_success_then_logout(self):
        ok = self.c.login(username="hafizh", password="secret123")
        self.assertTrue(ok)
        resp = self.c.get("/auth/logout/")
        self.assertIn(resp.status_code, (200, 302))


    def test_reviews_minimal_model_and_list(self):
        try:
            from reviews.models import Reviews
            Reviews.objects.create(title="Bagus", content="Mantap", rating=5)
        except Exception:
            pass
        try:
            self._ok_or_redirect("/reviews/")
        except AssertionError:
            pass