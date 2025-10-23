from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from main.models import Venue

# Dummy data venue
VENUES = [
    {"id": 1, "name": "Lapangan A", "address": "Jl. Merdeka No. 10, Jakarta", "price_per_hour": 100000,
     "image": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c"},
    {"id": 2, "name": "Lapangan B", "address": "Jl. Sudirman No. 45, Bandung", "price_per_hour": 150000,
     "image": "https://images.unsplash.com/photo-1600585154362-01d4e6b1e3e4"},
    {"id": 3, "name": "Lapangan C", "address": "Jl. Diponegoro No. 5, Surabaya", "price_per_hour": 125000,
     "image": "https://images.unsplash.com/photo-1600585154378-894b3b9f4427"},
]


def booking_page(request):
    return render(request, "booking_page.html", {"venues": VENUES})


def add_to_cart(request, venue_id):
    cart = request.session.get("cart", [])
    if venue_id not in cart:
        cart.append(venue_id)
        request.session["cart"] = cart
    return JsonResponse({"message": f"Venue {venue_id} ditambahkan"})


def checkout_page(request):
    cart = request.session.get("cart", [])
    selected_venues = [v for v in VENUES if v["id"] in cart]
    total = sum(v["price_per_hour"] for v in selected_venues)
    return render(request, "checkout_page.html", {"venues": selected_venues, "total": total})

def venue_detail(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id)
    return render(request, 'booking/venue_detail.html', {'venue': venue})

def add_to_cart(request, venue_id):
    # Ambil keranjang dari session
    cart = request.session.get('cart', {})

    # Ambil venue
    venue = Venue.objects.get(id=venue_id)
    
    # Tambahkan ke cart (pakai id sebagai key)
    if str(venue_id) in cart:
        cart[str(venue_id)]['quantity'] += 1
    else:
        cart[str(venue_id)] = {
            'name': venue.name,
            'price': venue.price_per_hour,
            'quantity': 1
        }

    # Simpan kembali ke session
    request.session['cart'] = cart

    # Kirim respons JSON untuk AJAX
    return JsonResponse({'message': f'{venue.name} ditambahkan ke keranjang!', 'cart': cart})


def view_cart(request):
    cart = request.session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    return JsonResponse({'cart': cart, 'total': total})