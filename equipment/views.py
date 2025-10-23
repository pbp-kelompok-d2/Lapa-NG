from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Equipment
from .forms import EquipmentForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Equipment


def equipment_list(request):
    equipments = Equipment.objects.all()

    # Filtering berdasarkan region & sport category
    region = request.GET.get('region')
    sport = request.GET.get('sport_category')

    if region and region != 'all':
        equipments = equipments.filter(region=region)
    if sport and sport != 'all':
        equipments = equipments.filter(sport_category=sport)

    # Cek apakah request berasal dari AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = [
            {
            'name': eq.name,
            'sport_category': eq.get_sport_category_display(),
            'price_per_hour': str(eq.price_per_hour),
            'region': eq.get_region_display(),
            'owner': eq.owner.username,
            'thumbnail': eq.thumbnail,
            'available': eq.available,
            } 
            for eq in equipments
        ]
        return JsonResponse({'equipments': data})

    # Kalau bukan AJAX, render halaman biasa
    context = {
        'equipments': equipments,
        'regions': Equipment.JAKARTA_REGION_CHOICES,
        'sports': Equipment.SPORT_CHOICES,
    }
    return render(request, 'equipment_list.html', context)

def equipment_create(request):
    # Cek apakah user adalah ownerl
    if not request.user.role == 'owner':
        return redirect('equipment:equipment_list')  # kalau bukan owner, redirect ke list

    form = EquipmentForm(request.POST or None)
    if form.is_valid() and request.method == 'POST':
        form = EquipmentForm(request.POST)
        if form.is_valid():
            equipment = form.save(commit=False)
            equipment.owner = request.user
            equipment.save()
            messages.success(request, '🛒 Equipment added successfully!')
            return redirect('equipment:equipment_list')

    return render(request, 'add_equipment.html', {'form': form})