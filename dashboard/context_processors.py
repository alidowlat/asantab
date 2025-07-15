from accounts.models import Provider
from accounts.services import calculate_profile_completion


def profile_completion(request):
    provider = Provider.objects.get(user=request.user)

    if provider:
        completion_percent = calculate_profile_completion(provider)
        is_profile_complete = provider.is_profile_complete
    else:
        completion_percent = 0
        is_profile_complete = False

    return {
        'completion_percent': completion_percent,
        'is_profile_complete': is_profile_complete
    }