from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse

from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.apps import apps
from django.contrib.auth import login, logout
from django.db import transaction
import traceback, datetime

from .forms import CustomUserCreationForm, ProfileForm
from .models import CustomUser, normalize_indonesia_number

from django.urls import reverse

# Configuration: how many items to return initially and per AJAX page
INITIAL_LIMIT = 12
MAX_LIMIT = 50  # safety cap for AJAX requests

def get_model_safe(label):
    # Return model class for 'app_label.ModelName' or None if not found.
    try:
        return apps.get_model(label)
    except LookupError:
        return None

def discover_user_field(model):
    """
    Try to find the field name on `model` that references the User model.
    Prefer common names first, then inspect FK fields.
    Returns field name string or None if not found.
    """
    common_names = ['user', 'owner', 'customer', 'created_by']
    # quick check for common names
    for name in common_names:
        try:
            f = model._meta.get_field(name)
            # ensure it's a relation (ForeignKey/OneToOne) or accepts user-like objects
            if getattr(f, 'related_model', None):
                return name
        except Exception:
            continue

    # fallback: inspect all fields for a relation to AUTH_USER_MODEL or auth.User
    auth_label = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')
    for f in model._meta.get_fields():
        # We are interested in ForeignKey / OneToOne fields
        related = getattr(f, 'related_model', None)
        if related:
            # Compare by app_label.ModelName or by class equality
            rel_label = f'{related._meta.app_label}.{related._meta.object_name}'
            if rel_label == auth_label or related.__name__.lower() == 'user':
                return f.name
    return None

def choose_ordering(model):
    """Pick a reasonable ordering field name (descending) for model queryset."""
    preferred = ['created_at', 'created', 'date', 'start_time', 'time', 'pk']
    for name in preferred:
        try:
            model._meta.get_field(name)
            # use descending order
            if name == 'pk':
                return '-pk'
            return f'-{name}'
        except Exception:
            continue
    # fallback
    return '-pk'

def serialize_obj_minimal(obj):
    """
    Create a small dictionary from an object with safe attribute lookups.
    This is intentionally generic — frontend should rely on expected keys but
    this keeps the view resilient to unknown models.
    """
    d = {}
    # common fields we might want
    for key in ('id', 'pk', 'name', 'title', 'court', 'location', 'date', 'booking_date', 'venue', 'start_time', 'end_time', 'total_price', 'created_at'):
        try:
            val = getattr(obj, key)
            # if attr is a related object, try to get a friendly representation
            if hasattr(val, 'strftime'):  # date/time
                d[key] = val.isoformat()
            elif hasattr(val, '__str__') and not isinstance(val, (str, int, float, bool)):
                # often related objects — cast to str
                d[key] = str(val)
            else:
                d[key] = val
        except Exception:
            continue

    # ensure id present
    if 'id' not in d:
        try:
            d['id'] = int(getattr(obj, 'pk'))
        except Exception:
            d['id'] = None
    try:
        img = None
        # common image field names to try
        if hasattr(obj, 'thumbnail'):
            fld = getattr(obj, 'thumbnail')
            if fld:
                # try FieldFile url or str fallback
                try:
                    img = fld.url
                except Exception:
                    img = str(fld)
                if img:
                    d['venue_image'] = img
    except Exception:
        pass

    # If this object has a related venue, try to include friendly venue fields
    try:
        if hasattr(obj, 'venue') and getattr(obj, 'venue') is not None:
            v = getattr(obj, 'venue')
            try:
                d['name'] = getattr(v, 'name')
            except Exception:
                pass
            # try common image attributes on the related venue
            try:
                if hasattr(obj, 'thumbnail'):
                    fld = getattr(obj, 'thumbnail')
                    if fld:
                        # try FieldFile url or str fallback
                        try:
                            img = fld.url
                        except Exception:
                            img = str(fld)
                        if img:
                            d['venue_image'] = img
            except Exception:
                pass
    except Exception:
        pass

    return d

