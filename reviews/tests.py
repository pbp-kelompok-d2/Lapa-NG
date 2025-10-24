from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
import json
from reviews.models import Reviews
from authentication.models import CustomUser

class ReviewTestCase(TestCase):
    def setUp(self):
        # Membuat user biasa (customer)
        self.user_customer = User.objects.create_user(username='testcustomer', password='testpass123')
        self.custom_user_customer = CustomUser.objects.create(user=self.user_customer, name='Test Customer', role='customer', number='12345')

        # Membuat user lain (owner)
        self.user_owner = User.objects.create_user(username='testowner', password='testpass123')
        self.custom_user_owner = CustomUser.objects.create(user=self.user_owner, name='Test Owner', role='owner', number='67890')

        # Membuat superuser/admin
        self.superuser = User.objects.create_superuser(username='admin', password='adminpass123', email='admin@test.com')

        # Membuat sebuah review awal oleh customer
        self.review = Reviews.objects.create(
            user=self.user_customer,
            venue_name='Lapangan Keren',
            rating=5,
            comment='Sangat bagus!'
        )

        self.client = Client()
        self.review_data = {
            'venue_name': 'Lapangan Futsal Merdeka',
            'rating': 5,
            'comment': 'Lapangan sangat bagus dan bersih!'
        }

    # ===================================
    # Test untuk Model
    # ===================================
    def test_review_model_creation(self):
        """Test membuat instance model Reviews"""
        self.assertEqual(self.review.venue_name, 'Lapangan Keren')
        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.user.username, 'testcustomer')

    def test_review_string_representation(self):
        """Test representasi string dari model Review"""
        expected_str = f"Lapangan Keren - 5★ by testcustomer"
        self.assertEqual(str(self.review), expected_str)

    # ===================================
    # Test untuk Views (Halaman dan JSON)
    # ===================================
    def test_show_reviews_page(self):
        """Test halaman utama review dapat diakses (tanpa login)"""
        response = self.client.get(reverse('reviews:show_reviews'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reviews.html')

    def test_get_reviews_json_unauthenticated(self):
        """Test endpoint JSON tanpa login (can_modify harus False)"""
        response = self.client.get(reverse('reviews:get_reviews_json'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['venue_name'], 'Lapangan Keren')
        self.assertFalse(data[0]['can_modify']) # Pastikan can_modify False

    def test_get_reviews_json_as_owner_of_review(self):
        """Test endpoint JSON sebagai pemilik review (can_modify harus True)"""
        self.client.login(username='testcustomer', password='testpass123')
        response = self.client.get(reverse('reviews:get_reviews_json'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data[0]['can_modify'])

    def test_get_reviews_json_as_other_user(self):
        """Test endpoint JSON sebagai user lain (can_modify harus False)"""
        self.client.login(username='testowner', password='testpass123')
        response = self.client.get(reverse('reviews:get_reviews_json'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data[0]['can_modify'])

    def test_get_my_reviews_filter(self):
        """Test filter 'my_reviews' hanya mengembalikan review milik user"""
        # Buat review lain oleh owner
        Reviews.objects.create(user=self.user_owner, venue_name='Venue Owner', rating=3, comment='Oke.')
        
        self.client.login(username='testcustomer', password='testpass123')
        response = self.client.get(reverse('reviews:get_reviews_json'), {'filter': 'my_reviews'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['user_username'], 'testcustomer')
    
    def test_get_all_reviews_filter(self):
        """Test filter 'all' mengembalikan semua review"""
        Reviews.objects.create(user=self.user_owner, venue_name='Venue Owner', rating=3, comment='Oke.')
        
        self.client.login(username='testcustomer', password='testpass123')
        response = self.client.get(reverse('reviews:get_reviews_json'), {'filter': 'all'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 2)

    def test_get_review_detail_json(self):
        """Test endpoint untuk detail satu review"""
        response = self.client.get(reverse('reviews:get_review_detail_json', args=[self.review.pk]))
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['data']['pk'], self.review.pk)

    def test_get_review_detail_not_found(self):
        """Test endpoint detail jika review tidak ada"""
        response = self.client.get(reverse('reviews:get_review_detail_json', args=[999]))
        self.assertEqual(response.status_code, 500) # get_object_or_404 akan raise Http404, ditangkap sbg Exception
    
    # ===================================
    # Test untuk AJAX: Add, Edit, Delete
    # ===================================

    # --- ADD REVIEW ---
    def test_add_review_ajax_success(self):
        """Test berhasil menambah review sebagai customer"""
        self.client.login(username='testcustomer', password='testpass123')
        response = self.client.post(
            reverse('reviews:add_review_ajax'),
            data=json.dumps(self.review_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Reviews.objects.count(), 2)

    def test_add_review_unauthenticated(self):
        """Test gagal menambah review jika belum login (akan redirect)"""
        response = self.client.post(reverse('reviews:add_review_ajax'), data=json.dumps(self.review_data), content_type='application/json')
        self.assertEqual(response.status_code, 302) # Redirect ke halaman login

    def test_add_review_as_owner(self):
        """Test gagal menambah review sebagai owner (forbidden)"""
        self.client.login(username='testowner', password='testpass123')
        response = self.client.post(reverse('reviews:add_review_ajax'), data=json.dumps(self.review_data), content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_add_review_invalid_data(self):
        """Test menambah review dengan data tidak valid"""
        self.client.login(username='testcustomer', password='testpass123')
        invalid_data = {'venue_name': '', 'rating': 6, 'comment': ''}
        response = self.client.post(reverse('reviews:add_review_ajax'), data=json.dumps(invalid_data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Reviews.objects.count(), 1)
        
    def test_add_review_invalid_json(self):
        """Test menambah review dengan JSON tidak valid"""
        self.client.login(username='testcustomer', password='testpass123')
        response = self.client.post(reverse('reviews:add_review_ajax'), data='not a json', content_type='application/json')
        self.assertEqual(response.status_code, 400)

    # --- EDIT REVIEW ---
    def test_edit_review_ajax_success(self):
        """Test berhasil mengedit review"""
        self.client.login(username='testcustomer', password='testpass123')
        updated_data = {'venue_name': 'Venue Diedit', 'rating': 4, 'comment': 'Diedit'}
        response = self.client.post(
            reverse('reviews:edit_review_ajax', args=[self.review.pk]),
            data=json.dumps(updated_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.review.refresh_from_db()
        self.assertEqual(self.review.venue_name, 'Venue Diedit')
        
    def test_edit_review_invalid_data(self):
        """Test gagal mengedit review dengan data tidak valid"""
        self.client.login(username='testcustomer', password='testpass123')
        invalid_data = {'venue_name': '', 'rating': 0, 'comment': 'Invalid'}
        response = self.client.post(
            reverse('reviews:edit_review_ajax', args=[self.review.pk]),
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
    def test_edit_review_not_found(self):
        """Test gagal mengedit review yang tidak ada"""
        self.client.login(username='testcustomer', password='testpass123')
        updated_data = {'venue_name': 'Venue Diedit', 'rating': 4, 'comment': 'Diedit'}
        response = self.client.post(
            reverse('reviews:edit_review_ajax', args=[999]),
            data=json.dumps(updated_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 500)

    # --- DELETE REVIEW ---
    def test_delete_review_ajax_success(self):
        """Test berhasil menghapus review"""
        self.client.login(username='testcustomer', password='testpass123')
        response = self.client.post(reverse('reviews:delete_review_ajax', args=[self.review.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Reviews.objects.count(), 0)

    def test_delete_review_not_found(self):
        """Test gagal menghapus review yang tidak ada"""
        self.client.login(username='testcustomer', password='testpass123')
        response = self.client.post(reverse('reviews:delete_review_ajax', args=[999]))
        self.assertEqual(response.status_code, 500)