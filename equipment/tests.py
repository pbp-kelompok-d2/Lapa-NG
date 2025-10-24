# equipment/tests.py (Revised)

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from equipment.models import Equipment
from authentication.models import CustomUser  # Make sure CustomUser is imported
import json

class EquipmentAppTestCase(TestCase):
    def setUp(self):
        """
        Menyiapkan data awal untuk setiap tes.
        Membuat dua user: satu 'owner' dan satu 'customer'.
        Membuat beberapa item equipment yang dimiliki oleh owner.
        """
        # --- Membuat User ---
        self.owner_user = User.objects.create_user(username='testowner', password='password123')
        self.customer_user = User.objects.create_user(username='testcustomer', password='password123')

        # --- Membuat CustomUser Profile ---
        # Ensure CustomUser model is correctly linked and created
        self.owner_profile = CustomUser.objects.create(user=self.owner_user, name='Owner Name', role='owner', number='111')
        self.customer_profile = CustomUser.objects.create(user=self.customer_user, name='Customer Name', role='customer', number='222')

        # --- Membuat Equipment ---
        self.equipment1 = Equipment.objects.create(
            name='Bola Basket Pro',
            price_per_hour=25000.00, # Use Decimal or float for price
            sport_category='basket',
            region='jakarta_pusat',
            owner=self.owner_user,
            quantity=10,
            available=True,
            thumbnail='http://example.com/basket.jpg'
        )
        self.equipment2 = Equipment.objects.create(
            name='Raket Badminton Pro',
            price_per_hour=15000.00, # Use Decimal or float for price
            sport_category='badminton',
            region='jakarta_selatan',
            owner=self.owner_user,
            quantity=5,
            available=True,
            thumbnail='http://example.com/badminton.jpg'
        )

        self.client = Client()

    # ===============================
    #  TESTS UNTUK MODEL
    # ===============================
    def test_equipment_model_creation(self):
        """Memastikan model Equipment dibuat dengan benar."""
        self.assertEqual(self.equipment1.name, 'Bola Basket Pro')
        self.assertEqual(self.equipment1.owner.username, 'testowner')
        self.assertEqual(float(self.equipment1.price_per_hour), 25000.00) # Compare as float or Decimal

    def test_equipment_string_representation(self):
        """Memastikan representasi string model sudah benar."""
        # Assumes CustomUser has 'name' attribute accessible via owner.customuser.name
        expected_str = f"{self.equipment1.name} ({self.equipment1.sport_category}) - {self.owner_profile.name}"
        self.assertEqual(str(self.equipment1), expected_str)

    # ===============================
    #  TESTS UNTUK VIEWS
    # ===============================
    def test_equipment_list_view_unauthenticated(self):
        """Memastikan user yang belum login di-redirect ke halaman login."""
        response = self.client.get(reverse('equipment:equipment_list'))
        # The login_url in the decorator is '/login'
        expected_redirect_url = '/login/?next=/equipment/equipment/' # Adjusted based on url pattern
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, expected_redirect_url)

    def test_equipment_list_view_as_customer(self):
        """Memastikan user 'customer' bisa melihat daftar equipment."""
        self.client.login(username='testcustomer', password='password123')
        response = self.client.get(reverse('equipment:equipment_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'equipment_list.html')
        self.assertContains(response, 'Bola Basket Pro')
        # Customer tidak boleh melihat tombol "Add Equipment"
        self.assertNotContains(response, '+ Add Equipment')

    def test_equipment_list_view_as_owner(self):
        """Memastikan user 'owner' bisa melihat daftar dan tombol tambah."""
        self.client.login(username='testowner', password='password123')
        response = self.client.get(reverse('equipment:equipment_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bola Basket Pro')
        # Owner harus melihat tombol "Add Equipment"
        self.assertContains(response, '+ Add Equipment')

    # ===============================
    #  TESTS UNTUK FUNGSI CRUD (Create, Read, Update, Delete)
    # ===============================
    def test_add_equipment_view_as_owner(self):
        """Test GET dan POST untuk menambah equipment sebagai owner."""
        self.client.login(username='testowner', password='password123')

        # Test GET request
        response_get = self.client.get(reverse('equipment:add_equipment'))
        self.assertEqual(response_get.status_code, 200)
        self.assertTemplateUsed(response_get, 'add_equipment.html')

        # Test POST request
        initial_count = Equipment.objects.count()
        response_post = self.client.post(reverse('equipment:add_equipment'), {
            'name': 'Shuttlecock Baru',
            'price_per_hour': 10000.00,
            'sport_category': 'badminton',
            'region': 'jakarta_timur',
            'quantity': 20,
            'available': True, # Use Python boolean
            'thumbnail': 'http://example.com/shuttlecock.jpg'
        })
        # Should redirect to the list view upon successful creation
        self.assertEqual(response_post.status_code, 302)
        self.assertRedirects(response_post, reverse('equipment:equipment_list'))
        self.assertEqual(Equipment.objects.count(), initial_count + 1)
        self.assertTrue(Equipment.objects.filter(name='Shuttlecock Baru').exists())

    def test_add_equipment_view_as_customer_is_redirected(self): # Renamed for clarity
        """Memastikan customer di-redirect dari halaman tambah equipment."""
        self.client.login(username='testcustomer', password='password123')
        response = self.client.get(reverse('equipment:add_equipment'))
        # The view explicitly redirects to equipment_list if not owner
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('equipment:equipment_list'))

        # Also test POST attempt
        response_post = self.client.post(reverse('equipment:add_equipment'), {
             'name': 'Attempt by Customer', 'price_per_hour': 5000, # ... other fields
        })
        self.assertEqual(response_post.status_code, 302)
        self.assertRedirects(response_post, reverse('equipment:equipment_list'))


    def test_edit_equipment_view_as_owner(self):
        """Test GET dan POST untuk mengedit equipment sebagai owner."""
        self.client.login(username='testowner', password='password123')
        edit_url = reverse('equipment:edit_equipment', args=[self.equipment1.id])

        # Test GET request (AJAX) - Expects HTML form fragment
        response_get = self.client.get(edit_url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response_get.status_code, 200)
        # Check if it renders the specific partial template used for the modal form
        self.assertTemplateUsed(response_get, 'edit_form.html')
        self.assertContains(response_get, 'Bola Basket Pro') # Check if initial data is there

        # Test POST request (AJAX) - Expects JSON response
        response_post = self.client.post(edit_url, {
            'name': 'Bola Basket Ganti Nama',
            'price_per_hour': 30000.00,
            'sport_category': self.equipment1.sport_category,
            'region': self.equipment1.region,
            'quantity': self.equipment1.quantity,
            'available': self.equipment1.available, # Keep original bool value
            'thumbnail': self.equipment1.thumbnail,
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response_post.status_code, 200)
        try:
            json_response = response_post.json()
            self.assertTrue(json_response.get('success', False))
        except json.JSONDecodeError:
            self.fail("POST request did not return valid JSON.")


        self.equipment1.refresh_from_db()
        self.assertEqual(self.equipment1.name, 'Bola Basket Ganti Nama')
        self.assertEqual(float(self.equipment1.price_per_hour), 30000.00)

    def test_edit_equipment_view_invalid_post_ajax(self):
        """Test invalid POST data during AJAX edit."""
        self.client.login(username='testowner', password='password123')
        edit_url = reverse('equipment:edit_equipment', args=[self.equipment1.id])

        # POST invalid data (e.g., missing name)
        response_post = self.client.post(edit_url, {
            'name': '', # Invalid: Name is required
            'price_per_hour': 30000.00,
            'sport_category': self.equipment1.sport_category,
            'region': self.equipment1.region,
            'quantity': self.equipment1.quantity,
            'available': self.equipment1.available,
            'thumbnail': self.equipment1.thumbnail,
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        # Expecting the form HTML with errors rendered back
        self.assertEqual(response_post.status_code, 200) # Form invalid, returns 200 with re-rendered form
        self.assertTemplateUsed(response_post, 'edit_form.html')
        self.assertContains(response_post, 'This field is required.') # Check for error message

        # Ensure the object wasn't actually changed
        self.equipment1.refresh_from_db()
        self.assertEqual(self.equipment1.name, 'Bola Basket Pro')


    def test_delete_equipment_view_as_owner(self):
        """Test menghapus equipment sebagai owner."""
        self.client.login(username='testowner', password='password123')
        # Create a new item specifically for this test to avoid conflicts
        to_delete = Equipment.objects.create(
            name='To Be Deleted', price_per_hour=100, sport_category='multi',
            region='jakarta_utara', owner=self.owner_user, quantity=1,
            thumbnail='http://delete.me'
        )
        equipment_count_before = Equipment.objects.count()
        delete_url = reverse('equipment:delete_equipment', args=[to_delete.id])

        # The view uses GET for delete, as per its implementation
        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, 302) # Redirects after delete
        self.assertRedirects(response, reverse('equipment:equipment_list'))
        self.assertEqual(Equipment.objects.count(), equipment_count_before - 1)
        self.assertFalse(Equipment.objects.filter(id=to_delete.id).exists())

    # Add tests for non-owners trying to edit/delete (should fail/redirect/403)
    def test_edit_equipment_view_as_customer(self):
         self.client.login(username='testcustomer', password='password123')
         edit_url = reverse('equipment:edit_equipment', args=[self.equipment1.id])
         response_get = self.client.get(edit_url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
         # Non-owners might get redirected or receive a 403, depending on view logic
         # Assuming 403 Forbidden is more appropriate for AJAX, but check your view
         self.assertIn(response_get.status_code, [302, 403])

         response_post = self.client.post(edit_url, {}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
         self.assertIn(response_post.status_code, [302, 403])

    def test_delete_equipment_view_as_customer(self):
         self.client.login(username='testcustomer', password='password123')
         delete_url = reverse('equipment:delete_equipment', args=[self.equipment1.id])
         response = self.client.get(delete_url)
         # Similar to edit, expect redirect or forbidden
         self.assertIn(response.status_code, [302, 403])


    # ===============================
    #  TESTS UNTUK AJAX FILTERING & SEARCH
    # ===============================
    def test_ajax_filter_by_sport(self):
        """Test filter AJAX berdasarkan kategori sport."""
        self.client.login(username='testcustomer', password='password123')
        response = self.client.get(reverse('equipment:equipment_list'),
                                    {'sport_category': 'basket'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('equipments', data)
        self.assertEqual(len(data['equipments']), 1)
        self.assertEqual(data['equipments'][0]['name'], 'Bola Basket Pro')

    def test_ajax_filter_by_region(self):
        """Test filter AJAX berdasarkan wilayah."""
        self.client.login(username='testcustomer', password='password123')
        response = self.client.get(reverse('equipment:equipment_list'),
                                    {'region': 'jakarta_selatan'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('equipments', data)
        self.assertEqual(len(data['equipments']), 1)
        self.assertEqual(data['equipments'][0]['name'], 'Raket Badminton Pro')

    def test_ajax_search_by_name(self):
        """Test search AJAX berdasarkan nama equipment."""
        self.client.login(username='testcustomer', password='password123')
        response = self.client.get(reverse('equipment:equipment_list'),
                                    {'search': 'Raket'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('equipments', data)
        self.assertEqual(len(data['equipments']), 1)
        self.assertEqual(data['equipments'][0]['name'], 'Raket Badminton Pro')

    def test_ajax_no_results(self):
        """Test filter AJAX yang tidak menghasilkan apa-apa."""
        self.client.login(username='testcustomer', password='password123')
        response = self.client.get(reverse('equipment:equipment_list'),
                                    {'search': 'Tidak Akan Ditemukan'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('equipments', data)
        # Correct assertion: check the length of the list
        self.assertEqual(len(data['equipments']), 0)