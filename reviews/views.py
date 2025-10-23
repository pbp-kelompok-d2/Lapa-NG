import json
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_GET
from reviews.models import Reviews
from reviews.forms import ReviewForm
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from authentication.models import CustomUser

# @login_required(login_url='/login')
def show_reviews(request):
    form = ReviewForm()
    context = {
        'form': form
    }
    return render(request, "reviews.html", context)

# reviews/views.py

@require_GET
def get_reviews_json(request):
    # Dapatkan filter dari query parameter, defaultnya 'all'
    review_filter = request.GET.get('filter', 'all')
    
    reviews_queryset = Reviews.objects.all()

    # Terapkan filter jika user adalah customer dan meminta 'my_reviews'
    if request.user.is_authenticated and review_filter == 'my_reviews':
        try:
            if request.user.customuser.role == 'customer':
                reviews_queryset = reviews_queryset.filter(user=request.user)
        except CustomUser.DoesNotExist:
            # Jika profil tidak ada, kembalikan list kosong untuk 'my_reviews'
            reviews_queryset = Reviews.objects.none()

    reviews = reviews_queryset.order_by('-created_at')
    
    data = []
    for review in reviews:
        # --- PERUBAHAN UTAMA DI SINI ---
        # Tombol edit/hapus hanya muncul jika ID user review sama dengan ID user yang login
        can_modify = request.user.is_authenticated and (review.user == request.user)
        
        data.append({
            "pk": review.pk,
            "user_username": review.user.username,
            "venue_name": review.venue_name,
            "rating": review.rating,
            "image_url": review.image_url if review.image_url else "",
            "created_at": review.created_at.strftime("%d %B %Y"),
            "can_modify": can_modify
        })
    return JsonResponse(data, safe=False)

@login_required(login_url='/login')
@csrf_exempt
@require_http_methods(["POST"])
def add_review_ajax(request):
    # Cek apakah pengguna punya profil dan rolenya adalah customer
    try:
        # Ambil custom profile dari user yang sedang login
        custom_user = request.user.customuser
        if custom_user.role != 'customer':
            return JsonResponse({"status": "error", "message": "Hanya customer yang dapat menambahkan review."}, status=403)
    except CustomUser.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Profil pengguna tidak ditemukan."}, status=404)

    try:
        data = json.loads(request.body)
        form = ReviewForm(data)
        
        if form.is_valid():
            review = form.save(commit=False)
            # --- PERUBAHAN UTAMA DI SINI ---
            # Gunakan user yang sedang login, bukan superuser
            review.user = request.user 
            review.save()
            
            new_review_data = {
                "pk": review.pk,
                "user_username": review.user.username,
                "venue_name": review.venue_name,
                "rating": review.rating,
                "comment": review.comment,
                "image_url": review.image_url if review.image_url else "",
                "created_at": review.created_at.strftime("%d %B %Y")
            }
            return JsonResponse({"status": "success", "data": new_review_data}, status=201)
        else:
            return JsonResponse({"status": "error", "errors": form.errors}, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@require_GET
def get_review_detail_json(request, review_id):
    try:
        review = get_object_or_404(Reviews, pk=review_id)
        data = {
            "pk": review.pk,
            "user_username": review.user.username,
            "venue_name": review.venue_name,
            "rating": review.rating,
            "comment": review.comment,
            "image_url": review.image_url if review.image_url else "",
            "created_at": review.created_at.strftime("%d %B %Y, %H:%M")
        }
        return JsonResponse({"status": "success", "data": data})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
@csrf_exempt
@require_http_methods(["POST"])
def edit_review_ajax(request, review_id):
    try:
        review = get_object_or_404(Reviews, pk=review_id)
        data = json.loads(request.body)
        
        # Inisialisasi form dengan data baru dan instance yang ada
        form = ReviewForm(data, instance=review)
        
        if form.is_valid():
            form.save()
            return JsonResponse({"status": "success", "message": "Ulasan berhasil diperbarui."}, status=200)
        else:
            return JsonResponse({"status": "error", "errors": form.errors}, status=400)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"]) # Menggunakan POST untuk kemudahan dari form JS
def delete_review_ajax(request, review_id):
    try:
        review = get_object_or_404(Reviews, pk=review_id)
        review.delete()
        return JsonResponse({"status": "success", "message": "Ulasan berhasil dihapus."}, status=200)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)