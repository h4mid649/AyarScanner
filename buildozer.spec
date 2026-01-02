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
android.archs = arm64-v8a,armeabi-v7a
android.permissions = INTERNET

# مهم: Buildozer را مجبور کن از SDK/NDK سیستم استفاده کند (نه دانلود داخلی)
android.sdk_path = /usr/local/lib/android/sdk
android.ndk_path = /usr/local/lib/android/sdk/ndk/25.2.9519653

# مهم: جلوی آپدیت را بگیر تا دوباره دنبال 36.x نرود
android.skip_update = True
android.accept_sdk_license = True

# پین build-tools
android.sdk_build_tools = 33.0.2

# پین NDK (برای سازگاری بهتر)
android.ndk = 25c
