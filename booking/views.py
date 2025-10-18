from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from .models import Booking
from .forms import BookingForm
import json


def home(request):
    # Halaman utama fitur booking. Data diambil via AJAX.
    return render(request, 'booking/home.html')

@login_required
@require_POST
def api_create(request):
    # Terima JSON atau form-encoded
    if request.content_type == 'application/json':
        try:
            payload = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON.")
        form = BookingForm(payload)
    else:
        form = BookingForm(request.POST)

    if form.is_valid():
        obj = form.save(commit=False)
        obj.user = request.user
        obj.save()
        return JsonResponse({"ok": True, "booking": obj.to_dict()}, status=201)
    return JsonResponse({"ok": False, "errors": form.errors}, status=400)

login_required
@require_POST
def api_create_from_main(request):
    # Dipanggil tombol "Book" di app main
    try:
        p = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON.")

    required = ("venue_name", "date", "start_time", "end_time")
    if any(not p.get(k) for k in required):
        return HttpResponseBadRequest("Missing required fields.")

    form = BookingForm({
        "venue_ref": p.get("venue_ref"),
        "venue_name": p.get("venue_name"),
        "venue_city": p.get("venue_city", ""),
        "sport_type": p.get("sport_type", ""),
        "date": p.get("date"),
        "start_time": p.get("start_time"),
        "end_time": p.get("end_time"),
        "notes": p.get("notes", ""),
    })

    if form.is_valid():
        obj = form.save(commit=False)
        obj.user = request.user
        obj.save()
        return JsonResponse({"ok": True, "booking": obj.to_dict()}, status=201)
    return JsonResponse({"ok": False, "errors": form.errors}, status=400)

@require_GET
def api_list(request):
    # Tambah basic filtering supaya lulus “Filtering (wajib!)”
    qs = Booking.objects.filter(user=request.user)
    q = request.GET.get('q', '').strip()
    sport = request.GET.get('sport', '').strip()
    city = request.GET.get('city', '').strip()
    date = request.GET.get('date', '').strip()

    if q:
        qs = qs.filter(venue_name__icontains=q)
    if sport:
        qs = qs.filter(sport_type__icontains=sport)
    if city:
        qs = qs.filter(venue_city__icontains=city)
    if date:
        qs = qs.filter(date=date)

    data = [b.to_dict() for b in qs]
    return JsonResponse({"bookings": data}, status=200)


@require_GET
def api_search(request):
    # STUB: sampai tim main expose data Venue beneran.
    # Return list kosong saja supaya URLConf tidak error saat import.
    return JsonResponse({"venues": []}, status=200)