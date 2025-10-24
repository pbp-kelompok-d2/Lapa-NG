from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Equipment
from .forms import EquipmentForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Equipment

@login_required(login_url='/login')
def equipment_list(request):
    equipments = Equipment.objects.all()

    # Filtering berdasarkan region & sport category
    region = request.GET.get('region')
    sport = request.GET.get('sport_category')
    search = request.GET.get('search')

    if region and region != 'all':
        equipments = equipments.filter(region=region)
    if sport and sport != 'all':
        equipments = equipments.filter(sport_category=sport)
    if search:
        equipments = equipments.filter(name__icontains=search)

    # Cek apakah request berasal dari AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = []
        for eq in equipments:
            data.append({
                'id': eq.id,
                'name': eq.name,
                'sport_category': eq.get_sport_category_display(),
                'price_per_hour': str(eq.price_per_hour),
                'region': eq.get_region_display(),
                'quantity': eq.quantity,
                'available': eq.available,
                'thumbnail': eq.thumbnail if eq.thumbnail else '',  
                'is_owner': request.user.is_authenticated and request.user == eq.owner, 
            })
        return JsonResponse({'equipments': data})

    # Kalau bukan AJAX, render halaman biasa
    context = {
        'equipments': equipments,
        'regions': Equipment.JAKARTA_REGION_CHOICES,
        'sports': Equipment.SPORT_CHOICES,
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
            messages.success(request, '🛒 Equipment added successfully!')
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
    messages.warning(request, '🗑 Equipment has been deleted.')
    return HttpResponseRedirect(reverse('equipment:equipment_list'))

