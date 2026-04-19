[app]
title = 一点天惊点名器
package.name = rollcall
package.domain = org.yidiantianjing
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json
version = 6.0.0.0
requirements = python3,kivy==2.3.1,pillow

[buildozer]
log_level = 2
warn_on_root = 1
build_dir = ./.buildozer
bin_dir = ./bin
build_mode = debug

[app:android]
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.archs = armeabi-v7a, arm64-v8a
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.orientation = portrait
android.fullscreen = 0
android.enable_androidx = True
android.java_version = 17
