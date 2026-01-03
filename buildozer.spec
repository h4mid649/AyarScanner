[app]
title = AyarScanner
package.name = ayarscanner
package.domain = ir.ayar
source.dir = .
source.include_exts = py,txt,json

version = 0.1

requirements = python3,requests
orientation = portrait
fullscreen = 0

android.api = 33
android.minapi = 21
android.archs = arm64-v8a,armeabi-v7a
android.permissions = INTERNET

android.skip_update = True
android.accept_sdk_license = True
android.sdk_build_tools = 33.0.2
p4a.branch = v2024.01.21

[buildozer]
log_level = 2