@login_required(login_url='/auth/login')
def show_dashboard(request):
    user = request.user
    if (user.is_superuser):
        return redirect('authentication:admin_dashboard')

    profile = get_object_or_404(CustomUser, user=user)

    Booking = get_model_safe('booking.Booking')
    Equipment = get_model_safe('equipment.Equipment')

    counts = {'bookings': 0, 'equipment': 0, 'reviews': 0}
    recent = {'bookings': []}

    # --- BOOKINGS ---
    if Booking is not None:
        try:
            user_field = discover_user_field(Booking) or 'user'
            ordering = choose_ordering(Booking)
            qs = Booking.objects.filter(**{user_field: user}).order_by(ordering)
            counts['bookings'] = qs.count()
            recent['bookings'] = list(qs[:INITIAL_LIMIT])
        except Exception:
            counts['bookings'] = 0
            recent['bookings'] = []

    # --- EQUIPMENT (count only) ---
    Equipment = get_model_safe('equipment.Equipment')
    if Equipment is not None:
        try:
            user_field = discover_user_field(Equipment) or 'user'
            qs = Equipment.objects.filter(**{user_field: user})
            counts['equipment'] = qs.count()
        except Exception:
            counts['equipment'] = 0

    # --- REVIEWS (count only) ---
    Review = get_model_safe('review.Review') or get_model_safe('reviews.Review')
    if Review is not None:
        try:
            user_field = discover_user_field(Review) or 'user'
            qs = Review.objects.filter(**{user_field: user})
            counts['reviews'] = qs.count()
        except Exception:
            counts['reviews'] = 0

    # If this is an AJAX request, support incremental loading:
    # ?type=bookings&offset=12&limit=12  OR ?type=my_courts&offset=0&limit=12
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        typ = request.GET.get('type', 'bookings')
        try:
            offset = int(request.GET.get('offset', 0))
        except ValueError:
            offset = 0
        try:
            limit = int(request.GET.get('limit', INITIAL_LIMIT))
        except ValueError:
            limit = INITIAL_LIMIT
        limit = min(limit, MAX_LIMIT)

        if typ == 'bookings' and Booking is not None:
            # re-use detection logic
            user_field = discover_user_field(Booking) or 'user'
            ordering = choose_ordering(Booking)
            qs = Booking.objects.filter(**{user_field: user}).order_by(ordering)
            items = qs[offset: offset + limit]
            data = [serialize_obj_minimal(o) for o in items]
            total = qs.count()
            has_more = (offset + len(items)) < total
            return JsonResponse({'success': True, 'items': data, 'total': total, 'has_more': has_more})

        elif typ == 'my_courts':
            # Try to find the Venue/Court model in common locations
            Venue = get_model_safe('main.Venue') or get_model_safe('venue.Venue') or get_model_safe('venues.Venue') or get_model_safe('court.Venue') or get_model_safe('main.Court')
            if Venue is None:
                return JsonResponse({'success': False, 'error': 'Venue model not found.'}, status=400)
            try:
                owner_field = discover_user_field(Venue) or 'owner' or 'user'
                ordering = choose_ordering(Venue)
                qs = Venue.objects.filter(**{owner_field: user}).order_by(ordering)
                total = qs.count()
                items = qs[offset: offset + limit]
                data = [serialize_obj_minimal(o) for o in items]
                has_more = (offset + len(items)) < total
                return JsonResponse({'success': True, 'items': data, 'total': total, 'has_more': has_more})
            except Exception:
                traceback.print_exc()
                return JsonResponse({'success': False, 'error': 'Failed to fetch venues.'}, status=500)

        else:
            return JsonResponse({'success': False, 'error': 'Unknown type or model missing.'}, status=400)

    context = {
        'profile': profile,
        'user': user,
        'counts': counts,
        'recent': recent,            # contains model instances lists (bookings/equipment/reviews)
        'bookings_limit': INITIAL_LIMIT,
        'equipment_limit': INITIAL_LIMIT,
        # convenience flag
        'is_owner': getattr(profile, 'role', '') == 'owner',
    }
    return render(request, 'user_dashboard.html', context)

@login_required(login_url='/auth/login')
def admin_dashboard(request):
    context = {
        "admin_index_url": "/admin/",
        "admin_user_url": "/admin/auth/user/",
        "admin_venue_url": "/admin/main/venue/",
        "admin_booking_url": "/admin/booking/booking/",
        "admin_equipment_url": "/admin/equipment/equipment"
    }
    return render(request, "admin_dashboard.html", context)

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account has been successfully created!")
            return redirect('authentication:login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})


def login_user(request):
   if request.method == 'POST':
      form = AuthenticationForm(data=request.POST)

      if form.is_valid():
            user = form.get_user()
            login(request, user)
            response = HttpResponseRedirect(reverse("main:show_main"))
            response.set_cookie('last_login', str(datetime.datetime.now()))
            return response

   else:
      form = AuthenticationForm(request)

   context = {'form': form}
   return render(request, 'login.html', context)

def logout_user(request):
    logout(request)
    response = HttpResponseRedirect(reverse('authentication:login'))
    response.delete_cookie('last_login')
    return redirect('authentication:login')

@login_required(login_url='/auth/login')
def edit_profile(request):
    # Only accept AJAX POST
    if request.method != 'POST' or request.headers.get('x-requested-with') != 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)

    try:
        custom = request.user.customuser
    except CustomUser.DoesNotExist:
        custom = CustomUser(user=request.user)

    # Keep a copy of the current role so we can re-enforce it
    current_role = custom.role

    form = ProfileForm(request.POST, instance=custom)

    if not form.is_valid():
        errors = {k: [str(e) for e in v] for k, v in form.errors.items()}
        return JsonResponse({'success': False, 'errors': errors}, status=400)

    # Normalize phone and enforce the role to be unchanged
    number_raw = form.cleaned_data.get('number', '')
    form.instance.number = normalize_indonesia_number(number_raw)
    form.instance.role = current_role  # enforce no role change from client

    form.save()

    payload = {
        'success': True,
        'username': request.user.username,
        'name': form.instance.name,
        'role': form.instance.role,
        'number': form.instance.number,
        'profile_picture': form.instance.profile_picture or '',
        'message': 'Profile updated successfully.'
    }
    return JsonResponse(payload)

@login_required(login_url='/auth/login')
def delete_profile(request):
    if request.method != "POST" or request.headers.get('x-requested-with') != 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)

    try:
        user = request.user
        # perform atomic delete (delete custom profile then user)
        with transaction.atomic():
            try:
                # delete custom user row if exists
                custom = user.customuser
                custom.delete()
            except CustomUser.DoesNotExist:
                pass

            # log the user out (clears session)
            logout(request)

            # delete the auth user record
            user.delete()

        # Prepare response: include redirect to main page and set a cookie
        redirect_url = reverse('main:show_main') 

        resp = JsonResponse({'success': True, 'redirect': redirect_url})
        # set a short-lived cookie for the toast message (path / so main can read it)
        # keep it for 10 seconds
        resp.set_cookie('toast_message', 'Profile deleted!', max_age=15, path='/', samesite='Lax')
        resp.set_cookie('toast_type', 'danger', max_age=15, path='/', samesite='Lax')

        return resp

    except Exception as e:
        # For debugging, return the error and log traceback (remove detailed error in production)
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)