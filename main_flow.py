# Python module to execute
import numpy  as np
from omegaconf import OmegaConf
import capture
from interface import take_oder , send_data , take_code
from arucomaker import check_bias, start_cam
from script import process_oder
from detector import get_object
from conver import convert_2d_to_arm
def init():
    config_path = "config.yaml"
    config = OmegaConf.load(config_path)
    
    return config, start_cam()
def LayHang(config ): 
    
    return take_oder(config)

def remove(position, Dict_hang):
    Dict_hang.pop(position,None)
    return Dict_hang

def check_empty(Dict_temp):
    c1=Dict_temp["square"]==0
    c2=Dict_temp["hexagon"]==0
    c3=Dict_temp["cricle"]==0
    c4=Dict_temp["octagon"]==0
    return c1*c2*c3*c4

def captureImage():
    while True:
        img = capture.capture_color_image()
        if img is None:
            continue
        break    
    return img

def sendData2Robot(mes, config):
    mes = str(mes)
    send_data(mes,config)
    return 0


def Pick(dict_hang,detection,config):
    dict_temp,box_select = process_oder(dict_hang,detection)
    box_select = convert_2d_to_arm(box_select,config.arm)
    sendData2Robot(box_select,config.interface.arm_pick) # box_selcet here is tuple
    WaitForComplete(config)
     #if dict_temp == 0 
    return dict_temp

def sendNullData2AVG(config):
    send_data("0",config)
    return 0

def WaitForComplete(config):
    complex=1
    while complex:
        a= take_code(config)
        if a=='C':
            complex =0
def runagain(config):
    send_data("1",config)
    return 0
def Tra_hang(position, Dict_hang, config): 
    Dict_temp=Dict_hang[position]
    while (not check_empty(Dict_temp)):
        img= captureImage() # check error
        detection = get_object(img,config.model)
        Dict_temp = Pick(Dict_temp,detection,config)
    
    Dict_hang=remove(position, Dict_hang)
    if not Dict_hang:
        sendNullData2AVG(config.interface.AVG)
    runagain(config.interface.AVG)
    return Dict_hang

def get_run_flag(config): 
    take_code(config)
    return 0
def Return_to_root(config):
    # return to root postion
    send_data("2",config.interface.AVG)
    return 0

def main():
   
   config, cap = init()
   while(1):
       run_flag=get_run_flag(config.interface.arm_pick) # return 0 neu xe dang chay
       if run_flag:
            position,offSet,dict = check_bias(cap, config.arucomaker) 
            if position==0:
                Dict_hang= LayHang(config.interface.receiver)
            else:
                if not Dict_hang: # kiem tra xem da giao hang xong
                    Return_to_root()
                else:
                    Dict_hang=Tra_hang(position, Dict_hang,config)


if __name__ == "__main__":
    main()