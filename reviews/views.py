import json
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from reviews.models import Reviews
from reviews.forms import ReviewForm

# @login_required(login_url='/login')
def show_reviews(request):
    return render(request, "reviews.html")

# @login_required(login_url='/login')
def get_reviews_json(request):
    try:
        reviews = Reviews.objects.all().order_by('-created_at')
        data = []
        for review in reviews:
            data.append({
                "pk": review.pk,
                "user": review.user.username,
                "venue_name": review.venue_name,
                "rating": review.rating,
                "comment": review.comment,
                "created_at": review.created_at.strftime("%d %B %Y, %H:%M")
            })
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
# @login_required(login_url='/login')
@require_http_methods(["POST"])
def add_review_ajax(request):
    try:
        data = json.loads(request.body)
        form = ReviewForm(data)
        
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            
            # Return the created review data
            new_review_data = {
                "pk": review.pk,
                "user": review.user.username,
                "venue_name": review.venue_name,
                "rating": review.rating,
                "comment": review.comment,
                "created_at": review.created_at.strftime("%d %B %Y, %H:%M")
            }
            return JsonResponse(new_review_data, status=201)
        else:
            return JsonResponse({
                "errors": form.errors
            }, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({
            "error": "Invalid JSON data"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "error": str(e)
        }, status=500)