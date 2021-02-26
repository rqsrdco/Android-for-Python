CameraXF BETA
=============

*A Kivy Android camera that actually works?*

CameraXF is BETA because:

- It depends on an (unapproved p4a PR)<https://github.com/kivy/python-for-android/pull/2385>

- It depends on Google software that is in part 'release candidate' and in part 'alpha'. This Google software is currently being updated monthly.

- You have not tested CameraXF. Really, we won't know unless you all look for the issues. I want to know if it does not perform as advertised, but I would prefer to hear that it does.

Building the QR reader, and hence the whole example, depends gettext. Do this first, if your Linux already has gettext installed then this will be a no-op.

	 sudo apt-get install gettext

The included buildozer.spec automatically imports a custom p4a that implements the unapproved PR. Since it depends on a fork, CameraXF should only be used for testing or prototyping. The *current* buildozer options are documented in (BUILDOZER_README.txt)<https://github.com/RobertFlatt/android-for-python/cameraxf/BUILDOZER_README.txt>

The example has 4 buttons. Select a Photo Camera, a Video Camera, a Mirror, or a QR code reader on the home screen. A back gesture or back button returns you to the buttons.

Try pause/resume, rotation, pinch zoom, tap for focus/exposure, the Photo Camera has a button to switch cameras dynamically. If a video is currently being recorded then, a pause, a back gesture/button, or rotating the camera between portrait and landscape (when .spec orientation = all) will cause the recording to stop and be saved. This is the expected behavior.

Images and videos are saved by default to public storage. My file manager app finds them under "Main Storage/DCIM/CameraXF BETA", organized by date and time. A toast shows the uri on which an app could operate. If you don't understand what a uri is, wait for some future example in this repository or set private=True (but then your file manager probably won't find the saved file).

The QR reader displays its results on screen; it should be viewed as a simple example of image analysis and image decorating as it does not implement a 'go to' functionality or a typical QR app. 

The camera is full screen ONLY, messing with the layouts is for fools and experts as the layouts are implemented in Java and Android View classes.

Captain Obvious pointed out that he wants a widget he could embed in a Kivy layout, rather than a full screen widget which is instantiated from a Kivy layout. One step at a time bro.



