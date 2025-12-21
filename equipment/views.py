from decimal import Decimal, InvalidOperation
import json
import requests
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404, redirect
from django.core import serializers
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Equipment
from .forms import EquipmentForm

@login_required(login_url='/auth/login')
def equipment_list(request):
    sport = request.GET.get('sport_category')
    region = request.GET.get('region')
    search = request.GET.get('search', '').strip()

    qs = Equipment.objects.all()
    if sport and sport != 'all':
        qs = qs.filter(sport_category=sport)
    if region and region != 'all':
        qs = qs.filter(region=region)
    if search:
        qs = qs.filter(name__icontains=search)

    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    if is_ajax:
        equipments = []
        for eq in qs:
            thumbnail = ''
            try:
                thumbnail = eq.thumbnail.url if eq.thumbnail else ''
            except Exception:
                thumbnail = getattr(eq, 'thumbnail', '') or ''

            owner_name = ''
            owner_number = ''
            if hasattr(eq.owner, 'customuser'):
                owner_name = getattr(eq.owner.customuser, 'name', '') or ''
                owner_number = getattr(eq.owner.customuser, 'formatted_number', '') or ''

            equipments.append({
                'id': eq.id,
                'name': eq.name,
                'thumbnail': thumbnail,
                'sport_category': eq.get_sport_category_display(),
                'region': eq.get_region_display(),
                'price_per_hour': eq.price_per_hour,
                'quantity': eq.quantity,
                'available': eq.available,
                'is_owner': request.user.is_authenticated and eq.owner == request.user,
                'owner_name': owner_name,
                'owner_number': owner_number,
            })

        return JsonResponse({'equipments': equipments})
    context = {
        'equipments': qs, 
        'sports': Equipment.SPORT_CHOICES,
        'regions': Equipment.JAKARTA_REGION_CHOICES,
    }
    return render(request, 'equipment_list.html', context)

@csrf_exempt
@login_required(login_url='/auth/login')
def equipment_create(request):
    if not request.user.customuser.role == 'owner':
        return redirect('equipment:equipment_list')  # kalau bukan owner, redirect ke list

    form = EquipmentForm(request.POST or None)
    if form.is_valid() and request.method == 'POST':
        form = EquipmentForm(request.POST)
        if form.is_valid():
            equipment = form.save(commit=False)
            equipment.owner = request.user
            equipment.save()
            return redirect('equipment:equipment_list')

    return render(request, 'add_equipment.html', {'form': form})

@csrf_exempt
def edit_equipment(request, id):
    equipment = get_object_or_404(Equipment, pk=id)

    if request.method == "POST":
        form = EquipmentForm(request.POST, request.FILES, instance=equipment)
        if form.is_valid():
            form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('equipment:equipment_list')
        else:
            # Form invalid, render form ulang untuk AJAX
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return render(request, 'edit_form.html', {'form': form, 'equipment': equipment})

    else:
        form = EquipmentForm(instance=equipment)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Render form saja untuk modal
        return render(request, 'edit_form.html', {'form': form, 'equipment': equipment})

    # fallback normal page
    return render(request, 'edit_form.html', {'form': form, 'equipment': equipment})

def delete_equipment(request, id):
    equipment = get_object_or_404(Equipment, pk=id)
    equipment.delete()
    return HttpResponseRedirect(reverse('equipment:equipment_list'))

#=====XML & JSON=====
def show_xml(request):
     equipment_list = Equipment.objects.all()
     xml_data = serializers.serialize("xml", equipment_list)
     return HttpResponse(xml_data, content_type="application/xml")

def show_json(request):
    qs = Equipment.objects.all().select_related('owner')
    data = [{
        'id': p.id,
        'name': p.name,
        'price_per_hour': p.price_per_hour,
        'sport_category': p.sport_category,
        'region': p.region,
        'quantity': p.quantity,
        'available': p.available,
        'thumbnail': p.thumbnail,
        'user': {
            'username': p.owner.username,
            'number': getattr(p.owner.customuser, 'formatted_number', ''),
            'name': p.owner.customuser.name,
            'role': p.owner.customuser.role,
            'profile_picture': p.owner.customuser.profile_picture,
        } if hasattr(p.owner, 'customuser') else None
    } for p in qs]
    return JsonResponse(data, safe=False)


