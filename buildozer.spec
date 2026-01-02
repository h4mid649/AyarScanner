[app]
title = Ayar Scanner
package.name = ayarscanner
package.domain = ir.ayar

source.dir = .
source.include_exts = py,txt,json,png,jpg

version = 0.1

requirements = python3,requests

orientation = portrait

[buildozer]
log_level = 2

[app:android]
android.api = 33
android.minapi = 21
android.archs = arm64-v8a,armeabi-v7a
android.permissions = INTERNET

# پین build-tools تا دنبال 36.x نرود
android.sdk_build_tools = 33.0.2
