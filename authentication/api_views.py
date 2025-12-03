import json
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.views.decorators.csrf import csrf_exempt 

from .forms import CustomUserCreationForm  
from .models import normalize_indonesia_number, CustomUser

@csrf_exempt
def api_login(request):
    # parse JSON or form data
    content_type = request.META.get("CONTENT_TYPE", "")
    if "application/json" in content_type:
        try:
            data = json.loads(request.body.decode("utf-8"))
        except Exception:
            return JsonResponse({"status": False, "message": "Invalid JSON."}, status=400)
    else:
        data = request.POST

    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return JsonResponse({"status": False, "message": "Missing username or password."}, status=400)

    user = authenticate(request, username=username, password=password)
    if user is not None:
        if user.is_active:
            auth_login(request, user)  # creates session cookie

            # try to fetch CustomUser
            try:
                cu = user.customuser
                number = normalize_indonesia_number(cu.number)
                profile_picture = cu.profile_picture
                name = cu.name
                role = cu.role
            except CustomUser.DoesNotExist:
                number = ""
                profile_picture = None
                name = ""
                role = ""

            payload = {
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "name": name,
                "role": role,
                "number": number,
                "profile_picture": profile_picture,
                "status": True,
                "message": "Login successful!"
            }
            return JsonResponse(payload, status=200)
        else:
            return JsonResponse({"status": False, "message": "Account is disabled."}, status=401)
    else:
        return JsonResponse({"status": False, "message": "Invalid credentials."}, status=401)


@csrf_exempt
def api_register(request):
    if request.content_type == "application/json":
        try:
            body_data = json.loads(request.body.decode("utf-8"))
        except Exception:
            return JsonResponse({"status": False, "message": "Invalid JSON."}, status=400)
        data = body_data
    else:
        data = request.POST

    form_data = {
        "username": data.get("username", "").strip(),
        "password1": data.get("password1", ""),
        "password2": data.get("password2", ""),
        "name": data.get("name", "") or data.get("username", "").strip(),
        "role": data.get("role", "owner"),
        "number": data.get("number", ""),
        "profile_picture": data.get("profile_picture", "")  
    }

    form = CustomUserCreationForm(form_data)
    if form.is_valid():
        user = form.save()

        try:
            custom = user.customuser
        except CustomUser.DoesNotExist:
            # fallback
            custom = None

        result = {
            "status": True,
            "message": "User created successfully.",
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "name": custom.name if custom else form_data["name"],
            "role": custom.role if custom else form_data["role"],
            "number": normalize_indonesia_number(custom.number) if custom else normalize_indonesia_number(form_data["number"]),
            "profile_picture": custom.profile_picture if custom else (form_data.get("profile_picture") or None),
        }
        return JsonResponse(result, status=201)
    else:
        errors = form.errors.get_json_data()
        human_errors = {k: [e['message'] for e in v] for k, v in errors.items()}
        return JsonResponse({
            "status": False, 
            "message": "Validation failed.", 
            "errors": human_errors}, 
            status=400)
    
@csrf_exempt
def api_logout(request):
    username = request.user.username
    try:
        auth_logout(request)
        return JsonResponse({
            "username": username,
            "status": True,
            "message": "Logged out successfully!"
        }, status=200)
    except:
        return JsonResponse({
            "status": False,
            "message": "Logout failed."
        }, status=401)
