from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
import json
from reviews.models import Reviews
from authentication.models import CustomUser

class ReviewFeatureTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        self.user_customer = User.objects.create_user(username='testcustomer', password='testpass123')
        CustomUser.objects.create(user=self.user_customer, name='Test Customer', role='customer', number='12345')

        self.user_owner = User.objects.create_user(username='testowner', password='testpass123')
        CustomUser.objects.create(user=self.user_owner, name='Test Owner', role='owner', number='67890')

        self.review1 = Reviews.objects.create(
            user=self.user_customer,
            venue_name='Lapangan Futsal Keren',
            sport_type='futsal',
            rating=5,
            comment='Sangat bagus!'
        )

        self.other_user = User.objects.create_user(username='othercustomer', password='testpass123')
        CustomUser.objects.create(user=self.other_user, name='Other Customer', role='customer', number='54321')
        self.review2 = Reviews.objects.create(
            user=self.other_user,
            venue_name='Stadion Basket',
            sport_type='basket',
            rating=4,
            comment='Cukup baik.'
        )
        
        self.valid_review_data = {
            'venue_name': 'Lapangan Badminton Jaya',
            'sport_type': 'badminton',
            'rating': 4,
            'comment': 'Shuttlecock disediakan!'
        }

    # 1. Pengujian Model
    def test_review_model_creation_and_str(self):
        self.assertEqual(self.review1.venue_name, 'Lapangan Futsal Keren')
        self.assertEqual(self.review1.sport_type, 'futsal')
        self.assertEqual(self.review1.rating, 5)
        self.assertEqual(str(self.review1), f"{self.review1.venue_name} - {self.review1.rating}★ by {self.user_customer.username}")

    # 2. Pengujian Views (Halaman dan JSON)
    def test_show_reviews_page_loads_correctly(self):
        response = self.client.get(reverse('reviews:show_reviews'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reviews.html')
        self.assertIn('sports', response.context)

    def test_get_reviews_json_unauthenticated(self):
        response = self.client.get(reverse('reviews:get_reviews_json'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertFalse(data[0]['can_modify'])
        self.assertFalse(data[1]['can_modify'])

    def test_get_reviews_json_as_owner_of_review(self):
        self.client.login(username='testcustomer', password='testpass123')
        response = self.client.get(reverse('reviews:get_reviews_json'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        my_review_data = next((item for item in data if item['user_username'] == 'testcustomer'), None)
        self.assertTrue(my_review_data['can_modify'])

    def test_filter_my_reviews(self):
        self.client.login(username='testcustomer', password='testpass123')
        response = self.client.get(reverse('reviews:get_reviews_json'), {'filter': 'my_reviews'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['user_username'], 'testcustomer')

    def test_filter_by_sport_type(self):
        response = self.client.get(reverse('reviews:get_reviews_json'), {'sport_type': 'basket'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['sport_type'], 'Basket')
        self.assertEqual(data[0]['venue_name'], 'Stadion Basket')

    # 3. Pengujian Fungsionalitas AJAX (Add, Edit, Delete)
    def test_add_review_ajax_success_as_customer(self):
        self.client.login(username='testcustomer', password='testpass123')
        response = self.client.post(
            reverse('reviews:add_review_ajax'),
            data=json.dumps(self.valid_review_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Reviews.objects.count(), 3)

    def test_add_review_fails_if_not_logged_in(self):
        response = self.client.post(reverse('reviews:add_review_ajax'), content_type='application/json')
        self.assertEqual(response.status_code, 302)

    def test_add_review_fails_as_owner(self):
        self.client.login(username='testowner', password='testpass123')
        response = self.client.post(
            reverse('reviews:add_review_ajax'),
            data=json.dumps(self.valid_review_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)

    def test_add_review_fails_with_invalid_data(self):
        self.client.login(username='testcustomer', password='testpass123')
        invalid_data = {'venue_name': '', 'rating': 6, 'comment': ''}
        response = self.client.post(
            reverse('reviews:add_review_ajax'),
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_edit_review_ajax_success(self):
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

    def test_edit_review_fails_for_other_user(self):
        self.client.login(username='othercustomer', password='testpass123')
        response = self.client.post(
            reverse('reviews:edit_review_ajax', args=[self.review1.pk]),
            data=json.dumps(self.valid_review_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_review_ajax_success(self):
        self.client.login(username='testcustomer', password='testpass123')
        response = self.client.post(reverse('reviews:delete_review_ajax', args=[self.review1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Reviews.objects.filter(pk=self.review1.pk).exists())

    def test_delete_review_fails_for_other_user(self):
        self.client.login(username='othercustomer', password='testpass123')
        response = self.client.post(reverse('reviews:delete_review_ajax', args=[self.review1.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Reviews.objects.filter(pk=self.review1.pk).exists())

    # 4. Pengujian Detail JSON
    def test_get_review_detail_json(self):
        response = self.client.get(reverse('reviews:get_review_detail_json', args=[self.review1.pk]))
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result['data']['sport_type'], 'futsal')
        
    # 5. Pengujian Skenario Error
    def test_add_review_fails_with_invalid_json(self):
        """Menguji jika body request bukan JSON yang valid."""
        self.client.login(username='testcustomer', password='testpass123')
        response = self.client.post(
            reverse('reviews:add_review_ajax'),
            data='ini bukan json',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_get_review_detail_not_found(self):
        """Menguji jika ID review pada detail JSON tidak ditemukan."""
        response = self.client.get(reverse('reviews:get_review_detail_json', args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_filter_my_reviews_user_has_no_profile(self):
        """Menguji filter 'my_reviews' jika CustomUser tidak ada (edge case)."""
        user_no_profile = User.objects.create_user(username='noprofile', password='password123')
        self.client.login(username='noprofile', password='password123')
        response = self.client.get(reverse('reviews:get_reviews_json'), {'filter': 'my_reviews'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 0)

    def test_add_review_fails_user_has_no_profile(self):
        """Menguji penambahan review jika CustomUser tidak ada."""
        user_no_profile = User.objects.create_user(username='noprofile', password='password123')
        self.client.login(username='noprofile', password='password123')
        response = self.client.post(
            reverse('reviews:add_review_ajax'),
            data=json.dumps(self.valid_review_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)