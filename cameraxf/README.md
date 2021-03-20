CameraXF
========

*A Kivy Android camera that actually works?*

[Download from the Code Button here](https://github.com/RobertFlatt/Android-for-Python)

CameraXF is a turnkey, full screen, photo, video, data analaysis camera.

- It depends on an [unapproved p4a PR](https://github.com/kivy/python-for-android/pull/2385)

- It depends on Google software, CameraX, that is in part 'release candidate' and in part 'alpha'. This Google software is currently being updated monthly. Google has a [list of supported devices](https://developer.android.com/training/camerax/devices).

Building the QR reader, and hence the whole example, depends gettext. Do this first, if your Linux already has gettext installed then this will be a no-op.

	 sudo apt-get install gettext

The included buildozer.spec automatically imports a custom p4a that implements the unapproved PR. Since it depends on a fork, CameraXF should only be used for testing or prototyping. The *current* buildozer options are documented in [BUILDOZER_README.txt](https://github.com/RobertFlatt/Android-for-Python/blob/main/cameraxf/BUILDOZER_README.txt)

The example has 4 buttons. On the home screen select a Photo Camera, a Video Camera, a Mirror, or a QR code reader. A back gesture or back button returns you to the buttons.

Try pause/resume, rotation, pinch zoom, tap for focus/exposure, the Photo Camera has a button to switch cameras dynamically. If a video is currently being recorded then, a pause, a back gesture/button, or rotating the camera between portrait and landscape (when .spec orientation = all) will cause the recording to stop and be saved. This is the expected behavior.

Images and videos are saved by default to public storage. My file manager app finds them under "Main Storage/DCIM/CameraXF", organized by date and time. A toast shows the file path or MediaStore reference on which an app could operate. On devices running Android 9 or less, the file path is of the form `/somepath/DCIM/AppName/Date/Time.jpg`. On devices running Android 10 or more, the MediaStore reference is of the form `DCIM/AppName/Date/Time.jpg`; where `DCIM/AppName/Date/` is the `RELATIVE_PATH` and `Time.jpg` is the `DISPLAY_NAME`. 

The QR reader displays its results on screen; it should be viewed as a simple example of image analysis and image decorating as it does not implement a 'go to' functionality of a typical QR app. 

The camera is full screen ONLY, messing with the layouts is for fools and experts as the layouts are implemented in Java and Android View classes. Details of the [API](https://github.com/RobertFlatt/Android-for-Python/blob/main/cameraxf/cameraxf/cameraxf.py).

Captain Obvious pointed out that he wants a widget he could embed in a Kivy layout, rather than a full screen widget which is instantiated from a Kivy layout. One step at a time bro.



