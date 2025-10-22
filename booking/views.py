from django.shortcuts import render, redirect, get_object_or_404
from booking.forms import VenueForm
from booking.models import Venue
from django.http import HttpResponse
from django.core import serializers

def show_booking(request):
    venue_list = Venue.objects.all()

    context = {
        'npm' : '240123456',
        'name': 'Haru Urara',
        'class': 'PBP A',
        'venue_list': venue_list
    }

    return render(request, "booking.html", context)

def create_venue(request):
    form = VenueForm(request.POST or None)

    if form.is_valid() and request.method == "POST":
        form.save()
        return redirect('main:show_venue')

    context = {'form': form}
    return render(request, "create_venue.html", context)

def show_venue(request, id):
    venue = get_object_or_404(Venue, pk=id)
    venue.increment_views()

    context = {
        'venue': venue
    }

    return render(request, "venue_detail.html", context)

def show_xml(request):
    venue_list = Venue.objects.all()
    xml_data = serializers.serialize("xml", venue_list)
    return HttpResponse(xml_data, content_type="application/xml")

def show_json(request):
    venue_list = Venue.objects.all()
    json_data = serializers.serialize("json", venue_list)
    return HttpResponse(json_data, content_type="application/json")

def show_xml_by_id(request, venue_id):
    try:
        venue_item = Venue.objects.filter(pk=venue_id)
        xml_data = serializers.serialize("xml", venue_item)
        return HttpResponse(xml_data, content_type="application/xml")
    except Venue.DoesNotExist:
        return HttpResponse(status=404)

def show_json_by_id(request, venue_id):
    try:
        venue_item = Venue.objects.get(pk=venue_id)
        json_data = serializers.serialize("json", [venue_item])
        return HttpResponse(json_data, content_type="application/json")
    except Venue.DoesNotExist:
        return HttpResponse(status=404)