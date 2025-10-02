from functools import wraps
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator


def provider_active_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('auth_page')
        provider = getattr(request.user, 'providers', None)
        if not provider or provider.status != 'active':
            return redirect('dashboard_page')
        return view_func(request, *args, **kwargs)

    return _wrapped_view


class ActiveProviderRequiredMixin:
    @method_decorator(provider_active_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


def expert_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not getattr(request.user, "support_agent", False):
            return render(request, "home/404.html", status=404)
        return view_func(request, *args, **kwargs)

    return _wrapped_view


class ExpertRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not getattr(request.user, "support_agent", False):
            return render(request, "home/404.html", status=404)
        return super().dispatch(request, *args, **kwargs)
