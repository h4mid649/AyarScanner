[app]
title = Ayar Scanner
package.name = ayarscanner
package.domain = ir.ayar

source.dir = .
source.include_exts = py,txt,json,png,jpg

version = 0.1

# بدون kivy
requirements = python3,requests

orientation = portrait

[buildozer]
log_level = 2

[app:android]
# نسخه‌های پایدار
android.api = 33
android.minapi = 21
android.archs = arm64-v8a,armeabi-v7a

# برای دریافت دیتا
android.permissions = INTERNET

# برای اینکه با workflow ما (build-tools 33.0.2) دقیقاً هم‌خوان باشد
android.sdk_build_tools = 33.0.2

# اختیاری ولی پیشنهاد شده
android.enable_androidx = True
android.gradle_dependencies = androidx.core:core-ktx:1.12.0