def show_xml_by_id(request, id):
    try:
        equipment = Equipment.objects.filter(pk=id)
        xml_data = serializers.serialize("xml", equipment)
        return HttpResponse(xml_data, content_type="application/xml")
    except Equipment.DoesNotExist:
        return HttpResponse(status=404)

def show_json_by_id(request, id):
     try:
        equipment = Equipment.objects.select_related('owner').get(pk=id)
        data = {
        'id': equipment.id,
        'name': equipment.name,
        'price_per_hour': equipment.price_per_hour,
        'sport_category': equipment.sport_category,
        'region': equipment.region,
        'quantity': equipment.quantity,
        'available': equipment.available,
        'thumbnail': equipment.thumbnail,
        'user': {
            'username': equipment.owner.username,
            'number': getattr(equipment.owner.customuser, 'formatted_number', ''),
            'name': equipment.owner.customuser.name,
            'role': equipment.owner.customuser.role,
            'profile_picture': equipment.owner.customuser.profile_picture,
        } if hasattr(equipment.owner, 'customuser') else None
        }
        return JsonResponse(data)
     except Equipment.DoesNotExist:
        return JsonResponse({'detail': 'Not found'}, status=404)
     
def get_equipment(request):
    image_url = request.GET.get('url')
    if not image_url:
        return HttpResponse('No URL provided', status=400)
    
    try:
        # Fetch image from external source
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # Return the image with proper content type
        return HttpResponse(
            response.content,
            content_type=response.headers.get('Content-Type', 'image/jpeg')
        )
    except requests.RequestException as e:
        return HttpResponse(f'Error fetching image: {str(e)}', status=500)    

@csrf_exempt
def create_equipment_flutter(request):
    if request.method == "POST":
        data = json.loads(request.body)
        name = strip_tags(data.get("name", ""))
        price_per_hour = strip_tags(data.get("price_per_hour", 0))
        sport_category = data.get("sport_category", "")
        region = data.get("region", "")
        quantity = strip_tags(data.get("quantity", ""))
        available = data.get("available", False)
        thumbnail = data.get("thumbnail", "")
        owner = request.user

        new_equipment = Equipment(
            name = name,
            price_per_hour = price_per_hour,
            sport_category = sport_category,
            region = region,
            quantity = quantity,
            available = available,
            thumbnail = thumbnail,
            owner = owner
        )
        new_equipment.save()
        return JsonResponse({"status": "success"}, status=200)
    else:
        return JsonResponse({"status": "error"}, status=401)

@csrf_exempt
@login_required
def edit_equipment_flutter(request, id):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "POST required"}, status=400)

    try:
        equipment = Equipment.objects.get(id=id)
    except Equipment.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Equipment not found"}, status=404)

    if equipment.owner != request.user:
        return JsonResponse({"status": "error", "message": "Forbidden"}, status=403)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    # STRING
    if "name" in data and data["name"] is not None:
        equipment.name = strip_tags(str(data["name"]).strip())

    if "sport_category" in data:
        equipment.sport_category = data["sport_category"]

    if "region" in data:
        equipment.region = data["region"]

    if "thumbnail" in data:
        equipment.thumbnail = data["thumbnail"] or ""

    if "price_per_hour" in data:
        try:
            equipment.price_per_hour = Decimal(
                str(data["price_per_hour"]).strip()
            )
        except (InvalidOperation, TypeError):
            return JsonResponse(
                {"status": "error", "message": "Invalid price format"},
                status=400
            )
        
    if "quantity" in data:
        equipment.quantity = int(data["quantity"])

    if "available" in data:
        equipment.available = data["available"]

    equipment.save()
    print("EDIT DATA:", data)
    print("PRICE TYPE:", type(data.get("price_per_hour")))
    return JsonResponse(
        {"status": "success", "message": "Equipment updated"},
        status=200
    )

@csrf_exempt
@login_required
def delete_equipment_flutter(request, id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    equipment = get_object_or_404(Equipment, id=id)

    if equipment.owner != request.user:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    equipment.delete()
    return JsonResponse({"status": "success"})
