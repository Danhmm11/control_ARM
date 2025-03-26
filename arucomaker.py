import cv2
import numpy as np
from config import config_module
import pickle 

def start_cam():
    cap = cv2.VideoCapture(1)
    return cap
def capture_image() :
    cap = cv2.VideoCapture(0)
    while True:   
        cv2.waitKey(100)
        ret, frame = cap.read()
        if ret:
            cap.release()
            break
    return frame

def identify_tag(config):
    """
    funcition detect and identify the tag
    
    arg:
        maker_img: the image of the tag take camera indefinitly tag

    return: 
        id(string): the name of the tag

        
    """
    with open("calib.pckl", "rb") as f:
        data = pickle.load(f)
        cMat = data[0]
        dcoeff = data[1]
        
    frame  = capture_image()
    dict_aucro = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_7X7_100)
    dt = cv2.aruco.DetectorParameters()
    # _, frame = cap.read()
    
    corners, ids, _ = cv2.aruco.detectMarkers(frame, dict_aucro, parameters=dt)
    if ids is not None and ids.size > 0:
        
        id = int(ids[0])
        
        rvec, tvec, _ = cv2.aruco.estimatePoseSingleMarkers(corners[0], config.marker_size, cMat, dcoeff)
        
        dict_matrix = dict(zip("xyz", tvec.flatten()))
       
        dist = np.linalg.norm(tvec)*100     
    return  id, dist,dict_matrix
def calculate_bias(dict_matrix, reference_dict):
    """
    Tính sai lệch (bias) giữa dict_matrix và reference_dict.

    Args:
        dict_matrix (dict): Dictionary chứa giá trị thực tế.
        reference_dict (dict): Dictionary chuẩn từ config.

    Returns:
        dict: Dictionary chứa sai lệch (bias) cho từng khóa.
    """
    dict_bias = {}
    for key in dict_matrix:
        if key in reference_dict:
            # Tính sai lệch
            dict_bias[key] = dict_matrix[key] - reference_dict[key]
        else:
            print(f"Warning: Key '{key}' not found in reference_dict.")
    
    return dict_bias
def check_bias(cap, config):
    
    """
    Kiểm tra sai lệch (bias) của marker ArUco so với giá trị tham chiếu.

    Function này sử dụng cấu hình từ module "arucomaker" để xác định các giá trị
    thực tế của marker ArUco, sau đó tính toán sai lệch giữa các giá trị thực tế
    và giá trị chuẩn.

    Returns:
        tuple: Gồm ID của marker, sai lệch (bias) đã tính, và khoảng cách tới marker.
    """
    
    with open("calib.pckl", "rb") as f:
        data = pickle.load(f)
        cMat = data[0]
        dcoeff = data[1]
        
    _, frame = cap.read()
    dict_aucro = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
    dt = cv2.aruco.DetectorParameters()
    # _, frame = cap.read()
    
    corners, ids, _ = cv2.aruco.detectMarkers(frame, dict_aucro, parameters=dt)
    if ids is not None and ids.size > 0:
        
        id = int(ids[0])
        
        rvec, tvec, _ = cv2.aruco.estimatePoseSingleMarkers(corners[0], config.marker_size, cMat, dcoeff)
        
        dict_matrix = dict(zip("xyz", tvec.flatten()))
       
        dist = np.linalg.norm(tvec)*100     
    # id ,dist, dict_matrix=  identify_tag(config)
    dict_bias = config["id"+str(id)]
    
    return id,calculate_bias(dict_matrix, dict_bias), dist



    

