from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from main.models import Venue
from booking.models import Booking
from booking.forms import BookingForm
from django.contrib import messages
from django.template.loader import render_to_string

@login_required(login_url='/auth/login')
def view_booking_cart(request):
    cart = request.session.get('cart', [])
    venue_ids = [item['id'] for item in cart]
    venues = Venue.objects.filter(id__in=venue_ids)
    context = {'cart': cart, 'venues': venues}
    return render(request, 'booking_cart.html', context)


@login_required(login_url='/auth/login')
def add_to_cart(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id)

    cart = request.session.get('cart', [])
    item = {
        'id': venue.id,
        'name': venue.name,
        'price': float(venue.price),
        'category': venue.category
    }

    if not any(x['id'] == venue.id for x in cart):
        cart.append(item)
        request.session['cart'] = cart
        request.session.modified = True
        message = f"Venue '{venue.name}' berhasil ditambahkan ke booking."
    else:
        message = f"Venue '{venue.name}' sudah ada di booking."

    return JsonResponse({'status': 'ok', 'message': message})


@login_required(login_url='/auth/login')
def view_cart(request):
    cart = request.session.get('cart', [])
    if not cart:
        # kalau kosong langsung tunjukkan halaman empty cart
        return render(request, 'empty_cart.html')

    total = sum(float(item.get('total_price', item['price'])) for item in cart)

    venues = []
    for item in cart:
        try:
            venue = Venue.objects.get(pk=item['id'])
            venues.append(venue)
        except Venue.DoesNotExist:
            continue
        
    context = {'venues': venues, 'total': total, 'cart': cart}
    return render(request, 'booking_cart.html', context)

def booking_page(request):
    cart = request.session.get('cart', [])
    if cart:
        return redirect('booking:checkout_page')
    return render(request, 'empty_cart.html')

@login_required(login_url='/auth/login')
def checkout_page(request):
    cart = request.session.get('cart', [])
    if not cart:
        # kalau cart kosong, render template empty_cart (bukan checkout kosong)
        return render(request, 'empty_cart.html')

    venues = []
    total_price = 0

    for item in cart:
        try:
            venue = Venue.objects.get(pk=item['id'])
        except Venue.DoesNotExist:
            continue

        booking_date = item.get('booking_date')
        start_time = item.get('start_time')
        end_time = item.get('end_time')
        borrower_name = item.get('borrower_name')
        item_total = float(item.get('total_price', venue.price))
        total_price += item_total

        venues.append({
            'id': venue.id,
            'name': venue.name,
            'address': venue.address,
            'price': venue.price,
            'booking_date': booking_date,
            'start_time': start_time,
            'end_time': end_time,
            'borrower_name': borrower_name,
            'total_price': item_total,
        })

    context = {'venues': venues, 'total_price': total_price}
    return render(request, 'checkout_page.html', context)

@login_required(login_url='/auth/login')
def edit_booking(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id)
    cart = request.session.get('cart', [])
    item = next((x for x in cart if x['id'] == venue.id), None)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking_date = form.cleaned_data['booking_date']
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']

            start_dt = datetime.combine(booking_date, start_time)
            end_dt = datetime.combine(booking_date, end_time)
            duration = (end_dt - start_dt).seconds / 3600
            duration = max(duration, 1)  # minimal 1 jam

            if item:
                item['borrower_name'] = form.cleaned_data['borrower_name']
                item['booking_date'] = str(booking_date)
                item['start_time'] = str(start_time)
                item['end_time'] = str(end_time)
                item['total_price'] = float(venue.price) * duration

                request.session['cart'] = cart
                request.session.modified = True

            return JsonResponse({'success': True, 'total_price': item['total_price']})
        return JsonResponse({'success': False, 'errors': form.errors})

    # GET
    form = BookingForm(initial=item or None)
    html_form = render(request, 'edit_booking_form.html', {'form': form, 'venue': venue}).content.decode()
    return JsonResponse({'html_form': html_form})

@login_required(login_url='/auth/login')
def remove_from_cart(request, venue_id):
    cart = request.session.get('cart', [])
    cart = [item for item in cart if item['id'] != venue_id]
    request.session['cart'] = cart
    request.session.modified = True

    # Untuk request via fetch (AJAX) kita kirim redirect ke booking_page agar frontend mengikuti
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if not cart:
            return redirect('booking:booking_page')  # fetch akan melihat redirect dan frontend akan pindah
        return JsonResponse({'success': True, 'empty': False})

    # request biasa (link)
    if not cart:
        return redirect('booking:booking_page')
    return redirect('booking:checkout_page')

@login_required(login_url='/auth/login')
def checkout_confirm(request):
    cart = request.session.get('cart', [])
    if not cart:
        return redirect('booking:checkout_page')

    for item in cart:
        venue = Venue.objects.get(id=item['id'])

        booking_date = (
            datetime.strptime(item['booking_date'], "%Y-%m-%d").date()
            if item.get('booking_date') else None
        )
        start_time = (
            datetime.strptime(item['start_time'], "%H:%M:%S").time()
            if item.get('start_time') else None
        )
        end_time = (
            datetime.strptime(item['end_time'], "%H:%M:%S").time()
            if item.get('end_time') else None
        )

        Booking.objects.create(
            user=request.user,
            venue=venue,
            borrower_name=item.get('borrower_name', ''),
            booking_date=booking_date,
            start_time=start_time,
            end_time=end_time,
            total_price=item.get('total_price', 0),
            status='Confirmed'
        )

    # Kosongkan keranjang
    request.session['cart'] = []
    request.session.modified = True

    return render(request, 'checkout_success.html')

@login_required(login_url='/auth/login')
def booking_list(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    sport_types = [c[0] for c in Venue.CATEGORIES]  # ambil semua jenis sport

    # ambil filter dari GET
    venue_name = request.GET.get('venue_name', '')
    sport_type = request.GET.get('sport_type', '')
    booker_name = request.GET.get('booker_name', '')

    if venue_name:
        bookings = bookings.filter(venue__name__icontains=venue_name)
    if sport_type:
        bookings = bookings.filter(venue__category=sport_type)
    if booker_name:
        bookings = bookings.filter(borrower_name__icontains=booker_name)

    # Kalau AJAX → return partial HTML (tanpa reload seluruh halaman)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('booking_cards.html', {'bookings': bookings})
        return JsonResponse({'html': html})

    # request biasa (GET awal)
    return render(request, 'booking_list.html', {
        'bookings': bookings,
        'sport_types': sport_types,
    })

@login_required(login_url='/auth/login')
def clear_booking(request, booking_id):
    if request.method == "POST":
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        booking.delete()
        return redirect('booking:booking_list')
    return redirect('booking:booking_list')
