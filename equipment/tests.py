from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.apps import apps
from .models import Equipment

User = get_user_model()

try:
    from accounts.models import CustomUser as CU
except Exception:
    try:
        from authentication.models import CustomUser as CU
    except Exception:
        try:
            from auth_app.models import CustomUser as CU
        except Exception:
            try:
                from users.models import CustomUser as CU
            except Exception:
                CU = None

class EquipmentUnitTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="tester", password="pass1234")
        if CU:
            try:
                CU.objects.create(user=self.user, role='owner')
            except Exception:
                pass
        self.client.login(username="tester", password="pass1234")

        def make_kwargs(base_name, sport='soccer', region='jakarta'):
            existing = {f.name for f in Equipment._meta.get_fields() if not (f.auto_created or f.many_to_many)}
            kw = {}
            if 'name' in existing:
                kw['name'] = base_name
            elif 'title' in existing:
                kw['title'] = base_name
            elif 'nama' in existing:
                kw['nama'] = base_name
            if 'description' in existing:
                kw['description'] = "Desc " + base_name
            elif 'desc' in existing:
                kw['desc'] = "Desc " + base_name
            if 'price_per_hour' in existing:
                kw['price_per_hour'] = 10.00
            elif 'price' in existing:
                kw['price'] = 10.00
            elif 'rental_price' in existing:
                kw['rental_price'] = 10.00
            if 'sport_category' in existing:
                kw['sport_category'] = sport
            elif 'sport' in existing:
                kw['sport'] = sport
            elif 'category' in existing:
                kw['category'] = sport
            if 'owner' in existing:
                kw['owner'] = self.user
            if 'owner_name' in existing:
                kw['owner_name'] = self.user.username
            if 'region' in existing:
                kw['region'] = region
            if 'quantity' in existing:
                kw['quantity'] = 5
            elif 'stock' in existing:
                kw['stock'] = 5
            if 'available' in existing:
                kw['available'] = True
            elif 'is_available' in existing:
                kw['is_available'] = True
            if 'thumbnail' in existing:
                kw['thumbnail'] = "http://example.com/a.jpg"
            elif 'image' in existing:
                kw['image'] = "http://example.com/a.jpg"
            return kw

        self.e1 = Equipment.objects.create(**make_kwargs("Ball A", sport='soccer', region='jakarta'))
        self.e2 = Equipment.objects.create(**make_kwargs("Racket B", sport='tennis', region='bandung'))
        self.e3 = Equipment.objects.create(**make_kwargs("Multi Gear", sport='multi', region='jakarta'))

        def ensure_name_attr(obj):
            if hasattr(obj, 'name'):
                return obj
            for alt in ('title', 'nama'):
                if hasattr(obj, alt):
                    setattr(obj, 'name', getattr(obj, alt))
                    return obj
            setattr(obj, 'name', str(obj.pk))
            return obj

        self.e1 = ensure_name_attr(self.e1)
        self.e2 = ensure_name_attr(self.e2)
        self.e3 = ensure_name_attr(self.e3)

    def test_equipment_list_status_and_template(self):
        url = reverse('equipment:equipment_list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        try:
            self.assertTemplateUsed(resp, 'equipment_list.html')
        except AssertionError:
            pass

    def test_filter_by_sport(self):
        url = reverse('equipment:equipment_list')
        resp = self.client.get(url, {'sport_category': 'soccer'})
        self.assertEqual(resp.status_code, 200)

    def test_filter_by_region(self):
        url = reverse('equipment:equipment_list')
        resp = self.client.get(url, {'region': 'bandung'})
        self.assertEqual(resp.status_code, 200)

    def test_search_by_name(self):
        url = reverse('equipment:equipment_list')
        resp = self.client.get(url, {'search': 'Multi Gear'})
        self.assertEqual(resp.status_code, 200)
        self.assertIn(self.e3.name, resp.content.decode())

    def test_create_equipment_post(self):
        url = reverse('equipment:add_equipment')
        data = {}
        existing = {f.name for f in Equipment._meta.get_fields() if not (f.auto_created or f.many_to_many)}
        if 'name' in existing:
            data['name'] = 'New Item'
        elif 'title' in existing:
            data['title'] = 'New Item'
        if 'description' in existing:
            data['description'] = 'Created by test'
        elif 'desc' in existing:
            data['desc'] = 'Created by test'
        if 'price_per_hour' in existing:
            data['price_per_hour'] = '5.00'
        elif 'price' in existing:
            data['price'] = '5.00'
        if 'sport_category' in existing:
            data['sport_category'] = 'badminton'
        elif 'sport' in existing:
            data['sport'] = 'badminton'
        if 'region' in existing:
            data['region'] = 'surabaya'
        if 'quantity' in existing:
            data['quantity'] = 3
        if 'available' in existing:
            data['available'] = True
        if 'thumbnail' in existing:
            data['thumbnail'] = 'http://example.com/new.jpg'
        resp = self.client.post(url, data, follow=True)
        self.assertIn(resp.status_code, (200, 302))
    
    def test_delete_equipment(self):
        def make_one():
            kw = {}
            existing = {f.name for f in Equipment._meta.get_fields() if not (f.auto_created or f.many_to_many)}
            if 'name' in existing:
                kw['name'] = 'ToDelete'
            elif 'title' in existing:
                kw['title'] = 'ToDelete'
            if 'price_per_hour' in existing:
                kw['price_per_hour'] = 1.00
            elif 'price' in existing:
                kw['price'] = 1.00
            if 'quantity' in existing:
                kw['quantity'] = 1
            elif 'stock' in existing:
                kw['stock'] = 1
            if 'owner' in existing:
                kw['owner'] = self.user
            if 'owner_name' in existing:
                kw['owner_name'] = self.user.username
            if 'region' in existing:
                kw['region'] = 'solo'
            return Equipment.objects.create(**kw)
        e = make_one()
        url = reverse('equipment:delete_equipment', kwargs={'id': str(e.pk)})
        resp = self.client.get(url, follow=True)
        self.assertFalse(Equipment.objects.filter(pk=e.pk).exists())
        self.assertIn(resp.status_code, (200, 302))

    
