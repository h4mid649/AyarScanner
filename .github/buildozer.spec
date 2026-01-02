[app]
# (str) Title of your application
title = Ayar Scanner

# (str) Package name
package.name = ayarscanner

# (str) Package domain (needed for Android package)
package.domain = ir.ayar

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (these are the extensions which will be included)
source.include_exts = py,json,png,jpg,kv,txt

# (str) Application versioning (method 1)
version = 0.1

# (list) Application requirements
# بدون kivy - ولی برای نوتیفیکیشن plyer + pyjnius لازم است
requirements = python3,requests,plyer,pyjnius

# (str) Supported orientations (landscape, portrait or all)
orientation = portrait

# (bool) Copy the bundles in ~/.buildozer to the application build directory.
# buildozer does not always need this, leave default.
# copy_libs = 1

# (str) Path to a custom icon (optional)
# icon.filename = %(source.dir)s/assets/icon.png

# (str) Path to a custom presplash (optional)
# presplash.filename = %(source.dir)s/assets/presplash.png


[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2


[app:android]
# (int) Target Android API to build for
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (list) Android architectures to build for
android.archs = arm64-v8a,armeabi-v7a

# (list) Permissions
# INTERNET برای گرفتن دیتا از tsetmc
# POST_NOTIFICATIONS برای اندروید 13+
android.permissions = INTERNET,POST_NOTIFICATIONS

# (bool) Enable AndroidX
android.enable_androidx = True

# (str) Gradle dependencies (optional)
# android.gradle_dependencies =

# (str) Use a custom Gradle repository (optional)
# android.gradle_repositories =

# (str) Extra args passed to Gradle (optional)
# android.gradle_extra_args =

# (list) If you want to include extra java files (optional)
# android.add_src =

# (list) Add extra resources (optional)
# android.add_resources =

# (str) Use a custom manifest (optional)
# android.manifest = ./AndroidManifest.xml

# (str) Use custom network security config (optional)
# android.network_security_config = ./network_security_config.xml
