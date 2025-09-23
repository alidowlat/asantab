import requests
from django.conf import settings
from django.core.cache import cache


def get_instagram_data(username: str) -> dict:
    cache_key = f"ig_profile_{username}"
    data = cache.get(cache_key)
    if data:
        return data

    try:
        r = requests.post(
            "https://boxapi.ir/api/instagram/user/get_web_profile_info",
            auth=(settings.BOXAPI_USERNAME, settings.BOXAPI_PASSWORD),
            json={"username": username},
            timeout=10
        )
        if not r.ok:
            return {}

        u = r.json().get("response", {}).get("body", {}).get("data", {}).get("user", {})
        data = {
            "username": u.get("username"),
            "full_name": u.get("full_name"),
            "biography": u.get("biography"),
            "followers": u.get("edge_followed_by", {}).get("count"),
            "following": u.get("edge_follow", {}).get("count"),
            "posts": u.get("edge_owner_to_timeline_media", {}).get("count"),
            "profile_url": u.get("external_url"),
            "avatar": u.get("profile_pic_url_hd"),
            "is_verified": u.get("is_verified", False),
        }

        cache.set(cache_key, data, 7200)

        return data
    except Exception:
        return {}