import pyrealsense2 as rs
import numpy as np
import cv2
from config import config_module , setup_logger

config = config_module("capture")
logger = setup_logger(__name__,'DEBUG',is_main = True)

  

def capture_color_image():
    # Khởi tạo pipeline
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, 1280, 720 ,rs.format.bgr8,30)
    # Bắt đầu luồng
    pipeline.start(config)
    frames = pipeline.wait_for_frames()
    color_frame = frames.get_color_frame()
    color_frame = np.asanyarray(color_frame.get_data())
    pipeline.stop()  
    return color_frame 
