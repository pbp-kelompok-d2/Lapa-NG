from django.shortcuts import render
import csv
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Venue
from .forms import VenueForm
<<<<<<< HEAD

=======
from django.db.models import Q # Import Q for complex lookups
from django.template.loader import render_to_string

PRICE_RANGES = {
    '0-50000': 'Under Rp 50.000',
    '50001-100000': 'Rp 50.001 - Rp 100.000',
    '100001+': 'Over Rp 100.000',
}
>>>>>>> dev

def show_main(request):
    venues = Venue.objects.all() # Get all venues from the DB
    context = {
        'venues': venues, # Pass the venues to the template
    }

    return render(request, "main.html", context)

def venue_detail(request, slug):
    venue = get_object_or_404(Venue, slug=slug) # Find venue by slug or return 404
    context = {
        'venue': venue,
    }
    return render(request, "venue_detail.html", context)

@login_required(login_url='authentication:login') # Redirect to login if not authenticated
def create_venue(request):
    form = VenueForm() # Initialize an empty form

    if request.method == 'POST':
        form = VenueForm(request.POST)
        if form.is_valid():
            venue = form.save(commit=False)  # Don't save to DB yet
            venue.owner = request.user       
            venue.save()                     
            return redirect('main:venue_detail', slug=venue.slug) # Redirect to the new venue's detail page

    context = {'form': form}
    return render(request, 'create_venue.html', context)

@login_required(login_url='authentication:login')
def edit_venue(request, slug):
    venue = get_object_or_404(Venue, slug=slug) # Get the venue to edit

    # Security Check: Only the owner can edit
    if venue.owner != request.user:
        return HttpResponseForbidden("You are not allowed to edit this venue.")

    # Pre-populate the form with the venue's existing data
    form = VenueForm(request.POST or None, instance=venue)

    if request.method == 'POST':
        if form.is_valid():
            form.save() # Save the changes to the existing venue
            return redirect('main:venue_detail', slug=venue.slug) # Redirect to detail page

    context = {'form': form, 'venue': venue}
    return render(request, 'edit_venue.html', context)

@login_required(login_url='authentication:login')
def delete_venue(request, slug):
    venue = get_object_or_404(Venue, slug=slug)

    # Security Check: Only the owner can delete
    if venue.owner != request.user:
        return HttpResponseForbidden("You are not allowed to delete this venue.")

    if request.method == 'POST':
        venue.delete() # Delete the venue from the database
        return redirect('main:show_main') # Redirect to the homepage

    # If GET request, just redirect (or show a confirmation page)
    return redirect('main:venue_detail', slug=venue.slug)


CSV_RELATIVE_PATH = Path("data") / "venues - courts_enriched_data.csv"  

def _parse_hhmm(s: str):
    if not s:
        return None
    s = s.strip()
    # CSV kamu konsisten "H:MM" atau "HH:MM"
    return datetime.strptime(s, "%H:%M").time()

@staff_member_required 
def import_venues_from_csv(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    csv_path = Path(settings.BASE_DIR) / CSV_RELATIVE_PATH
    if not csv_path.exists():
        return JsonResponse({"ok": False, "error": f"CSV not found at {csv_path}"}, status=400)

    created = updated = skipped = errors = 0

    with transaction.atomic():
        try:
            with open(csv_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                expected = ["name","category","address","price","capacity","opening_time","closing_time","time","thumbnail"]
                # cek header minimal
                missing = [h for h in expected if h not in reader.fieldnames]
                if missing:
                    return JsonResponse({"ok": False, "error": f"Missing columns: {missing}"}, status=400)

                for i, row in enumerate(reader, start=2):
                    try:
                        name = row["name"].strip()
                        if not name:
                            skipped += 1
                            continue

                        # lookup kunci duplikasi sederhana
                        address = (row.get("address") or "").strip()
                        lookup = {"name": name}
                        if address:
                            lookup["address"] = address

                        defaults = {
                            "category": (row.get("category") or "").strip(),
                            "price": int(row["price"]) if row.get("price") not in (None, "",) else None,
                            "capacity": int(row["capacity"]) if row.get("capacity") not in (None, "",) else None,
                            "opening_time": _parse_hhmm(row.get("opening_time")),
                            "closing_time": _parse_hhmm(row.get("closing_time")),
                            "time_display": (row.get("time") or "").strip(),
                            "thumbnail": (row.get("thumbnail") or "").strip(),
                        }
                        if address:
                            defaults["address"] = address

                        obj, is_created = Venue.objects.update_or_create(**lookup, defaults=defaults)
                        if is_created:
                            created += 1
                        else:
                            updated += 1

                    except Exception:
                        errors += 1
                        # lanjut baris berikutnya, kita tidak rollback seluruhnya
                        continue

        except Exception as e:
            transaction.set_rollback(True)
            return JsonResponse({"ok": False, "error": str(e)}, status=500)

    return JsonResponse({"ok": True, "stats": {"created": created, "updated": updated, "skipped": skipped, "errors": errors}}, status=200)
