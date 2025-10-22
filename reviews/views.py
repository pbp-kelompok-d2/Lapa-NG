import json
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_GET
from reviews.models import Reviews
from reviews.forms import ReviewForm
from django.shortcuts import get_object_or_404

# @login_required(login_url='/login') 
def show_reviews(request):
    form = ReviewForm()
    context = {
        'form': form
    }
    return render(request, "reviews.html", context)

@require_GET
def get_reviews_json(request):
    try:
        # Ambil semua review, urutkan dari yang terbaru
        reviews = Reviews.objects.all().order_by('-created_at')
        data = []
        for review in reviews:
            data.append({
                "pk": review.pk,
                "user_username": review.user.username,
                "venue_name": review.venue_name,
                "rating": review.rating,
                # Jika image_url kosong, kirim string kosong
                "image_url": review.image_url if review.image_url else "", 
                "created_at": review.created_at.strftime("%d %B %Y")
            })
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

# @login_required(login_url='/login')
@csrf_exempt
@require_http_methods(["POST"])
def add_review_ajax(request):
    try:
        data = json.loads(request.body)
        
        # Buat instance form dengan data dari JSON
        form_data = {
            'venue_name': data.get('venue_name'),
            'rating': data.get('rating'),
            'comment': data.get('comment'),
            'image_url': data.get('image_url') # Ambil image_url
        }
        
        form = ReviewForm(form_data)
        
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user  # Set user yang sedang login
            review.save()
            
            # Kembalikan data review yang baru dibuat
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
            # Jika form tidak valid, kirim error
            return JsonResponse({"status": "error", "errors": form.errors}, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@require_GET
def get_review_detail_json(request, review_id):
    try:
        # Ambil satu review berdasarkan PK (review_id)
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
