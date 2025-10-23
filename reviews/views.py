# import json
# from django.shortcuts import render
# from django.http import JsonResponse
# from django.contrib.auth.decorators import login_required
# from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.http import require_http_methods, require_GET
# from reviews.models import Reviews
# from reviews.forms import ReviewForm
# from django.shortcuts import get_object_or_404
# from django.contrib.auth.models import User # Tambahkan import ini

# # @login_required(login_url='/login')
# def show_reviews(request):
#     form = ReviewForm()
#     context = {
#         'form': form
#     }
#     return render(request, "reviews.html", context)

# @require_GET
# def get_reviews_json(request):
#     try:
#         reviews = Reviews.objects.all().order_by('-created_at')
#         data = []
#         for review in reviews:
#             data.append({
#                 "pk": review.pk,
#                 "user_username": review.user.username,
#                 "venue_name": review.venue_name,
#                 "rating": review.rating,
#                 "image_url": review.image_url if review.image_url else "", 
#                 "created_at": review.created_at.strftime("%d %B %Y")
#             })
#         return JsonResponse(data, safe=False)
#     except Exception as e:
#         return JsonResponse({"status": "error", "message": str(e)}, status=500)

# # @login_required(login_url='/login')
# @csrf_exempt # CSRF akan ditangani oleh AJAX fetch
# @require_http_methods(["POST"])
# def add_review_ajax(request):
#     try:
#         user = User.objects.get(is_superuser=True)
#     except User.DoesNotExist:
#         return JsonResponse({"status": "error", "message": "Admin user tidak ditemukan."}, status=500)

#     try:
#         data = json.loads(request.body)
#         form = ReviewForm(data)
        
#         if form.is_valid():
#             review = form.save(commit=False)
#             review.user = user
#             review.save()
            
#             new_review_data = {
#                 "pk": review.pk,
#                 "user_username": review.user.username,
#                 "venue_name": review.venue_name,
#                 "rating": review.rating,
#                 "comment": review.comment,
#                 "image_url": review.image_url if review.image_url else "",
#                 "created_at": review.created_at.strftime("%d %B %Y")
#             }
#             return JsonResponse({"status": "success", "data": new_review_data}, status=201)
#         else:
#             return JsonResponse({"status": "error", "errors": form.errors}, status=400)
            
#     except json.JSONDecodeError:
#         return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
#     except Exception as e:
#         return JsonResponse({"status": "error", "message": str(e)}, status=500)

# @require_GET
# def get_review_detail_json(request, review_id):
#     try:
#         review = get_object_or_404(Reviews, pk=review_id)
#         data = {
#             "pk": review.pk,
#             "user_username": review.user.username,
#             "venue_name": review.venue_name,
#             "rating": review.rating,
#             "comment": review.comment,
#             "image_url": review.image_url if review.image_url else "",
#             "created_at": review.created_at.strftime("%d %B %Y, %H:%M")
#         }
#         return JsonResponse({"status": "success", "data": data})
#     except Exception as e:
#         return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
# @csrf_exempt
# @require_http_methods(["POST"])
# def edit_review_ajax(request, review_id):
#     try:
#         review = get_object_or_404(Reviews, pk=review_id)
#         data = json.loads(request.body)
        
#         # Inisialisasi form dengan data baru dan instance yang ada
#         form = ReviewForm(data, instance=review)
        
#         if form.is_valid():
#             form.save()
#             return JsonResponse({"status": "success", "message": "Ulasan berhasil diperbarui."}, status=200)
#         else:
#             return JsonResponse({"status": "error", "errors": form.errors}, status=400)
#     except Exception as e:
#         return JsonResponse({"status": "error", "message": str(e)}, status=500)

# # --- FUNGSI BARU UNTUK DELETE ---
# @csrf_exempt
# @require_http_methods(["POST"]) # Menggunakan POST untuk kemudahan dari form JS
# def delete_review_ajax(request, review_id):
#     try:
#         review = get_object_or_404(Reviews, pk=review_id)
#         review.delete()
#         return JsonResponse({"status": "success", "message": "Ulasan berhasil dihapus."}, status=200)
#     except Exception as e:
#         return JsonResponse({"status": "error", "message": str(e)}, status=500)

