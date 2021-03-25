#####################################################################
#
# Add these to buildozer.spec
# A total of 9 (count them) buildozer.spec parameters must be set....
#
# To prevent issues building pyzbar do this first:
# sudo apt-get install gettext
# 
#####################################################################

# pyzbar, libzbar, Pillow are only for the QR Reader in the example 

requirements= python3,kivy==2.0.0, pyzbar, libzbar, Pillow

# use any of these ('all' recomended):

orientation = landscape, portrait, or all

# RECORD_AUDIO required only if capturing video with audio

android.permissions = CAMERA, RECORD_AUDIO

# api 29 or greater

android.api = 30

# add some Java

android.add_src = cameraxf/camerax_src

# there are 5 gradle_dependencies
# Check the current versions of those camera Gradle dependencies here:
# https://developer.android.com/jetpack/androidx/releases/camera#dependencies

android.gradle_dependencies = "androidx.camera:camera-core:1.0.0-rc04",
   "androidx.camera:camera-camera2:1.0.0-rc04",
   "androidx.camera:camera-lifecycle:1.0.0-rc04",
   "androidx.camera:camera-view:1.0.0-alpha23",
   "androidx.lifecycle:lifecycle-process:2.3.0"

# use any one of these (arm64-v8a recomended):

android.arch = armeabi-v7a, arm64-v8a, x86, or x86_64

### These two lines download a custom p4a for use in this demo only
### Until https://github.com/kivy/python-for-android/pull/2385 is approved

p4a.fork = RobertFlatt

p4a.branch = enable_androidx_demo


