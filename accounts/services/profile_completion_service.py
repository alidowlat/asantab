PROFILE_WEIGHTS = {
    'iban_number': 15,
    'card_number': 15,
    'national_card_image': 15,
    'national_id': 15,
    'first_name': 5,
    'last_name': 5,
    'username': 5,
    'email': 5,
    'province': 4,
    'city': 4,
    'gender': 4,
    'birth_date': 4,
    'bio': 2,
    'profile_image': 2,
}

def calculate_profile_completion(provider):
    def get_value(field_name):
        if hasattr(provider, field_name):
            return getattr(provider, field_name)
        elif hasattr(provider.user, field_name):
            return getattr(provider.user, field_name)
        return None

    total_weight = sum(PROFILE_WEIGHTS.values())
    score = 0

    for field, weight in PROFILE_WEIGHTS.items():
        value = get_value(field)
        if value:
            score += weight

    percent = int((score / total_weight) * 100)
    provider.is_profile_complete = percent >= 80 and all([
        provider.iban_number,
        provider.card_number,
        provider.national_card_image,
        provider.user.national_id,
    ])
    provider.save(update_fields=['is_profile_complete'])

    return percent