import json
import traceback # Impor untuk debugging
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_GET
from reviews.models import Reviews
from reviews.forms import ReviewForm

# --- FUNGSI show_reviews dan get_reviews_json (tetap sama) ---
def show_reviews(request):
    form = ReviewForm()
    try:
        user = User.objects.filter(is_superuser=True).first() or User.objects.first()
    except User.DoesNotExist:
        user = None
    user_data = {
        'id': user.id if user else None,
        'is_superuser': user.is_superuser if user else False
    }
    context = { 'form': form, 'user_data': user_data }
    return render(request, "reviews.html", context)

@require_GET
def get_reviews_json(request):
    try:
        current_user = User.objects.filter(is_superuser=True).first() or User.objects.first()
    except User.DoesNotExist:
        current_user = None
    reviews = Reviews.objects.all().order_by('-created_at')
    data = []
    for review in reviews:
        can_modify = bool(current_user and (review.user.id == current_user.id or current_user.is_superuser))
        data.append({
            "pk": review.pk, "user_username": review.user.username, "venue_name": review.venue_name,
            "rating": review.rating, "image_url": review.image_url or "",
            "created_at": review.created_at.strftime("%d %B %Y"), "can_modify": can_modify
        })
    return JsonResponse(data, safe=False)

# --- INI FUNGSI YANG KITA PERBAIKI DENGAN DEBUGGING ---
@csrf_exempt
@require_http_methods(["POST"])
def add_review_ajax(request):
    print("\n--- [DEBUG] FUNGSI add_review_ajax DIPANGGIL ---")

    try:
        user = User.objects.filter(is_superuser=True).first() or User.objects.first()
        if not user:
             print("--- [DEBUG] ERROR: Tidak ada user di database.")
             return JsonResponse({"status": "error", "message": "KRITIS: Tidak ada user di database."}, status=500)
        print(f"--- [DEBUG] Pengguna ditemukan: {user.username}")
    except Exception as e:
        print(f"--- [DEBUG] ERROR saat mencari user: {str(e)}")
        return JsonResponse({"status": "error", "message": f"Error saat mencari user: {str(e)}"}, status=500)

    try:
        data = json.loads(request.body)
        print(f"--- [DEBUG] Data diterima dari frontend: {data}")
        
        form = ReviewForm(data)
        
        if form.is_valid():
            print("--- [DEBUG] Form valid. Mencoba menyimpan...")
            review = form.save(commit=False)
            review.user = user
            review.save()
            print("--- [DEBUG] SUKSES: Review berhasil disimpan!")
            return JsonResponse({"status": "success"}, status=201)
        else:
            # Ini adalah kemungkinan terbesar penyebab masalah Anda
            print(f"--- [DEBUG] FORM TIDAK VALID. Errors: {form.errors.as_json()}")
            return JsonResponse({"status": "error", "errors": form.errors}, status=400)
            
    except Exception as e:
        print(f"--- [DEBUG] TERJADI ERROR TAK TERDUGA: {str(e)}")
        traceback.print_exc() # Mencetak error lengkap ke terminal
        return JsonResponse({"status": "error", "message": f"Terjadi error di server: {str(e)}"}, status=500)

# ... Sisa fungsi (get_review_detail_json, edit, delete) biarkan seperti sebelumnya ...
@require_GET
def get_review_detail_json(request, review_id):
    review = get_object_or_404(Reviews, pk=review_id)
    data = {
        "pk": review.pk, "user_username": review.user.username, "venue_name": review.venue_name,
        "rating": review.rating, "comment": review.comment, "image_url": review.image_url or "",
        "created_at": review.created_at.strftime("%d %B %Y, %H:%M")
    }
    return JsonResponse({"status": "success", "data": data})

@csrf_exempt
@require_http_methods(["POST"])
def edit_review_ajax(request, review_id):
    review = get_object_or_404(Reviews, pk=review_id)
    try:
        data = json.loads(request.body)
        form = ReviewForm(data, instance=review)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse({"status": "error", "errors": form.errors}, status=400)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def delete_review_ajax(request, review_id):
    try:
        review = get_object_or_404(Reviews, pk=review_id)
        review.delete()
        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)