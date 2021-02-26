package org.kivy.camerax;

import androidx.camera.core.VideoCapture.OnVideoSavedCallback;
import androidx.camera.core.VideoCapture.OutputFileResults;
import android.net.Uri;
import org.kivy.camerax.CallbackWrapper;

public class VideoSavedCallback implements OnVideoSavedCallback {

    private CallbackWrapper callback_wrapper;

    public VideoSavedCallback(CallbackWrapper callback_wrapper) {	
	this.callback_wrapper = callback_wrapper;
    }    

    public void onVideoSaved(OutputFileResults outputFileResults){
	Uri saveuri = outputFileResults.getSavedUri();
	if (saveuri != null) {
	    this.callback_wrapper.callback_string(saveuri.toString()); 
	}
    }
	
    public void onError(int videoCaptureError, String message, Throwable cause){
	this.callback_wrapper.callback_string("ERROR:" + message); 
    }
}
