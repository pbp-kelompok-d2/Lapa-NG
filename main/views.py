from django.shortcuts import render
from authentication.models import CustomUser
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
from django.db.models import Q # Import Q for complex lookups
from django.template.loader import render_to_string
from django.core.paginator import Paginator

PRICE_RANGES = {
    '0-50000': 'Under Rp 50.000',
    '50001-100000': 'Rp 50.001 - Rp 100.000',
    '100001+': 'Over Rp 100.000',
}

def show_main(request):
    categories = Venue.objects.values_list('category', flat=True).order_by('category').distinct()
    venues = Venue.objects.all()

    search_query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')
    price_range_key = request.GET.get('price_range', '') 

    if search_query:
        venues = venues.filter(
            Q(name__icontains=search_query) | 
            Q(address__icontains=search_query)
        )
    if category_filter:
        venues = venues.filter(category=category_filter)

    min_price = None
    max_price = None
    if price_range_key in PRICE_RANGES:
        if price_range_key == '0-50000':
            max_price = 50000
        elif price_range_key == '50001-100000':
            min_price = 50001
            max_price = 100000
        elif price_range_key == '100001+':
            min_price = 100001

    if min_price is not None:
        venues = venues.filter(price__gte=min_price)
    if max_price is not None:
        venues = venues.filter(price__lte=max_price)

    # ---  PAGINATION LOGIC ---
    paginator = Paginator(venues, 20) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    current_filters_no_page = request.GET.copy()
    if 'page' in current_filters_no_page:
        del current_filters_no_page['page']

    context = {
        'venues': page_obj, 
        'categories': categories,
        'price_ranges': PRICE_RANGES,
        'current_filters': request.GET,
        'current_filters_no_page': current_filters_no_page, # for pagination
    }

    return render(request, "main.html", context)

# View u/ handle AJAX filter 
def filter_venues(request):
    # same logic dengan show_main
    venues = Venue.objects.all()

    search_query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')
    price_range_key = request.GET.get('price_range', '') # Get the selected price range key

    if search_query:
        venues = venues.filter(
            Q(name__icontains=search_query) | 
            Q(address__icontains=search_query)
        )

    if category_filter:
        venues = venues.filter(category=category_filter)

    min_price = None
    max_price = None
    if price_range_key in PRICE_RANGES:
        if price_range_key == '0-50000':
            max_price = 50000
        elif price_range_key == '50001-100000':
            min_price = 50001
            max_price = 100000
        elif price_range_key == '100001+':
            min_price = 100001

    if min_price is not None:
        venues = venues.filter(price__gte=min_price)
    if max_price is not None:
        venues = venues.filter(price__lte=max_price)

    paginator = Paginator(venues, 20) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Hapus parameter 'page' dari current_filters untuk link pagination
    current_filters_no_page = request.GET.copy()
    if 'page' in current_filters_no_page:
        del current_filters_no_page['page']

    context = {
        'venues': page_obj,
        'current_filters_no_page': current_filters_no_page, # Untuk pagination
    }
    
    # --- UBAH RETURN JADI JSON ---
    # Render 2 partial: satu untuk list, satu untuk pagination
    list_html = render_to_string("_venue_list.html", context, request=request)
    pagination_html = render_to_string("_pagination.html", context, request=request)
    
    return JsonResponse({
        'list_html': list_html,
        'pagination_html': pagination_html
    })

def venue_detail(request, slug):
    venue = get_object_or_404(Venue, slug=slug) # Find venue by slug or return 404
    context = {
        'venue': venue,
    }
    return render(request, "venue_detail.html", context)

#=============AJAX STUFF ===============
def get_venue_details(request, slug):
    venue = get_object_or_404(Venue, slug=slug) 
    context = {
        'venue': venue,
    }
    return render(request, '_venue_modal_content.html', context)

