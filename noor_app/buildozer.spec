[app]

# (str) Title of your application
title = نور - تطبيق ديني

# (str) Package name
package.name = noor

# (str) Package domain (needed for android/ios packaging)
package.domain = org.noor

# (source.dir) Source code where the main.py live
source.dir = .

# (list) Source includes patterns, let's you fine control which files
source.include_exts = py,png,jpg,kv,atlas,json

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*,images/*.png

# (list) Source excludes patterns, let's you fine control which files
# to not include in the build:
source.exclude_exts = spec

# (list) List of directory to exclude from build:
source.exclude_dirs = tests, bin, .git, .github, doc, assets

# (list) List of exclusions using pattern matching
#source.exclude_patterns = license,images/*/*.png

# (str) Application versioning (method 1)
version = 1.0.0

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,plyer

# (str) Supported orientation (landscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (string) Presplash of the application (image or drawable xml)
# presplash.filename = %(source.dir)s/data/presplash.png

# (list) Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_PHONE_STATE,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION

# (int) Target Android API, should be as high as possible.
android.api = 31

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
#android.ndk = 23b

# (bool) Use --private data storage (True) or --dir public storage (False)
#android.private_storage = True

# (str) Android app theme, default is ok for Kivy-based app
# android.theme = "@android:style/Theme.NoTitleBar"

# (bool) Copy library instead of making a libpymodules.so
#android.copy_libs = 1

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a,armeabi-v7a

# (bool) Enable AndroidX support
android.enable_androidx = True

# (str) Android logcat filters to use
#android.logcat_filters = *:S python:D

# (bool) Copy library instead of making a libpymodules.so
# android.copy_libs = 1

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
# android.archs = arm64-v8a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (str) XML file for custom backup scheme, see the documentation
# android.backup_rules =

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning (+1 per warning, -1 to disable)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab, .ipa) storage
# bin_dir = ./bin
