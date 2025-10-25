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

def show_reviews(request):
    form = ReviewForm()
    context = {
        'form': form,
        'sports': Reviews.SPORT_CHOICES,
    }
    return render(request, "reviews.html", context)

@require_GET
def get_reviews_json(request):
    review_filter = request.GET.get('filter', 'all')
    sport_type_filter = request.GET.get('sport_type', 'all')
    reviews_queryset = Reviews.objects.all()

    if request.user.is_authenticated and review_filter == 'my_reviews':
        try:
            if request.user.customuser.role == 'customer':
                reviews_queryset = reviews_queryset.filter(user=request.user)
        except CustomUser.DoesNotExist:
            reviews_queryset = Reviews.objects.none()

    if sport_type_filter != 'all':
        reviews_queryset = reviews_queryset.filter(sport_type=sport_type_filter)

    reviews = reviews_queryset.order_by('-created_at')
    
    data = []
    for review in reviews:
        can_modify = request.user.is_authenticated and (review.user == request.user)
        
        data.append({
            "pk": review.pk,
            "user_username": review.user.username,
            "venue_name": review.venue_name,
            "sport_type": review.get_sport_type_display(),
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
    try:
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
            "sport_type": review.sport_type,
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
        review = get_object_or_404(Reviews, pk=review_id, user=request.user)
        data = json.loads(request.body)

        form = ReviewForm(data, instance=review)

        if form.is_valid():
            form.save()
            return JsonResponse({"status": "success", "message": "Ulasan berhasil diperbarui."}, status=200)
        else:
            return JsonResponse({"status": "error", "errors": form.errors}, status=400)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=404)

@csrf_exempt
@require_http_methods(["POST"])
def delete_review_ajax(request, review_id):
    try:
        review = get_object_or_404(Reviews, pk=review_id, user=request.user)
        review.delete()
        return JsonResponse({"status": "success", "message": "Ulasan berhasil dihapus."}, status=200)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=404)