from django.conf import settings
from django.core.cache import cache
from urllib.parse import urlparse
from uuid import uuid4
import requests
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


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

        avatar_url = u.get("profile_pic_url_hd") or u.get("avatar")
        local_avatar = download_instagram_avatar(avatar_url)

        data = {
            "username": u.get("username"),
            "full_name": u.get("full_name"),
            "biography": u.get("biography"),
            "followers": u.get("edge_followed_by", {}).get("count"),
            "following": u.get("edge_follow", {}).get("count"),
            "posts": u.get("edge_owner_to_timeline_media", {}).get("count"),
            "profile_url": u.get("external_url"),
            "avatar": local_avatar,
            "is_verified": u.get("is_verified", False),
        }
        cache.set(cache_key, data, 7200)

        return data
    except Exception:
        return {}


def extract_instagram_data(platform_link: str):
    if not platform_link:
        return {}

    parsed = urlparse(platform_link)
    username = parsed.path.strip("/")

    if not username:
        return {}

    return get_instagram_data(username=username)


def download_instagram_avatar(url):
    print("DOWNLOADING --- URL:", url)
    if not url:
        print("NO URL")
        return None
    r = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
    print("STATUS:", r.status_code)
    name = f"instagram/{uuid4()}.jpg"
    path = default_storage.save(name, ContentFile(r.content))
    print("SAVED:", path)
    return default_storage.url(path)