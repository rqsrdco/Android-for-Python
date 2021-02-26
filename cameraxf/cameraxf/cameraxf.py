# Android *only* Camera for Kivy, *full screen only*.
# >>>>>> see BUILDOZER_README.txt <<<<<<
#
# Capture photo, video, or data; both cameras; zoom; focus.
#
# An implementation of Android CameraX
# About CameraX:
#    https://developer.android.com/training/camerax
# Available devices:
#    https://developer.android.com/training/camerax/devices
#
# Kivy Base Class: ModalView
# The contents of this ModalView are Android Views, not Kivy Widgets. Inside
# this ModalView Kivy does not paint the screen or get touch events from the
# screen. Painting and touch handling are done using the Android Java API via
# Pyjnius.
#
#
# CameraXF Class initialization parameters:
###########################################
#
#   capture = (string) 'photo', 'video', 'data', 'none'    default 'none'
#   facing = (string) 'back' or 'front',                   default 'back'
#   callback = None                                      see *Callback* below
#
# This applies only to 'photo' , 'video' and 'data':
#   aspect_ratio = (string) '4:3', '16:9' 
#                                   default photo '4:3' , video or data '16:9'
#
# This applies only to 'data':
#   DO NOT USE CameraX BEHAVIOR INCONSISTENT
#   resolution = (tuple)  eg (1024,768) overides aspect_ratio if specified
#
# These apply only to 'photo' and 'video':
#   private = (boolean) True use Private storage         default Public storage
#   optimize = (string) 'latency', 'quality',              default 'latency'
#   flash = (string) 'on', 'off', 'auto'                   default 'off'
#
# *Callback*
# callback must be a user supplied method with the signature:
#                              def callbackname(self, argument):
# For 'photo' and 'video' the argument is a string containing either
#    a file path, a content uri, or an error (starts with 'ERROR:')
# For 'data' the argument is a Java ImageProxy: androidx.camera.core.ImageProxy
#
# Run time permissions in build()
#   RECORD_AUDIO is only required for 'video'
#   WRITE_EXTERNAL_STORACE maybe required for private storage whan api <=28
#   request_permissions([Permission.CAMERA,Permission.RECORD_AUDIO])
#
# Source https://github.com/RobertFlatt/Android-for-Python/cameraxf
#
# build note: in the example pyzbar may fail to build, try this:
# sudo apt-get update
# sudo apt-get install gettext
# 

from kivy.uix.modalview import ModalView
from kivy.clock import Clock
from functools import partial
from android.runnable import run_on_ui_thread
from inspect import ismethod, signature
from cameraxf.camerax import CameraX
from cameraxf.layoutxf import LayoutXF

class CameraXF(ModalView):
    def __init__(self,
                 capture = 'none',
                 facing = 'back',
                 aspect_ratio = 'default',  
                 flash = 'off',
                 optimize = 'latency',
                 resolution = None,
                 private_storage = False,
                 callback = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.camerax = None
        self.layout = None
        ##############################
        # Option handling
        ##############################
        capture = capture.lower()
        facing = facing.lower()
        aspect_ratio = aspect_ratio.lower()
        flash = flash.lower()
        optimize = optimize.lower()

        self.capture = False
        self.video = False
        self.analysis = False
        if capture == 'photo':
            self.capture = True
        elif capture == 'video':
            self.capture = True
            self.video = True
        elif capture == 'data':
            self.analysis = True

        if aspect_ratio == 'default':
            if capture == 'photo':
                aspect_ratio = '4:3'
            elif capture == 'video':
                aspect_ratio = '16:9'
            elif capture == 'data':
                aspect_ratio = '16:9'
            else:
                aspect_ratio = 'crop'
        elif aspect_ratio not in ['4:3','16:9','crop']:
            aspect_ratio = 'crop'

        if facing not in ['back','front']:
            facing = 'back'

        if flash not in ['on','off','auto']:
            flash = 'off'

        if optimize not in ['latency','quality']:
            optimize = 'latency'

        if resolution and resolution is tuple and len(resolution) == 2:
            resolution = (max(resolution),min(resolution))
        else:
            resolution = None

        if callback:
            if not ismethod(callback) or\
               len(signature(callback).parameters) !=1:
                callbacb = None

        ##############################
        # Create Camera
        ##############################
        self.layout = LayoutXF(
            video_toggle = self.video_toggle,
            photo_take = self.photo_take,
            other_camera = self.other_camera,
            touch_action = self._preview_touch_action,
            dismiss = self.dismiss,
            aspect_ratio = aspect_ratio)

        self.camerax = CameraX(
            capture = self.capture,
            video = self.video,
            analysis = self.analysis,
            facing = facing,
            resolution = resolution,
            aspect_ratio = aspect_ratio,
            callback = callback,
            flash = flash,
            optimize = optimize,
            privatex = private_storage)   

        ##############################
        # Initialize Camera
        ##############################
        self.open()

    ##############################
    # Lifecycle events
    ##############################
    def on_open(self):
        self.build_layout()

    def on_dismiss(self):
        self.video_stop()
        self._unbind_camera()
        if self.layout:
            self.layout.destroy_layout()
        self.camerax = None
        self.layout = None

    def on_size(self, instance, size):
        self.video_stop()
        if self.layout and self.layout.instantiated:
            self.layout.orientation(self.capture, self.video,
                                    self.width,self.height)
            # This fixes the vertical stretch on rotation from
            # initial orientation
            # Seems like a PreviewView:1.0.0-alpha20 issue,
            # but maybe I just don't understand.
            if self.camerax:
                self.camerax.bind_camera(self.layout.imgview)

    def resume(self):
        # Required if the device is rotated between pause and resume
        # perhaps a p4a issue ?
        self.on_size(0,0)

    def pause(self):
        self.video_stop()

    ##############################
    # UI events
    ##############################
    def video_stop(self):
        if self.camerax:
            self.layout.button_red(False,0)
            self.camerax.video_stop()

    def video_start(self):
        if self.camerax:
            self.layout.button_red(True,0)
            self.camerax.video_start()

    def video_toggle(self):
        if self.camerax:
            if self.camerax.video_is_recording:
                self.video_stop()
            else:
                self.video_start()

    def photo_take(self):
        if self.camerax:                     
            self._photo_button_red()
            self.camerax.photo_take()

    def other_camera(self):
        if self.camerax:
            self.camerax.other_camera()

    def _preview_touch_action(self,type,x,y,scale):
        if self.camerax:
            self.camerax.touch_action(type,x,y,scale)

    ##############################
    # Layout
    ##############################
    def build_layout(self):
        if self.layout:
            if self.capture and self.video:
                self.layout.video_layout()
            elif self.capture:
                self.layout.photo_layout()
            elif self.analysis:
                self.layout.analyze_layout()
            else:
                self.layout.none_layout()
            self.layout.orientation(self.capture, self.video,
                                    self.width,self.height)
            self.layout.instantiate(self.camerax.bind_camera,
                                    self.capture, self.video)

    ##############################
    # Utils
    ##############################
    def _photo_button_red(self):
        self.layout.button_red(True,0)
        Clock.schedule_interval(partial(self.layout.button_red,False),0.3)

    @run_on_ui_thread
    def _unbind_camera(self):
        if self.camerax:
            self.camerax.unbind_camera()


