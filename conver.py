import math


# Hàm load file config


# Hàm tính tọa độ tâm của bounding box
def get_bounding_box_center(x1, y1, x2, y2):
    """
    Tính tọa độ tâm của bounding box dựa trên tọa độ góc.
    """
    cx = (x1 + x2) // 2  # Trung bình tọa độ x
    cy = (y1 + y2) // 2  # Trung bình tọa độ y
    return cx, cy

# Hàm chuyển tọa độ tương đối
def relative_center(cx_green, cy_green, config):
    """
    Chuyển tọa độ tâm hình chữ nhật xanh sang hệ tọa độ của hình chữ nhật đen.
    """
    x, y = config.in_2d.A  # Lấy tọa độ góc A của hình chữ nhật đen
    cx_relative = cx_green - x
    cy_relative = cy_green - y
    return cx_relative, cy_relative

# Hàm tính khoảng cách giữa hai điểm
def calculate_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# Hàm chuyển đổi pixel sang tọa độ thực
def pixel_to_real(x_pixel, y_pixel, image_width, image_height, config):
    scale_x = image_width/config.AB
    scale_y = image_height /config.AC
    x_real = x_pixel / scale_x
    y_real = y_pixel / scale_y
    return x_real, y_real

def convert_2d_to_arm(bounding_box, config):

    # Load cấu hình # Đường dẫn tuyệt đối
   

    # Tọa độ bounding box
      # x1, y1, x2, y2
    cx, cy = get_bounding_box_center(*bounding_box)

    # Tính khoảng cách giữa các điểm
    weight_2d = calculate_distance(config.in_2d.A, config.in_2d.B)
    height_2d = calculate_distance(config.in_2d.A, config.in_2d.C)

    # In kết quả
    print(f"Tọa độ tâm của bounding box: ({cx}, {cy})")
    print(f"Chiều rộng hình chữ nhật đen (2D): {weight_2d:.2f}")
    print(f"Chiều cao hình chữ nhật đen (2D): {height_2d:.2f}")

    # Tính tọa độ tâm tương đối
    cx, cy = relative_center(cx, cy, config)
    cx, cy =pixel_to_real (cx,cy, weight_2d,height_2d, config.in_3d)
    
    return (cx, cy)