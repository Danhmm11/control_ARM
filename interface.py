import socket
   
from config import setup_logger ,config_module
import subprocess
logger = setup_logger(__name__,'DEBUG',is_main = True)

def connect2_network(config):
    id_wifi = config.wifi_id
    password_wifi = config.wifi_password
def fotmat_oder(mes):
    """
    funcition format the oder sended from the loccation pick product
    input:
        mes (string): mes take off the oder 
    return 
        result (dict): oder after format
    """
   
    rows = mes.split(";")
# Tạo dict chứa kết quả
    result = {}
    for index, row in enumerate(rows, start=1):
        # Tách từng giá trị trong hàng
        values = row.split(",")
        # Gắn các giá trị a, b, c, d vào một dict tạm thời
        result[index] = {
            "square": int(values[0]),
            "hexagon": int(values[1]),
            "cricle": int(values[2]),
            "octagon": int(values[3]),
        }
    return result
def fotmat_packet(data,code): #code 1 list good code 2 offset split with space 
    """
    funcition format the packet
    arg :
        data (list): the data of the packet
        code (int): the code of the packet code 1 data with list code 2 data with offset
    return 
        packet (string): the packet send to more device
    
    """
    try:
        match code:
            case 1:
                packet = " ".join(data)
                logger.info(packet)
            case 2:
                packet = f"x:{data[0]} y:{data[1]} z:{data[2]} ".join(data)
                logger.debug(packet)
            
    except ValueError:
        logger.error(f"{code} is not a value accepted")
    return packet  
def start_up_receiver(config):
    """
        funcition start the serceiver lisen receiver
        return 
            ret (bool): the result of the pocess start_up_receciver
    """ 
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((config.ip , config.port))
    return  server_socket
    
def send_data(message,config):
    """
    funcition send the data to the server

    arg:
        devitation
    return:
        result (bool): the result of the send 
    """
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((config.ip, config.port))
        logger.debug(f"ip sender is :{config.ip} port sender is :{config.port}")
        client_socket.sendall(message.encode('utf-8'))
        ret = True
        client_socket.close()
    except ValueError:
        logger.error("can not send data")
        ret = False
    
    return ret

def receive_data(server_socket,config):
    """
    funcition receive the data from the server
    return:
        data (string): the data of the server
    """
    server_socket.listen(1)
    client_socket, client_address = server_socket.accept()
    message = client_socket.recv(1024).decode('utf-8')
    logger.info(f"connect from {client_address}")
    logger.debug(message)
    
    server_socket.close()
    return message

def connect_to_wifi(ssid, password):
    try:
        # Tạo hồ sơ Wi-Fi tạm thời
        profile_xml = f"""
        <WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
            <name>{ssid}</name>
            <SSIDConfig>
                <SSID>
                    <name>{ssid}</name>
                </SSID>
            </SSIDConfig>
            <connectionType>ESS</connectionType>
            <connectionMode>auto</connectionMode>
            <MSM>
                <security>
                    <authEncryption>
                        <authentication>WPA2PSK</authentication>
                        <encryption>AES</encryption>
                        <useOneX>false</useOneX>
                    </authEncryption>
                    <sharedKey>
                        <keyType>passPhrase</keyType>
                        <protected>false</protected>
                        <keyMaterial>{password}</keyMaterial>
                    </sharedKey>
                </security>
            </MSM>
        </WLANProfile>
        """
        profile_path = "wifi_profile.xml"

        # Lưu hồ sơ Wi-Fi ra tệp XML
        with open(profile_path, "w") as file:
            file.write(profile_xml)

        # Thêm hồ sơ Wi-Fi vào hệ thống
        subprocess.run(["netsh", "wlan", "add", "profile", f"filename={profile_path}"], check=True)

        # Kết nối tới Wi-Fi
        subprocess.run(["netsh", "wlan", "connect", f"name={ssid}"], check=True)

        print(f"Kết nối thành công với Wi-Fi: {ssid}")
    except subprocess.CalledProcessError as e:
        print(f"Lỗi khi kết nối tới Wi-Fi: {e}")
def take_oder(config):
    config = config_module("interface","config.yaml")
    while True:
        
        sever_socket = start_up_receiver(config.receiver)
        oder = fotmat_oder(receive_data(sever_socket,config))
        if oder:
            break
    sever_socket.close()
    return oder

def take_code(config):
    
    while True:
        
        sever_socket = start_up_receiver(config)
        code = receive_data(sever_socket,config)
        if code:
            break
    sever_socket.close()
    return code