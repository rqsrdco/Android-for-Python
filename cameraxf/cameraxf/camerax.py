import datetime
from android.storage import app_storage_path
from android.runnable import run_on_ui_thread   
from jnius import autoclass, cast
from os.path import exists, join
from os import mkdir
from cameraxf.listeners import TouchListener, CallbackWrapper

# General
PythonActivity = autoclass('org.kivy.android.PythonActivity')
Environment = autoclass('android.os.Environment')
File = autoclass('java.io.File')
Size = autoclass('android.util.Size')

# MediaStore
MediaStore = autoclass('android.provider.MediaStore')
MediaStoreImagesMedia = autoclass('android.provider.MediaStore$Images$Media')
MediaStoreVideoMedia = autoclass('android.provider.MediaStore$Video$Media')
MediaStoreMediaColumns = autoclass('android.provider.MediaStore$MediaColumns')
ContentValues = autoclass('android.content.ContentValues')

# CameraX components:
PreviewBuilder = autoclass('androidx.camera.core.Preview$Builder')
AspectRatio = autoclass('androidx.camera.core.AspectRatio')
ImageCapture = autoclass('androidx.camera.core.ImageCapture') 
ImageCaptureBuilder = autoclass('androidx.camera.core.ImageCapture$Builder')
ImageCaptureOutputFileOptionsBuilder = autoclass('androidx.camera.core.ImageCapture$OutputFileOptions$Builder')
VideoCaptureBuilder = autoclass('androidx.camera.core.VideoCapture$Builder')
VideoCaptureOutputFileOptionsBuilder = autoclass('androidx.camera.core.VideoCapture$OutputFileOptions$Builder')
FocusMeteringActionBuilder = autoclass('androidx.camera.core.FocusMeteringAction$Builder')
ImageAnalysis = autoclass('androidx.camera.core.ImageAnalysis')
ImageAnalysisBuilder = autoclass('androidx.camera.core.ImageAnalysis$Builder')
ProcessCameraProvider = autoclass('androidx.camera.lifecycle.ProcessCameraProvider')
UseCaseGroupBuilder = autoclass('androidx.camera.core.UseCaseGroup$Builder') 
CameraSelector = autoclass('androidx.camera.core.CameraSelector')
CameraSelectorBuilder = autoclass('androidx.camera.core.CameraSelector$Builder')
ProcessLifecycleOwner = autoclass('androidx.lifecycle.ProcessLifecycleOwner')
CameraInfo =autoclass('androidx.camera.core.CameraInfo')

# Local Java
ImageSavedCallback = autoclass('org.kivy.camerax.ImageSavedCallback')
VideoSavedCallback = autoclass('org.kivy.camerax.VideoSavedCallback')
ImageAnalysisAnalyzer = autoclass('org.kivy.camerax.ImageAnalysisAnalyzer')
    

