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

# -------- Android settings (must be in [app]) --------
android.api = 33
android.minapi = 21
android.ndk_api = 21
android.archs = arm64-v8a,armeabi-v7a
android.permissions = INTERNET

# Force Buildozer to use SYSTEM SDK/NDK (prevent ~/.buildozer downloads)
android.sdk_path = /usr/local/lib/android/sdk
android.ndk_path = /usr/local/lib/android/sdk/ndk/25.2.9519653

# Prevent SDK update + auto accept licenses (for CI)
android.skip_update = True
android.accept_sdk_license = True

# Pin build-tools so it won't try 36.x
android.sdk_build_tools = 33.0.2

# Optional: pin p4a branch (stability)
p4a.branch = v2024.01.21

[buildozer]
log_level = 2
