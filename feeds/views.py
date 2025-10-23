from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.core import serializers
from .models import Post
from .forms import PostForm

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
    
    context = {
        "npm": "2406437451",
        "name": request.user.username,
        "class": "PBP D",
        "post_list": post_list,
        "active_filter": filter_type,
        "active_category": category,
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
    post_list = Post.objects.all()
    json_data = serializers.serialize("json", post_list)
    return HttpResponse(json_data, content_type="application/json")

def show_xml_by_id(request, id):
    try:
       post_item = Post.objects.filter(pk=id)
       xml_data = serializers.serialize("xml", post_item)
       return HttpResponse(xml_data, content_type="application/xml")
    except Post.DoesNotExist:
       return HttpResponse(status=404)
   
def show_json_by_id(request, id):
    try:
       post_item = Post.objects.filter(pk=id)
       json_data = serializers.serialize("json", post_item)
       return HttpResponse(json_data, content_type="application/json")
    except Post.DoesNotExist:
       return HttpResponse(status=404)
   
@login_required(login_url='/auth/login/')
def edit_post(request, id):
    post = get_object_or_404(Post, pk=id)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid() and request.method == 'POST':
        form.save()
        return redirect('feeds:show_post', id=post.id)

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
