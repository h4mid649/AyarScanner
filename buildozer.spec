[app]
title = Ayar Scanner
package.name = ayarscanner
package.domain = ir.ayar

source.dir = .
source.include_exts = py,txt,json,png,jpg

version = 0.1

requirements = python3,requests

orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2

[app:android]
android.api = 33
android.minapi = 21
android.ndk_api = 21

# اجبار به استفاده از SDK/NDK سیستم (CI)
android.sdk_path = /usr/local/lib/android/sdk
android.ndk_path = /usr/local/lib/android/sdk/ndk/25.2.9519653

# پین نسخه‌ها برای جلوگیری از 36.x و مشکلات aidl
android.sdk_build_tools = 33.0.2
android.ndk = 25b

# جلوی آپدیت خودکار SDK را بگیر (تا دوباره دنبال Build-Tools جدید نرود)
android.skip_update = True
android.accept_sdk_license = True

android.archs = arm64-v8a,armeabi-v7a
android.permissions = INTERNET

# پین python-for-android به نسخه پایدار
p4a.branch = v2024.01.21
