package org.kivy.camerax;

import androidx.camera.core.ImageCapture.OnImageSavedCallback;
import androidx.camera.core.ImageCapture.OutputFileResults;
import androidx.camera.core.ImageCaptureException;
import android.net.Uri;
import org.kivy.camerax.CallbackWrapper;

public class ImageSavedCallback implements OnImageSavedCallback {

    private CallbackWrapper callback_wrapper;

    public ImageSavedCallback(CallbackWrapper callback_wrapper) {	
	this.callback_wrapper = callback_wrapper;
    }    

    public void onImageSaved(OutputFileResults outputFileResults){
	Uri saveuri = outputFileResults.getSavedUri();
	if (saveuri != null) {
	    this.callback_wrapper.callback_string(saveuri.toString()); 
	}
    }
	
    public void onError(ImageCaptureException exception) {
	int id = exception.getImageCaptureError();
	String msg = "ERROR: Android CameraX ImageCaptureException:" + id;
	this.callback_wrapper.callback_string(msg); 
    }
}
