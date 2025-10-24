import json
import datetime
import io
from unittest.mock import patch, mock_open

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from authentication.models import CustomUser
from main.models import Venue
from main.forms import VenueForm

# ==================================
#  MODEL TESTS
# ==================================

class TestVenueModel(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testowner', password='password123')
    
    def test_str_representation(self):
        venue = Venue.objects.create(name="LapaNG Keren", owner=self.user)
        self.assertEqual(str(venue), "LapaNG Keren")

    def test_auto_slug_creation(self):
        venue = Venue.objects.create(name="Venue Baru 1", owner=self.user)
        self.assertEqual(venue.slug, "venue-baru-1")

    def test_auto_slug_uniqueness(self):
        # FIX: Provide different addresses to avoid UNIQUE constraint (name, address)
        venue1 = Venue.objects.create(name="Venue Sama", owner=self.user, address="Alamat 1")
        venue2 = Venue.objects.create(name="Venue Sama", owner=self.user, address="Alamat 2")
        self.assertEqual(venue1.slug, "venue-sama")
        self.assertEqual(venue2.slug, "venue-sama-2")

    def test_time_display_generation(self):
        venue = Venue.objects.create(
            name="Venue Pagi-Sore",
            owner=self.user,
            opening_time=datetime.time(9, 0),
            closing_time=datetime.time(17, 30)
        )
        self.assertEqual(venue.time_display, "09:00 - 17:30")

    def test_time_display_not_available(self):
        venue = Venue.objects.create(name="Venue Tanpa Jam", owner=self.user)
        self.assertEqual(venue.time_display, "N/A")

# ==================================
#  FORM TESTS
# ==================================

class TestVenueForm(TestCase):

    def test_valid_form(self):
        data = {
            'name': 'Venue Valid',
            'category': 'soccer',
            'description': 'Deskripsi singkat.',
            'address': 'Jl. Valid No. 1',
            'price': 100000,
            'capacity': 10,
            'opening_time': '09:00',
            'closing_time': '22:00',
            'thumbnail': 'img.jpg',
            'is_featured': True
        }
        form = VenueForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_form_missing_name(self):
        data = {
            'category': 'soccer',
            'price': 100000,
        }
        form = VenueForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_invalid_form_bad_price(self):
        data = {
            'name': 'Venue Harga Aneh',
            'category': 'soccer',
            'price': 'bukan-angka',
        }
        form = VenueForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)

# ==================================
#  VIEW TESTS
# ==================================

