[app]
title = Cis Takibi
package.name = cistakibi
package.domain = org.cistakibi
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# Python sürümünü ve p4a sürümlerini kilitliyoruz
requirements = python3==3.10.12,kivy==2.3.0

orientation = portrait
fullscreen = 0

# Android Ayarları
android.archs = arm64-v8a
android.api = 33
android.minapi = 24
android.ndk = 25b
android.accept_sdk_license = True
