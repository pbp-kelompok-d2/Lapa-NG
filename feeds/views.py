from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.core import serializers
from .models import Post
from .forms import PostForm
from django.utils.timezone import localtime
from django.views.decorators.http import require_http_methods

@login_required(login_url='/auth/login/')
def show_feed_main(request):
    filter_type = request.GET.get("filter", "all")
    category = request.GET.get("category", "all")
    
    if filter_type == "my":
        post_list = Post.objects.filter(user=request.user)
    else:
        post_list = Post.objects.all()
        
    if category != "all":
        post_list = post_list.filter(category=category)
        
    post_list = post_list.order_by("-created_at")
    
    context = {
        "npm": "2406437451",
        "name": request.user.username,
        "class": "PBP D",
        "post_list": post_list,
        "active_filter": filter_type,
        "active_category": category,
        "active_page": "feeds",
    }
    return render(request, "feed_main.html", context)

@login_required(login_url='/auth/login/')
def create_post(request):
    form = PostForm(request.POST or None)
    if form.is_valid() and request.method == "POST":
        post_entry = form.save(commit=False)
        post_entry.user = request.user
        post_entry.save()
        return redirect("feeds:show_feed_main")
    
    context = {
        'form': form
    }
    return render(request, "create_post.html", context)

@login_required(login_url='/auth/login/')
def show_post(request, id):
    post = get_object_or_404(Post, pk=id)
    post.increment_views()
    
    context = {
        'post': post
    }
    return render(request, "post_detail.html", context)

def show_xml(request):
    post_list = Post.objects.all()
    xml_data = serializers.serialize("xml", post_list)
    return HttpResponse(xml_data, content_type="application/xml")

def show_json(request):
    filter_type = request.GET.get("filter", "all")
    category = request.GET.get("category", "all")

    qs = Post.objects.select_related('user').all()
    if filter_type == "my" and request.user.is_authenticated:
        qs = qs.filter(user=request.user)
    if category != "all":
        qs = qs.filter(category=category)

    qs = qs.order_by("-created_at")

    data = [
        {
            'id': str(p.id),
            'content': p.content,
            'category': p.category,
            'thumbnail': p.thumbnail,
            'post_views': p.post_views,
            'created_at': p.created_at.isoformat() if p.created_at else None,
            'is_featured': p.is_featured,
            'is_hot': p.post_views > 10,
            'user_id': p.user_id,
            'user_username': p.user.username if p.user_id else None,
        }
        for p in qs
    ]
    response = JsonResponse(data, safe=False)
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    return response


def show_xml_by_id(request, id):
    try:
       post_item = Post.objects.filter(pk=id)
       xml_data = serializers.serialize("xml", post_item)
       return HttpResponse(xml_data, content_type="application/xml")
    except Post.DoesNotExist:
       return HttpResponse(status=404)
   
def show_json_by_id(request, id):
    try:
        post = Post.objects.select_related('user').get(pk=id)
        data = {
            'id': str(post.id),
            'content': post.content,
            'category': post.category,
            'thumbnail': post.thumbnail,
            'post_views': post.post_views,
            'created_at': post.created_at.isoformat() if post.created_at else None,
            'is_featured': post.is_featured,
            'is_hot': post.post_views > 10,
            'user_id': post.user_id,
            'user_username': post.user.username if post.user_id else None,
        }
        return JsonResponse(data)
    except Post.DoesNotExist:
        return JsonResponse({'detail': 'Not found'}, status=404)
   
@login_required(login_url='/auth/login/')
def edit_post(request, id):
    post = get_object_or_404(Post, pk=id)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid() and request.method == 'POST':
        form.save()
        return redirect('feeds:show_feed_main')

    context = {
        'form': form,
        'post': post
    }

    return render(request, "edit_post.html", context)

@login_required(login_url='/auth/login/')
def delete_post(request, id):
    post = get_object_or_404(Post, pk=id)
    post.delete()
    return HttpResponseRedirect(reverse('feeds:show_feed_main'))

def post_json_detail(request, id):
    try:
        post = Post.objects.select_related('user').get(pk=id)
        data = {
            "id": str(post.id),
            "username": post.user.username if post.user_id else "Anon",
            "is_owner": request.user.is_authenticated and post.user_id == request.user.id,
            "category": post.category,
            "category_label": post.get_category_display(),
            "content": post.content,
            "thumbnail": post.thumbnail or "",
            "is_featured": post.is_featured,
            "post_views": post.post_views,
            "created_at": localtime(post.created_at).isoformat() if post.created_at else None,
            "is_hot": getattr(post, "is_post_hot", False),
        }
        return JsonResponse(data)
    except Post.DoesNotExist:
        return JsonResponse({'detail': 'Not found'}, status=404)

@login_required(login_url='/auth/login/')
@require_http_methods(["POST"])
def edit_post_ajax(request, id):
    post = get_object_or_404(Post, pk=id)
    
    post.content = request.POST.get("content")
    post.category = request.POST.get("category")
    post.thumbnail = request.POST.get("thumbnail")
    post.is_featured = request.POST.get("is_featured") == 'on'
    post.save()

    return JsonResponse({
        "ok": True,
        "post": {
            "id": str(post.id),
            "content": post.content,
            "category": post.category,
            "category_label": post.get_category_display(),
            "thumbnail": post.thumbnail or "",
            "is_featured": post.is_featured,
        }
    }, status=200)

@login_required(login_url='/auth/login/')
@require_http_methods(["POST"])
def delete_post_ajax(request, id):
    post = get_object_or_404(Post, pk=id)
    if not request.user.is_authenticated:
        return JsonResponse({"ok": False, "detail": "Unauthorized"}, status=401)

    # batasi hanya pemilik yang boleh hapus
    if post.user_id != request.user.id:
        return JsonResponse({"ok": False, "detail": "Forbidden"}, status=403)

    post.delete()
    return JsonResponse({
        "ok": True,
        "redirect": reverse("feeds:show_feed_main"),
    }, status=200)
    
@login_required(login_url='/auth/login/')
@require_http_methods(["POST"])
def create_post_ajax(request):
    content     = request.POST.get("content")
    category    = request.POST.get("category")
    thumbnail   = request.POST.get("thumbnail")
    is_featured = request.POST.get("is_featured") == 'on'

    post = Post.objects.create(
        user=request.user,
        content=content,
        category=category,
        thumbnail=thumbnail,
        is_featured=is_featured,
    )

    return JsonResponse({
        "ok": True,
        "post": {
            "id": str(post.id),
            "content": post.content,
            "category": post.category,
            "thumbnail": post.thumbnail or "",
            "post_views": post.post_views,
            "created_at": localtime(post.created_at).isoformat() if post.created_at else None,
            "is_featured": post.is_featured,
            "is_hot": post.post_views > 10,
            "user_id": post.user_id,
            "user_username": post.user.username if post.user_id else None,
        }
    }, status=201)