from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from .models import UserProfile


def role_required(*roles):
    """Restrict a view to users with one of the given roles."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            try:
                profile = request.user.profile
            except UserProfile.DoesNotExist:
                messages.error(request, "User profile not found. Contact an administrator.")
                return redirect('login')
            if profile.role not in roles and UserProfile.Role.ADMIN not in [profile.role]:
                messages.error(request, "You do not have permission to access this page.")
                return redirect(profile.dashboard_url())
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def government_required(view_func):
    """Restrict a view to government officials only."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            return redirect('login')
        if not profile.is_government_official() and profile.role != UserProfile.Role.ADMIN:
            messages.error(request, "Access restricted to government officials.")
            return redirect(profile.dashboard_url())
        return view_func(request, *args, **kwargs)
    return wrapper
