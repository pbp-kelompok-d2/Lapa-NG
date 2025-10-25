from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
import json
from reviews.models import Reviews
from authentication.models import CustomUser

class ReviewFeatureTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Membuat user customer
        self.user_customer = User.objects.create_user(username='testcustomer', password='testpass123')
        CustomUser.objects.create(user=self.user_customer, name='Test Customer', role='customer', number='12345')

        # Membuat user owner (yang tidak akan bisa membuat review)
        self.user_owner = User.objects.create_user(username='testowner', password='testpass123')
        CustomUser.objects.create(user=self.user_owner, name='Test Owner', role='owner', number='67890')

        # Membuat review awal oleh customer
        self.review1 = Reviews.objects.create(
            user=self.user_customer,
            venue_name='Lapangan Futsal Keren',
            sport_type='futsal',
            rating=5,
            comment='Sangat bagus!'
        )

        # Membuat review kedua oleh user lain untuk pengujian filter
        self.other_user = User.objects.create_user(username='othercustomer', password='testpass123')
        CustomUser.objects.create(user=self.other_user, name='Other Customer', role='customer', number='54321')
        self.review2 = Reviews.objects.create(
            user=self.other_user,
            venue_name='Stadion Basket',
            sport_type='basket',
            rating=4,
            comment='Cukup baik.'
        )
        
        # Data valid untuk membuat review baru via POST request
        self.valid_review_data = {
            'venue_name': 'Lapangan Badminton Jaya',
            'sport_type': 'badminton',
            'rating': 4,
            'comment': 'Shuttlecock disediakan!'
        }

    # 1. Pengujian Model
    def test_review_model_creation_and_str(self):
        """Memastikan model Review dibuat dengan benar dan __str__ berfungsi."""
        self.assertEqual(self.review1.venue_name, 'Lapangan Futsal Keren')
        self.assertEqual(self.review1.sport_type, 'futsal')
        self.assertEqual(self.review1.rating, 5)
        self.assertEqual(str(self.review1), f"{self.review1.venue_name} - {self.review1.rating}★ by {self.user_customer.username}")

    # 2. Pengujian Views (Halaman dan JSON)
    def test_show_reviews_page_loads_correctly(self):
        """Memastikan halaman utama reviews dapat diakses dan menggunakan template yang benar."""
        response = self.client.get(reverse('reviews:show_reviews'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reviews.html')
        self.assertIn('sports', response.context) # Memastikan data sport dikirim ke template

    def test_get_reviews_json_unauthenticated(self):
        """Memastikan endpoint JSON mengembalikan data dan can_modify bernilai False jika tidak login."""
        response = self.client.get(reverse('reviews:get_reviews_json'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertFalse(data[0]['can_modify']) # Review milik other_user
        self.assertFalse(data[1]['can_modify']) # Review milik user_customer

    def test_get_reviews_json_as_owner_of_review(self):
        """Memastikan can_modify bernilai True jika login sebagai pemilik review."""
        self.client.login(username='testcustomer', password='testpass123')
        response = self.client.get(reverse('reviews:get_reviews_json'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Cari review milik testcustomer
        my_review_data = next((item for item in data if item['user_username'] == 'testcustomer'), None)
        self.assertTrue(my_review_data['can_modify'])

    def test_filter_my_reviews(self):
        """Memastikan filter 'my_reviews' hanya mengembalikan review milik user yang login."""
        self.client.login(username='testcustomer', password='testpass123')
        response = self.client.get(reverse('reviews:get_reviews_json'), {'filter': 'my_reviews'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['user_username'], 'testcustomer')

    def test_filter_by_sport_type(self):
        """Memastikan filter 'sport_type' berfungsi dengan benar."""
        response = self.client.get(reverse('reviews:get_reviews_json'), {'sport_type': 'basket'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['sport_type'], 'Basket')
        self.assertEqual(data[0]['venue_name'], 'Stadion Basket')

    # 3. Pengujian Fungsionalitas AJAX (Add, Edit, Delete)
    
    # --- ADD ---
    def test_add_review_ajax_success_as_customer(self):
        """Memastikan customer bisa menambahkan review baru."""
        self.client.login(username='testcustomer', password='testpass123')
        response = self.client.post(
            reverse('reviews:add_review_ajax'),
            data=json.dumps(self.valid_review_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Reviews.objects.count(), 3)
        self.assertTrue(Reviews.objects.filter(venue_name='Lapangan Badminton Jaya').exists())

    def test_add_review_fails_if_not_logged_in(self):
        """Memastikan user yang belum login akan di-redirect."""
        response = self.client.post(reverse('reviews:add_review_ajax'), content_type='application/json')
        self.assertEqual(response.status_code, 302)

    def test_add_review_fails_as_owner(self):
        """Memastikan user dengan role 'owner' tidak bisa membuat review."""
        self.client.login(username='testowner', password='testpass123')
        response = self.client.post(
            reverse('reviews:add_review_ajax'),
            data=json.dumps(self.valid_review_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)

    def test_add_review_fails_with_invalid_data(self):
        """Memastikan penambahan review gagal jika data tidak valid."""
        self.client.login(username='testcustomer', password='testpass123')
        invalid_data = {'venue_name': '', 'rating': 6, 'comment': ''} # Rating > 5
        response = self.client.post(
            reverse('reviews:add_review_ajax'),
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Reviews.objects.count(), 2)

    # --- EDIT ---
    def test_edit_review_ajax_success(self):
        """Memastikan pemilik review bisa mengedit ulasannya."""
        self.client.login(username='testcustomer', password='testpass123')
        updated_data = {
            'venue_name': 'Venue Diedit', 
            'sport_type': 'soccer', 
            'rating': 3, 
            'comment': 'Telah diedit.'
        }
        response = self.client.post(
            reverse('reviews:edit_review_ajax', args=[self.review1.pk]),
            data=json.dumps(updated_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.review1.refresh_from_db()
        self.assertEqual(self.review1.venue_name, 'Venue Diedit')
        self.assertEqual(self.review1.sport_type, 'soccer')

    def test_edit_review_fails_for_other_user(self):
        """Memastikan user lain tidak bisa mengedit review yang bukan miliknya."""
        self.client.login(username='othercustomer', password='testpass123')
        response = self.client.post(
            reverse('reviews:edit_review_ajax', args=[self.review1.pk]),
            data=json.dumps(self.valid_review_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

    # --- DELETE ---
    def test_delete_review_ajax_success(self):
        """Memastikan pemilik review bisa menghapus ulasannya."""
        self.client.login(username='testcustomer', password='testpass123')
        response = self.client.post(reverse('reviews:delete_review_ajax', args=[self.review1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Reviews.objects.count(), 1)
        self.assertFalse(Reviews.objects.filter(pk=self.review1.pk).exists())

    def test_delete_review_fails_for_other_user(self):
        """Memastikan user lain tidak bisa menghapus review yang bukan miliknya."""
        self.client.login(username='othercustomer', password='testpass123')
        response = self.client.post(reverse('reviews:delete_review_ajax', args=[self.review1.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Reviews.objects.count(), 2)

    # 4. Pengujian Detail JSON
    def test_get_review_detail_json(self):
        """Memastikan endpoint detail mengembalikan data yang benar, termasuk sport_type."""
        response = self.client.get(reverse('reviews:get_review_detail_json', args=[self.review1.pk]))
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['data']['pk'], self.review1.pk)
        self.assertEqual(result['data']['sport_type'], 'futsal')