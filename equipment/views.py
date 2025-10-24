from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Equipment
from .forms import EquipmentForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Equipment

@login_required(login_url='/login')
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

@login_required(login_url='/login')
def equipment_create(request):
    # Cek apakah user adalah ownerl
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
    return render(request, 'edit_equipment.html', {'form': form, 'equipment': equipment})

def delete_equipment(request, id):
    equipment = get_object_or_404(Equipment, pk=id)
    equipment.delete()
    return HttpResponseRedirect(reverse('equipment:equipment_list'))

