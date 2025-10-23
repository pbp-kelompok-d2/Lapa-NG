from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from booking.models import Booking
from booking.forms import BookingForm
from main.models import Venue

@login_required
def booking_by_venue(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id)
    form = BookingForm(request.POST or None)
    
    if request.method == "POST" and form.is_valid():
        booking = form.save(commit=False)
        booking.user = request.user
        booking.venue = venue

        duration_hours = (
            (booking.end_time.hour + booking.end_time.minute / 60)
            - (booking.start_time.hour + booking.start_time.minute / 60)
        )
        booking.total_price = int(duration_hours * (venue.price or 0))

        booking.save()
        return redirect("booking:booking_success")
    
    return render(request, "booking_form.html", {"form": form, "venue": venue})

def venue_list(request):
    venues = Venue.objects.all()
    return render(request, "venue_list.html", {"venues": venues})

def show_venue(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id)
    return render(request, 'venue_detail.html', {'venue': venue})