@login_required(login_url='authentication:login')
def create_venue_ajax(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

    try:
        if request.user.customuser.role != 'owner':
            return JsonResponse({'status': 'error', 'message': 'Hanya Owner yang dapat menambah venue.'}, status=403)
    except CustomUser.DoesNotExist:
         return JsonResponse({'status': 'error', 'message': 'Profil pengguna tidak ditemukan.'}, status=404)
    
    form = VenueForm(request.POST)
    
    if form.is_valid():
        venue = form.save(commit=False)
        venue.owner = request.user
        venue.save()
        
        new_card_html = render_to_string('_venue_card.html', {'venue': venue})
        
        return JsonResponse({
            'status': 'ok',
            'message': 'Venue created successfully!',
            'new_card_html': new_card_html
        })
    else:
        # Form is invalid, re-render the form HTML with errors
        context = {
            'form': form,
            'modal_title': 'Add Your Venue',
            'button_text': 'Save Venue',
            'form_url': reverse('main:create_venue_ajax')
        }
        form_html = render_to_string('_venue_form.html', context, request=request)
        return JsonResponse({'status': 'error', 'form_html': form_html}, status=400)

@login_required(login_url='authentication:login')
def get_create_form_html(request):
    form = VenueForm()
    context = {
        'form': form,
        'modal_title': 'Add Your Venue',
        'button_text': 'Save Venue',
        'form_url': reverse('main:create_venue_ajax') # Points to the new POST handler
    }
    html = render_to_string('_venue_form.html', context, request=request)
    return JsonResponse({'html': html})

# --- EDIT FORM HTML FOR AJAX ---
@login_required(login_url='authentication:login')
def get_edit_form_html(request, slug):
    venue = get_object_or_404(Venue, slug=slug)

    if venue.owner != request.user:
        return JsonResponse({'status': 'error', 'message': 'Forbidden'}, status=403)

    form = VenueForm(instance=venue) # Pre-fill the form
    context = {
        'form': form,
        'venue': venue, 
        'modal_title': f'Edit "{venue.name}"',
        'button_text': 'Save Changes',
        'form_url': reverse('main:edit_venue_ajax', kwargs={'slug': venue.slug}) 
    }
    html = render_to_string('_venue_form.html', context, request=request)
    return JsonResponse({'html': html})

# --- EDIT VENUE HANDLER FOR AJAX ---
@login_required(login_url='authentication:login')
def edit_venue_ajax(request, slug):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

    venue = get_object_or_404(Venue, slug=slug)

    if venue.owner != request.user:
        return JsonResponse({'status': 'error', 'message': 'Forbidden'}, status=403)

    form = VenueForm(request.POST, instance=venue) 
    
    if form.is_valid():
        updated_venue = form.save() 
        
        updated_card_html = render_to_string('_venue_card.html', {'venue': updated_venue})
        
        return JsonResponse({
            'status': 'ok',
            'message': 'Venue updated successfully!',
            'updated_card_html': updated_card_html,
            'new_slug': updated_venue.slug 
        })
    else:
        context = {
            'form': form,
            'venue': venue,
            'modal_title': f'Edit "{venue.name}"',
            'button_text': 'Save Changes',
            'form_url': reverse('main:edit_venue_ajax', kwargs={'slug': venue.slug})
        }
        form_html = render_to_string('_venue_form.html', context, request=request)
        return JsonResponse({'status': 'error', 'form_html': form_html}, status=400)


# --- DELETE VENUE FOR AJAX ---
@login_required(login_url='authentication:login')
def delete_venue_ajax(request, slug):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

    venue = get_object_or_404(Venue, slug=slug)

    # Security Check: Only the owner can delete
    if venue.owner != request.user:
        return JsonResponse({'status': 'error', 'message': 'Forbidden'}, status=403)

    try:
        venue_name = venue.name # Get name before deleting
        venue.delete()
        return JsonResponse({
            'status': 'ok',
            'message': f'Venue "{venue_name}" deleted successfully!',
            'deleted_slug': slug # Send back slug so JS can remove the card
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'Could not delete venue.'}, status=500)

@login_required(login_url='authentication:login')
def get_delete_form_html(request, slug):
    venue = get_object_or_404(Venue, slug=slug)

    # Security Check
    if venue.owner != request.user:
        return JsonResponse({'status': 'error', 'message': 'Forbidden'}, status=403)

    context = {
        'venue': venue, 
    }
    # Render template konfirmasi yang sudah ada
    html = render_to_string('_venue_delete_confirm.html', context, request=request)
    return JsonResponse({'html': html})

# LOAD CSV IMPORT FUNCTIONALITY
CSV_RELATIVE_PATH = Path("data") / "venues - courts_enriched_data.csv"  

def _parse_hhmm(s: str):
    if not s:
        return None
    s = s.strip()
    return datetime.strptime(s, "%H:%M").time()

@staff_member_required 
def import_venues_from_csv(request):
    if request.method != "GET":
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
                        continue

        except Exception as e:
            transaction.set_rollback(True)
            return JsonResponse({"ok": False, "error": str(e)}, status=500)

    return JsonResponse({"ok": True, "stats": {"created": created, "updated": updated, "skipped": skipped, "errors": errors}}, status=200)


# --- STUB ENDPOINT FOR BOOKING APP ---
@login_required(login_url='authentication:login')
def add_to_booking_draft_stub(request, venue_id):
    # This view is a placeholder for the real Booking app.
    # simulasikan proses penambahan venue ke draft booking

    venue = get_object_or_404(Venue, id=venue_id)
    
    
    print(f"STUB: User {request.user.username} added venue {venue.name} (ID: {venue_id}) to booking draft.")

    return JsonResponse({
        "status": "ok",
        "message": f"Venue '{venue.name}' added to your booking draft!"
    })
