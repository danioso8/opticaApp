from apps.organizations.models import LandingPageConfig
from django.conf import settings

configs = LandingPageConfig.objects.all()

print(f"📋 MEDIA_ROOT: {settings.MEDIA_ROOT}")
print(f"📋 MEDIA_URL: {settings.MEDIA_URL}")
print(f"📋 DEBUG: {settings.DEBUG}")
print()

for config in configs:
    print(f"🏢 {config.organization.name}")
    if config.logo:
        print(f"   ✅ Logo existe")
        print(f"   📁 Path: {config.logo.name}")
        print(f"   🔗 URL: {config.logo.url}")
    else:
        print(f"   ❌ Sin logo")
    print()
