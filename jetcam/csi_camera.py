from .camera import Camera
import atexit
import cv2
import numpy as np
import threading
import traitlets


class CSICamera(Camera):
    
    capture_device = traitlets.Integer(default_value=0)
    capture_fps = traitlets.Integer(default_value=10)
    capture_width = traitlets.Integer(default_value=640)
    capture_height = traitlets.Integer(default_value=480)
    custom_args = traitlets.String(default_value="None")
    
    def __init__(self, *args, **kwargs):
        super(CSICamera, self).__init__(*args, **kwargs)
        try:
            if self.custom_args != "None":
                self.cap = cv2.VideoCapture(self.custom_args, cv2.CAP_GSTREAMER)
            else:
                self.cap = cv2.VideoCapture(self._gst_str(), cv2.CAP_GSTREAMER)

            re, image = self.cap.read()

            if not re:
                raise RuntimeError('Could not read image from camera.')
        except:
            raise RuntimeError(
                'Could not initialize camera.  Please see error trace.')

        atexit.register(self.cap.release)
                
    def _gst_str(self):
        return f"""
        nvarguscamerasrc sensor-id={self.capture_device} ! 
        video/x-raw(memory:NVMM), width={self.capture_width}, height={self.capture_height}, 
        format=(string)NV12, framerate=(fraction){self.capture_fps}/1 ! 
        nvvidconv ! video/x-raw, width=(int){self.width}, height=(int){self.heigh}, 
        format=(string)I420 ! nvjpegenc ! appsink
        """
    
    def _read(self):
        re, image = self.cap.read()
        if re:
            return image
        else:
            raise RuntimeError('Could not read image from camera')