class TestMainViews(TestCase):

    def setUp(self):
        self.client = Client()
        
        # 1. Customer User
        self.user_customer = User.objects.create_user(username='customer', password='password123')
        self.profile_customer = CustomUser.objects.create(user=self.user_customer, name='Customer Biasa', role='customer', number='812')
        
        # 2. Owner User
        self.user_owner = User.objects.create_user(username='owner', password='password123')
        self.profile_owner = CustomUser.objects.create(user=self.user_owner, name='Pemilik Lapangan', role='owner', number='813')

        # 3. Another Owner User
        self.user_owner2 = User.objects.create_user(username='owner2', password='password123')
        self.profile_owner2 = CustomUser.objects.create(user=self.user_owner2, name='Pemilik Lain', role='owner', number='814')
        
        # 4. Staff User
        self.user_staff = User.objects.create_user(username='staffuser', password='password123', is_staff=True)

        # 5. Venues
        self.venue_owner = Venue.objects.create(
            name="Lapangan Milik Owner",
            owner=self.user_owner,
            category='soccer',
            price=150000,
            address="Jl. Owner"
        )
        
        self.venue_other = Venue.objects.create(
            name="Lapangan Milik Owner 2",
            owner=self.user_owner2,
            category='basketball',
            price=100000,
            address="Jl. Owner 2"
        )

        self.venue_filter_1 = Venue.objects.create(
            name="Cari Futsal Murah",
            category='futsal',
            price=50000,
            address="Depok"
        )
        
        self.venue_filter_2 = Venue.objects.create(
            name="Cari Tennis Mahal",
            category='tennis',
            price=120000,
            address="Jakarta"
        )

        self.initial_venue_count = Venue.objects.count()

        # Valid data for POST requests
        self.valid_venue_data = {
            'name': 'Venue Baru dari Test',
            'category': 'soccer',
            'description': 'Deskripsi.',
            'address': 'Jl. Test No. 123',
            'price': 100000,
            'capacity': 10,
            'opening_time': '09:00',
            'closing_time': '22:00',
        }
    
    # --- Test show_main and filter_venues (GET) ---

    def test_show_main_get(self):
        response = self.client.get(reverse('main:show_main'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main.html')
        # Should contain all venues
        self.assertContains(response, self.venue_owner.name)
        self.assertContains(response, self.venue_filter_1.name)

    def test_show_main_filter_search(self):
        response = self.client.get(reverse('main:show_main'), {'q': 'Milik Owner'})
        self.assertContains(response, 'Lapangan Milik Owner')
        self.assertNotContains(response, 'Cari Futsal Murah')
        
    def test_show_main_filter_category(self):
        response = self.client.get(reverse('main:show_main'), {'category': 'futsal'})
        self.assertContains(response, 'Cari Futsal Murah')
        self.assertNotContains(response, 'Lapangan Milik Owner')

    def test_show_main_filter_price_low(self):
        response = self.client.get(reverse('main:show_main'), {'price_range': '0-50000'})
        self.assertContains(response, 'Cari Futsal Murah')
        self.assertNotContains(response, 'Cari Tennis Mahal')
        
    def test_show_main_filter_price_mid(self):
        response = self.client.get(reverse('main:show_main'), {'price_range': '50001-100000'})
        self.assertContains(response, 'Lapangan Milik Owner 2')
        self.assertNotContains(response, 'Cari Futsal Murah')

    def test_show_main_filter_price_high(self):
        response = self.client.get(reverse('main:show_main'), {'price_range': '100001+'})
        self.assertContains(response, 'Lapangan Milik Owner')
        self.assertContains(response, 'Cari Tennis Mahal')
        self.assertNotContains(response, 'Cari Futsal Murah')
        
    def test_filter_venues_ajax(self):
        response = self.client.get(
            reverse('main:filter_venues'), 
            {'category': 'tennis'}, 
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, '_venue_list.html')
        self.assertContains(response, 'Cari Tennis Mahal')
        self.assertNotContains(response, 'Cari Futsal Murah')

    # --- Test get_venue_details (AJAX GET) ---
        
    def test_get_venue_details_ajax(self):
        response = self.client.get(
            reverse('main:get_venue_details', kwargs={'slug': self.venue_owner.slug}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, '_venue_modal_content.html')
        self.assertContains(response, self.venue_owner.name)

    def test_get_venue_details_404(self):
        response = self.client.get(
            reverse('main:get_venue_details', kwargs={'slug': 'slug-tidak-ada'}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 404)

    # --- Test Create Views (GET and POST) ---

    def test_get_create_form_not_logged_in(self):
        response = self.client.get(reverse('main:get_create_form'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 302) # Redirects to login
    
    def test_get_create_form_as_customer(self):
        self.client.login(username='customer', password='password123')
        response = self.client.get(reverse('main:get_create_form'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response_get_form = self.client.get(reverse('main:get_create_form'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response_get_form.status_code, 200) # The GET view itself doesn't check role
        self.assertIn('html', response_get_form.json())

    def test_get_create_form_as_owner(self):
        self.client.login(username='owner', password='password123')
        response = self.client.get(reverse('main:get_create_form'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertIn('html', response.json())

    def test_create_venue_ajax_not_logged_in(self):
        response = self.client.post(reverse('main:create_venue_ajax'), self.valid_venue_data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 302) 

    def test_create_venue_ajax_as_customer(self):
        self.client.login(username='customer', password='password123')
        response = self.client.post(reverse('main:create_venue_ajax'), self.valid_venue_data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertIn('Hanya Owner', data['message'])
        self.assertEqual(Venue.objects.count(), self.initial_venue_count)

    def test_create_venue_ajax_as_owner_success(self):
        self.client.login(username='owner', password='password123')
        response = self.client.post(reverse('main:create_venue_ajax'), self.valid_venue_data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        self.assertIn('new_card_html', data)
        self.assertEqual(Venue.objects.count(), self.initial_venue_count + 1)
        self.assertTrue(Venue.objects.filter(name='Venue Baru dari Test').exists())

    def test_create_venue_ajax_as_owner_invalid_data(self):
        self.client.login(username='owner', password='password123')
        invalid_data = self.valid_venue_data.copy()
        del invalid_data['name'] 
        response = self.client.post(reverse('main:create_venue_ajax'), invalid_data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertIn('form_html', data) 
        self.assertContains(response, 'This field is required.', status_code=400) # Error message
        self.assertEqual(Venue.objects.count(), self.initial_venue_count)
        
    def test_create_venue_ajax_wrong_method(self):
        self.client.login(username='owner', password='password123')
        response = self.client.get(reverse('main:create_venue_ajax'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 405) # Method Not Allowed


    # --- Test Edit Views (GET and POST) ---

    def test_get_edit_form_not_logged_in(self):
        response = self.client.get(reverse('main:get_edit_form', kwargs={'slug': self.venue_owner.slug}), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 302)

    def test_get_edit_form_not_owner(self):
        self.client.login(username='customer', password='password123') 
        response = self.client.get(reverse('main:get_edit_form', kwargs={'slug': self.venue_owner.slug}), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 403) 
        
    def test_get_edit_form_wrong_owner(self):
        self.client.login(username='owner', password='password123') 
        response = self.client.get(reverse('main:get_edit_form', kwargs={'slug': self.venue_other.slug}), HTTP_X_REQUESTED_WITH='XMLHttpRequest') # Try to edit owner2's venue
        self.assertEqual(response.status_code, 403) 

    def test_get_edit_form_correct_owner(self):
        self.client.login(username='owner', password='password123') 
        response = self.client.get(reverse('main:get_edit_form', kwargs={'slug': self.venue_owner.slug}), HTTP_X_REQUESTED_WITH='XMLHttpRequest') # Edit own venue
        self.assertEqual(response.status_code, 200)
        self.assertIn('html', response.json())

    def test_edit_venue_ajax_wrong_owner(self):
        self.client.login(username='owner', password='password123') 
        response = self.client.post(
            reverse('main:edit_venue_ajax', kwargs={'slug': self.venue_other.slug}), 
            self.valid_venue_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 403) 
        
    def test_edit_venue_ajax_success(self):
        self.client.login(username='owner', password='password123')
        updated_data = self.valid_venue_data.copy()
        updated_data['name'] = "Nama Sudah Diupdate"
        response = self.client.post(
            reverse('main:edit_venue_ajax', kwargs={'slug': self.venue_owner.slug}), 
            updated_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        self.assertIn('updated_card_html', data)
        self.venue_owner.refresh_from_db()
        self.assertEqual(self.venue_owner.name, "Nama Sudah Diupdate")
        
    def test_edit_venue_ajax_invalid_data(self):
        self.client.login(username='owner', password='password123')
        invalid_data = self.valid_venue_data.copy()
        invalid_data['name'] = "" 
        response = self.client.post(
            reverse('main:edit_venue_ajax', kwargs={'slug': self.venue_owner.slug}), 
            invalid_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertIn('form_html', data)
        self.venue_owner.refresh_from_db()
        self.assertNotEqual(self.venue_owner.name, "") 
        
    def test_edit_venue_ajax_wrong_method(self):
        self.client.login(username='owner', password='password123')
        response = self.client.get(reverse('main:edit_venue_ajax', kwargs={'slug': self.venue_owner.slug}), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 405) 


    # --- Test Delete Views (GET and POST) ---
        
    def test_get_delete_form_wrong_owner(self):
        self.client.login(username='owner', password='password123')
        response = self.client.get(reverse('main:get_delete_form', kwargs={'slug': self.venue_other.slug}), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 403)

    def test_get_delete_form_correct_owner(self):
        self.client.login(username='owner', password='password123')
        response = self.client.get(reverse('main:get_delete_form', kwargs={'slug': self.venue_owner.slug}), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertIn('html', response.json())
        
    def test_delete_venue_ajax_wrong_owner(self):
        self.client.login(username='owner', password='password123')
        response = self.client.post(
            reverse('main:delete_venue_ajax', kwargs={'slug': self.venue_other.slug}), 
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Venue.objects.count(), self.initial_venue_count) 
        
    def test_delete_venue_ajax_success(self):
        # FIX: Correct the password from the previous typo
        self.client.login(username='owner', password='password123') 
        response = self.client.post(
            reverse('main:delete_venue_ajax', kwargs={'slug': self.venue_owner.slug}), 
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        self.assertEqual(data['deleted_slug'], self.venue_owner.slug)
        self.assertEqual(Venue.objects.count(), self.initial_venue_count - 1) 
        self.assertFalse(Venue.objects.filter(slug=self.venue_owner.slug).exists())
        
    def test_delete_venue_ajax_wrong_method(self):
        self.client.login(username='owner', password='password123')
        response = self.client.get(reverse('main:delete_venue_ajax', kwargs={'slug': self.venue_owner.slug}), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 405) 

    # --- Test Misc Views ---

    def test_import_csv_not_staff(self):
        self.client.login(username='owner', password='password123')
        response = self.client.get(reverse('main:import_venues_csv'))
        self.assertEqual(response.status_code, 302) 
    
    @patch('pathlib.Path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data="name,category,address,price,capacity,opening_time,closing_time,time,thumbnail\nTest CSV Venue,soccer,123 CSV St,50000,10,10:00,18:00,10-18,img.jpg\nVenue Duplikat,soccer,Alamat A,1,1,10:00,18:00,,")
    def test_import_csv_as_staff(self, mock_file, mock_exists):
        # Create a venue that will be updated
        Venue.objects.create(name="Venue Duplikat", address="Alamat A")
        count_before = Venue.objects.count()

        self.client.login(username='staffuser', password='password123')
        response = self.client.get(reverse('main:import_venues_csv'))
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['ok'])
        self.assertEqual(data['stats']['created'], 1)
        self.assertEqual(data['stats']['updated'], 1)
        self.assertEqual(data['stats']['skipped'], 0)
        self.assertEqual(Venue.objects.count(), count_before + 1) 
        self.assertTrue(Venue.objects.filter(name='Test CSV Venue').exists())

    @patch('pathlib.Path.exists', return_value=False)
    def test_import_csv_file_not_found(self, mock_exists):
        self.client.login(username='staffuser', password='password123')
        response = self.client.get(reverse('main:import_venues_csv'))
        self.assertEqual(response.status_code, 400)
        self.assertIn('CSV not found', response.json()['error'])

    @patch('pathlib.Path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data="nama,kategori\nVenue,soccer") 
    def test_import_csv_missing_columns(self, mock_file, mock_exists):
        self.client.login(username='staffuser', password='password123')
        response = self.client.get(reverse('main:import_venues_csv'))
        self.assertEqual(response.status_code, 400)
        self.assertIn('Missing columns', response.json()['error'])

    def test_add_to_booking_stub_logged_in(self):
        self.client.login(username='customer', password='password123')
        response = self.client.post(
            reverse('main:stub_add_to_booking', kwargs={'venue_id': self.venue_filter_1.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.json())

    def test_add_to_booking_stub_not_logged_in(self):
        response = self.client.post(
            reverse('main:stub_add_to_booking', kwargs={'venue_id': self.venue_filter_1.id})
        )
        self.assertEqual(response.status_code, 302) 