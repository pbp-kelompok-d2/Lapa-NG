from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
import json
from reviews.models import Reviews

class ReviewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.review_data = {
            'venue_name': 'Lapangan Futsal Merdeka',
            'rating': 5,
            'comment': 'Lapangan sangat bagus dan bersih!'
        }

    def test_create_review_model(self):
        """Test creating a review model instance"""
        review = Reviews.objects.create(
            user=self.user,
            venue_name='Test Venue',
            rating=4,
            comment='Test comment'
        )
        self.assertEqual(review.venue_name, 'Test Venue')
        self.assertEqual(review.rating, 4)
        self.assertEqual(review.user.username, 'testuser')

    def test_show_reviews_page_authenticated(self):
        """Test accessing reviews page when authenticated"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('review:show_reviews'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reviews.html')

    def test_show_reviews_page_unauthenticated(self):
        """Test redirect when accessing reviews page unauthenticated"""
        response = self.client.get(reverse('review:show_reviews'))
        self.assertEqual(response.status_code, 302)  

    def test_get_reviews_json(self):
        """Test JSON endpoint returns reviews"""
        Reviews.objects.create(
            user=self.user,
            venue_name='Test Venue',
            rating=5,
            comment='Great venue!'
        )
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('review:get_reviews_json'))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['venue_name'], 'Test Venue')

    def test_add_review_ajax_success(self):
        """Test adding review via AJAX successfully"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(
            reverse('review:add_review_ajax'),
            data=json.dumps(self.review_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Reviews.objects.count(), 1)
        
        review = Reviews.objects.first()
        self.assertEqual(review.venue_name, 'Lapangan Futsal Merdeka')
        self.assertEqual(review.rating, 5)

    def test_add_review_ajax_invalid_data(self):
        """Test adding review with invalid data"""
        self.client.login(username='testuser', password='testpass123')
        
        invalid_data = {
            'venue_name': '',  
            'rating': 6,       
            'comment': ''
        }
        
        response = self.client.post(
            reverse('review:add_review_ajax'),
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Reviews.objects.count(), 0)

    def test_review_ordering(self):
        """Test that reviews are ordered by creation date (newest first)"""
        for i in range(3):
            Reviews.objects.create(
                user=self.user,
                venue_name=f'Venue {i}',
                rating=4,
                comment=f'Comment {i}'
            )
        
        reviews = Reviews.objects.all()
        self.assertEqual(reviews[0].venue_name, 'Venue 2')
        self.assertEqual(reviews[2].venue_name, 'Venue 0')

    def test_review_string_representation(self):
        """Test the string representation of Review model"""
        review = Reviews.objects.create(
            user=self.user,
            venue_name='Test Venue',
            rating=3,
            comment='Test comment'
        )
        expected_str = f"Test Venue - 3★ by testuser"
        self.assertEqual(str(review), expected_str)