class CameraX():
    def __init__(self,
                 capture,
                 video,
                 analysis,
                 facing,
                 resolution,
                 aspect_ratio,
                 callback,
                 flash,
                 optimize,
                 privatex,
                 **kwargs):
        super().__init__(**kwargs)

        self.capture = capture
        self.video = video
        self.analysis = analysis
        self.resolution = resolution
        self.callback = callback
        self.private = privatex

        self.ASPECT_RATIO_NONE = 432
        if aspect_ratio == '16:9':
            self.aspect_ratio = AspectRatio.RATIO_16_9
        elif aspect_ratio == '4:3':
            self.aspect_ratio = AspectRatio.RATIO_4_3
        elif aspect_ratio == 'crop' and not self.capture:
            self.aspect_ratio = self.ASPECT_RATIO_NONE
        else:
            self.aspect_ratio = AspectRatio.RATIO_4_3
            
        if facing == 'front':
            self.lens_facing = CameraSelector.LENS_FACING_FRONT
        elif facing == 'back':
            self.lens_facing = CameraSelector.LENS_FACING_BACK
        else:
            self.lens_facing = CameraSelector.LENS_FACING_BACK
            
        if optimize == 'quality':
            self.optimize = ImageCapture.CAPTURE_MODE_MAXIMIZE_QUALITY
        elif optimize == 'latency':
            self.optimize = ImageCapture.CAPTURE_MODE_MINIMIZE_LATENCY
        else:
            self.optimize = ImageCapture.CAPTURE_MODE_MINIMIZE_LATENCY
            
        if flash == 'on':
            self.flash_mode = ImageCapture.FLASH_MODE_ON
        elif flash == 'auto':
            self.flash_mode = ImageCapture.FLASH_MODE_AUTO
        elif flash == 'off':
            self.flash_mode = ImageCapture.FLASH_MODE_OFF
        else:
            self.flash_mode = ImageCapture.FLASH_MODE_OFF

        self.cameraProvider = None
        self.video_is_recording = False


    ##############################
    # Android CameraX
    ##############################
    @run_on_ui_thread        
    def bind_camera(self,preview_view):   
        self.preview_view = preview_view   
        # CameraProvider
        context =  cast('android.content.Context',
                        PythonActivity.mActivity.getApplicationContext())
        cpf = ProcessCameraProvider.getInstance(context)
        self.cameraProvider = cpf.get()
        self.cameraProvider.unbindAll()

        # CameraSelector
        csb = CameraSelectorBuilder()
        csb.requireLensFacing(self.lens_facing)
        cameraSelector = csb.build()

        # ImageAnalysis
        if self.analysis:
            wm =  PythonActivity.mActivity.getWindowManager()
            self.rotation = wm.getDefaultDisplay().getRotation()

            strategy = ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST
            self.ib = ImageAnalysisBuilder()
            if self.resolution:
                self.ib.setTargetResolution(Size(self.resolution[0],
                                                 self.resolution[1]))
            else:
                self.ib.setTargetAspectRatio(self.aspect_ratio)
            self.ib.setBackpressureStrategy(strategy)
            self.ib.setTargetRotation(self.rotation)
            self.imageAnalysis = self.ib.build()
            self.te = context.getMainExecutor()
            self.wrapper = CallbackWrapper(self.callback)  
            self.iaa = ImageAnalysisAnalyzer(self.wrapper)
            self.imageAnalysis.setAnalyzer(self.te, self.iaa)

        # ImageCapture
        if self.capture:
            mActivity =  PythonActivity.mActivity
            rot = mActivity.getWindowManager().getDefaultDisplay().getRotation()
            if self.video:
                self.cb = VideoCaptureBuilder()
            else:
                self.cb = ImageCaptureBuilder()
                self.cb.setFlashMode(self.flash_mode)
                self.cb.setCaptureMode(self.optimize)
            self.cb.setTargetAspectRatio(self.aspect_ratio)
            self.cb.setTargetRotation(rot)
            self.imageCapture = self.cb.build()

        # Preview
        pb = PreviewBuilder()
        if self.analysis and self.resolution:
            pb.setTargetResolution(Size(self.resolution[0],
                                        self.resolution[1])) 
        elif self.capture or self.analysis:
            if self.aspect_ratio == AspectRatio.RATIO_4_3 or\
               self.aspect_ratio == AspectRatio.RATIO_16_9:
                pb.setTargetAspectRatio(self.aspect_ratio)
        preview = pb.build()
        preview.setSurfaceProvider(preview_view.getSurfaceProvider())


        # UseCase
        ucgb = UseCaseGroupBuilder()
        ucgb.addUseCase(preview)
        if self.capture:
            ucgb.addUseCase(self.imageCapture)
        if self.analysis:
            ucgb.addUseCase(self.imageAnalysis)
        #if previewview:
        ucgb.setViewPort(preview_view.getViewPort())  
        useCaseGroup = ucgb.build()
        
        # Bind
        self.cam = self.cameraProvider.bindToLifecycle(ProcessLifecycleOwner.get(),
                                                       cameraSelector,
                                                       useCaseGroup)
        self.cam.cameraControl.setLinearZoom(0.5)
        self.focus(0.5,0.5)

    @run_on_ui_thread        
    def unbind_camera(self):
        if self.cameraProvider:
            self.cameraProvider.unbindAll()

        
    ##############################
    # User Events
    ##############################
    def other_camera(self):
        if self.lens_facing == CameraSelector.LENS_FACING_FRONT:
            self.lens_facing = CameraSelector.LENS_FACING_BACK
        else:
            self.lens_facing = CameraSelector.LENS_FACING_FRONT
        self.bind_camera(self.preview_view)
    
    def focus(self,x,y):
        factory = self.preview_view.getMeteringPointFactory()
        self.point = factory.createPoint(x,y)
        self.action = FocusMeteringActionBuilder(self.point).build()
        if self.cam:
            self.cam.cameraControl.startFocusAndMetering(self.action)
        
    def touch_action(self,type,x,y,scale):
        if type == 'tapup':
            self.focus(x,y)
        elif type == 'scale':
            if self.cam:
                self.zs = self.cam.cameraInfo.getZoomState().getValue()
                scale = self.zs.getZoomRatio() * scale
                scale = min(scale,self.zs.getMaxZoomRatio())
                scale = max(scale,self.zs.getMinZoomRatio())
                self.cam.cameraControl.setZoomRatio(scale)

    def video_stop(self):
        if self.video_is_recording:
            self.preview_view.performClick()
            self.imageCapture.stopRecording()
            self.video_is_recording = not self.video_is_recording
        
    def video_start(self):
        if not self.video_is_recording:
            self.preview_view.performClick()
            context = PythonActivity.mActivity.getApplicationContext()
            dt = datetime.datetime.now()
            today = dt.strftime("%Y_%m_%d")
            name = dt.strftime("%H_%M_%S") + '.mp4'
            if self.private:
                dir = join(app_storage_path(), Environment.DIRECTORY_DCIM)
                if not exists(dir):
                    mkdir(dir)
                dir = join(dir,today)
                if not exists(dir):
                    mkdir(dir)
                self.filepath = join(dir,name)
                self.videofile = File(self.filepath)
                self.vcf = VideoCaptureOutputFileOptionsBuilder(self.videofile).build()
            else:
                self.cr =  PythonActivity.mActivity.getContentResolver()
                collection = MediaStoreVideoMedia.EXTERNAL_CONTENT_URI
                self.cv = ContentValues()
                self.cv.put(MediaStoreMediaColumns.DISPLAY_NAME, name)
                self.cv.put(MediaStoreMediaColumns.MIME_TYPE, "video/mp4")
                self.cv.put(MediaStoreMediaColumns.RELATIVE_PATH,
                            join(Environment.DIRECTORY_DCIM,
                                 self.app_name(),today))
                self.vcf = VideoCaptureOutputFileOptionsBuilder(self.cr,
                                                                collection,
                                                                self.cv).build()
            self.te = context.getMainExecutor()
            self.wrapper = CallbackWrapper(self.callback)  
            self.vsc = VideoSavedCallback(self.wrapper)
            self.imageCapture.startRecording(self.vcf,self.te,self.vsc)
            self.video_is_recording = not self.video_is_recording

    def photo_take(self):
        self.preview_view.performClick()
        context = PythonActivity.mActivity.getApplicationContext()
        dt = datetime.datetime.now()
        today = dt.strftime("%Y_%m_%d")
        name = dt.strftime("%H_%M_%S")
        if self.private:
            file = name + '.jpg'
            dir = join(app_storage_path(), Environment.DIRECTORY_DCIM)
            if not exists(dir):
                mkdir(dir)
            dir = join(dir,today)
            if not exists(dir):
                mkdir(dir)
            self.filepath = join(dir,file)
            self.picfile = File(self.filepath)
            self.icf = ImageCaptureOutputFileOptionsBuilder(self.picfile).build()
        else:
            self.cr =  PythonActivity.mActivity.getContentResolver()
            collection = MediaStoreImagesMedia.EXTERNAL_CONTENT_URI
            self.cv = ContentValues()
            self.cv.put(MediaStoreMediaColumns.DISPLAY_NAME, name)
            self.cv.put(MediaStoreMediaColumns.MIME_TYPE, "image/jpeg")
            self.cv.put(MediaStoreMediaColumns.RELATIVE_PATH,
                        join(Environment.DIRECTORY_DCIM,
                             self.app_name(),today))
            self.icf = ImageCaptureOutputFileOptionsBuilder(self.cr,
                                                            collection,
                                                            self.cv).build()

        self.te = context.getMainExecutor()
        self.wrapper = CallbackWrapper(self.callback)  
        self.isc = ImageSavedCallback(self.wrapper)
        self.imageCapture.takePicture(self.icf,self.te,self.isc)

    def app_name(self):
        context = PythonActivity.mActivity.getApplicationContext()
        appinfo = context.getApplicationInfo()
        if appinfo.labelRes:
            name = context.getString(appinfo.labelRes)
        else:
            name = appinfo.nonLocalizedLabel.toString()
        return name
