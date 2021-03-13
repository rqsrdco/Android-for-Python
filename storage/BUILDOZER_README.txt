
# For testing only, we add 3 files types to include in the .apk
source.include_exts = py,png,jpg,kv,atlas  ,ogg,mp3,txt

# Required to read other app's public storage
# No other STORAGE permissions are required
android.permissions = READ_EXTERNAL_STORAGE

# android.api >= 29 is required for storage.py
android.api = 30
