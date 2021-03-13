

# VideoPlayer depends on ffpyplayer
requirements = python3, kivy==2.0.0, ffpyplayer

# android.api >= 29 is required for storage.py
android.api = 30

# Add Intent filter
android.manifest.intent_filters = intent_filter.xml

