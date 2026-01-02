[app]
title = Ayar Scanner
package.name = ayarscanner
package.domain = ir.ayar

source.dir = .
source.include_exts = py,json

version = 0.1

requirements = python3,requests

orientation = portrait

[buildozer]
log_level = 2

[app:android]
android.permissions = INTERNET
android.minapi = 21
android.api = 33
android.archs = arm64-v8a,armeabi-v7a
