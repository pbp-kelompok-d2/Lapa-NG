from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from main.models import Venue
from booking.models import Booking
from datetime import date, time, datetime


class BookingTests(TestCase):
    def setUp(self):
        # Setup user dan client login
        self.client = Client()
        self.user = User.objects.create_user(username='tester', password='password123')
        self.client.login(username='tester', password='password123')

        # Setup venue
        self.venue1 = Venue.objects.create(
            name='Badengan Sport Arena',
            address='Jalan Badengan',
            category='futsal',
            price=30000,
            slug='badengan-sport-arena'
        )
        self.venue2 = Venue.objects.create(
            name='Lapangan Biru',
            address='Jalan Merdeka',
            category='basketball',
            price=50000,
            slug='lapangan-biru'
        )

        self.booking_list_url = reverse('booking:booking_list')

    # -------------------------
    #  URL & TEMPLATE TESTS
    # -------------------------
    def test_booking_list_url_exists(self):
        response = self.client.get(self.booking_list_url)
        self.assertEqual(response.status_code, 200)

    def test_booking_list_uses_correct_template(self):
        response = self.client.get(self.booking_list_url)
        self.assertTemplateUsed(response, 'booking_list.html')

    def test_nonexistent_booking_page(self):
        response = self.client.get('/booking/somethingdoesnotexist/')
        self.assertEqual(response.status_code, 404)

    # -------------------------
    #  MODEL LOGIC TESTS
    # -------------------------
    def test_total_price_is_calculated_correctly(self):
        """Pastikan total_price dihitung otomatis berdasarkan durasi"""
        booking = Booking.objects.create(
            user=self.user,
            venue=self.venue1,
            borrower_name='Tester',
            booking_date=date.today(),
            start_time=time(9, 0),
            end_time=time(11, 0)
        )
        self.assertEqual(booking.total_price, 60000)  # 2 jam × 30000

    def test_end_time_before_start_time_does_not_crash(self):
        """Pastikan booking dengan end_time < start_time tidak crash"""
        booking = Booking.objects.create(
            user=self.user,
            venue=self.venue1,
            borrower_name='Tester',
            booking_date=date.today(),
            start_time=time(10, 0),
            end_time=time(9, 0)
        )
        # total_price tidak dihitung karena durasi negatif
        self.assertIsNone(booking.total_price)

    def test_booking_str_representation(self):
        booking = Booking.objects.create(
            user=self.user,
            venue=self.venue1,
            borrower_name='Tester',
            booking_date=date.today(),
            start_time=time(9, 0),
            end_time=time(10, 0)
        )
        expected = f"{self.user.username} - {self.venue1.name} ({booking.booking_date})"
        self.assertEqual(str(booking), expected)

    # -------------------------
    #  BOOKING CREATION TESTS
    # -------------------------
    def test_create_booking_directly(self):
        booking = Booking.objects.create(
            user=self.user,
            venue=self.venue2,
            borrower_name='Abhi',
            booking_date=date.today(),
            start_time=time(8, 0),
            end_time=time(9, 30)
        )
        self.assertEqual(booking.total_price, int(1.5 * self.venue2.price))

    # -------------------------
    #  CLEAR BOOKING TESTS
    # -------------------------
    def test_clear_booking_removes_booking(self):
        booking = Booking.objects.create(
            user=self.user,
            venue=self.venue1,
            borrower_name='Tester',
            booking_date=date.today(),
            start_time=time(9, 0),
            end_time=time(10, 0),
            total_price=30000,
            status='Confirmed'
        )
        clear_url = reverse('booking:clear_booking', args=[booking.id])
        response = self.client.post(clear_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Booking.objects.filter(id=booking.id).exists())

    # -------------------------
    #  UI BEHAVIOR TESTS
    # -------------------------
    def test_empty_booking_page_shows_message(self):
        """Jika belum ada booking, tampilkan pesan kosong"""
        response = self.client.get(self.booking_list_url)
        self.assertContains(response, 'Belum Ada Booking')
        self.assertNotContains(response, 'Total:')

    def test_booking_page_shows_existing_bookings(self):
        Booking.objects.create(
            user=self.user,
            venue=self.venue1,
            borrower_name='Tester',
            booking_date=date.today(),
            start_time=time(9, 0),
            end_time=time(10, 0),
            total_price=30000,
            status='Confirmed'
        )
        response = self.client.get(self.booking_list_url)
        self.assertContains(response, 'Badengan Sport Arena')
        self.assertContains(response, 'Total: Rp 30000')
        self.assertNotContains(response, 'Belum Ada Booking')

    # -------------------------
    #  FILTER FUNCTIONALITY TESTS
    # -------------------------
    def test_filter_by_venue_name(self):
        Booking.objects.create(
            user=self.user,
            venue=self.venue1,
            borrower_name='Tester',
            booking_date=date.today(),
            start_time=time(9, 0),
            end_time=time(10, 0),
            total_price=30000,
            status='Confirmed'
        )
        Booking.objects.create(
            user=self.user,
            venue=self.venue2,
            borrower_name='Tester',
            booking_date=date.today(),
            start_time=time(10, 0),
            end_time=time(11, 0),
            total_price=50000,
            status='Confirmed'
        )

        response = self.client.get(self.booking_list_url, {'venue_name': 'Badengan'})
        self.assertContains(response, 'Badengan Sport Arena')
        self.assertNotContains(response, 'Lapangan Biru')

    def test_filter_by_booker_name(self):
        Booking.objects.create(
            user=self.user,
            venue=self.venue1,
            borrower_name='Tester',
            booking_date=date.today(),
            start_time=time(9, 0),
            end_time=time(10, 0),
            total_price=30000,
            status='Confirmed'
        )
        response = self.client.get(self.booking_list_url, {'booker_name': 'Tester'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Badengan Sport Arena')

    def test_filter_by_sport_type(self):
        Booking.objects.create(
            user=self.user,
            venue=self.venue1,
            borrower_name='Tester',
            booking_date=date.today(),
            start_time=time(9, 0),
            end_time=time(10, 0),
            total_price=30000,
            status='Confirmed'
        )
        Booking.objects.create(
            user=self.user,
            venue=self.venue2,
            borrower_name='Tester',
            booking_date=date.today(),
            start_time=time(10, 0),
            end_time=time(11, 0),
            total_price=50000,
            status='Confirmed'
        )
        response = self.client.get(self.booking_list_url, {'sport_type': 'basketball'})
        self.assertContains(response, 'Lapangan Biru')
        self.assertNotContains(response, 'Badengan Sport Arena')

    # -------------------------
    #  CHECKOUT / FLOW TESTS
    # -------------------------
    def test_checkout_page_redirects_when_empty_cart(self):
        checkout_url = reverse('booking:checkout_page')
        response = self.client.get(checkout_url)
        self.assertTemplateUsed(response, 'empty_cart.html')

    def test_checkout_confirm_clears_cart_and_saves_booking(self):
        session = self.client.session
        session['cart'] = [{
            'id': self.venue1.id,
            'borrower_name': 'Tester',
            'booking_date': str(date.today()),
            'start_time': '09:00:00',
            'end_time': '10:00:00',
            'total_price': 30000
        }]
        session.save()

        checkout_confirm_url = reverse('booking:checkout_confirm')
        response = self.client.post(checkout_confirm_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'checkout_success.html')
        self.assertTrue(Booking.objects.filter(venue=self.venue1).exists())

    # -------------------------
    #  CART & BOOKING EDIT TESTS
    # -------------------------
    def test_add_to_cart_adds_item(self):
        add_url = reverse('booking:add_to_cart', args=[self.venue1.id])
        response = self.client.get(add_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('cart', self.client.session)
        self.assertEqual(len(self.client.session['cart']), 1)

    def test_add_to_cart_duplicate(self):
        add_url = reverse('booking:add_to_cart', args=[self.venue1.id])
        self.client.get(add_url)
        response = self.client.get(add_url)
        self.assertContains(response, 'sudah ada', status_code=200)

    def test_edit_booking_with_valid_data(self):
        """Edit booking di cart dengan data valid"""
        self.client.get(reverse('booking:add_to_cart', args=[self.venue1.id]))
        form_data = {
            'borrower_name': 'Tester',
            'booking_date': str(date.today()),
            'start_time': '08:00',
            'end_time': '09:00'
        }
        response = self.client.post(reverse('booking:edit_booking', args=[self.venue1.id]), data=form_data)
        self.assertJSONEqual(response.content, {'success': True})

    def test_edit_booking_with_invalid_data(self):
        """Edit booking tapi form tidak valid"""
        self.client.get(reverse('booking:add_to_cart', args=[self.venue1.id]))
        response = self.client.post(reverse('booking:edit_booking', args=[self.venue1.id]), data={})
        self.assertIn('success', response.json())
        self.assertFalse(response.json()['success'])

    def test_remove_from_cart_redirects_when_not_empty(self):
        """Hapus salah satu item dari cart"""
        session = self.client.session
        session['cart'] = [{'id': self.venue1.id}]
        session.save()
        remove_url = reverse('booking:remove_from_cart', args=[self.venue1.id])
        response = self.client.get(remove_url)
        self.assertEqual(response.status_code, 302)

    def test_remove_from_cart_shows_empty_cart_when_last_item_removed(self):
        """Jika cart jadi kosong, harus tampil halaman empty_cart"""
        self.client.get(reverse('booking:add_to_cart', args=[self.venue1.id]))
        response = self.client.get(reverse('booking:remove_from_cart', args=[self.venue1.id]))
        # pastikan sekarang cart kosong dan render empty_cart.html
        self.assertTemplateUsed(response, 'empty_cart.html')