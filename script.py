import json
import os
import cv2
from collections import defaultdict
import argparse
from detector import get_object


def load_detected_objects(json_path):
    """
    Đọc các đối tượng được phát hiện từ file JSON.
    Trả về một danh sách các đối tượng detection.
    """
    if not os.path.exists(json_path):
        print(f"Error: File JSON '{json_path}' không tồn tại.")
        sys.exit(1)
    with open(json_path, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            sys.exit(1)
    detections = []
    for image_entry in data:
        image_name = image_entry.get("image")
        if not image_name:
            print("Warning: Một mục image không có trường 'image'. Bỏ qua mục này.")
            continue
        for det in image_entry.get("detections", []):
            det_copy = det.copy()
            det_copy['image'] = image_name
            detections.append(det_copy)
    return detections

def select_single_object(order, detections):
    """
    Chọn một đối tượng duy nhất có combine_score cao nhất từ toàn bộ detections,
    đảm bảo rằng label của đối tượng đó vẫn còn trong đơn hàng.
    
    Trả về đối tượng đã chọn và đơn hàng đã cập nhật.
    """
    valid_detections = [det for det in detections if order.get(det.get('label_name'), 0) > 0]
    if not valid_detections:
        print("Không còn detections phù hợp với đơn hàng.")
        return None, order
    # Chọn detection có combine_score cao nhất
    selected = max(valid_detections, key=lambda x: x.get('combine_score', 0)) 
    # Cập nhật đơn hàng
    label = selected.get('label_name')
    updated_order = order.copy()
    updated_order[label] -= 1
    return selected, updated_order

def save_selected_object(selected_object, output_path):
    """
    Lưu đối tượng đã chọn vào file JSON.
    Nếu file đã tồn tại, thêm vào danh sách hiện có.
    Nếu không, tạo mới.
    """
    if os.path.exists(output_path):
        with open(output_path, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []
    
    data.append(selected_object)
    
    try:
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Đã lưu đối tượng đã chọn vào '{output_path}'.")
    except IOError as e:
        print(f"Error saving selected object: {e}")

def save_updated_order(updated_order, file_path):
    """
    Ghi đè file đơn hàng gốc với nội dung đã cập nhật.
    """
    try:
        with open(file_path, 'w') as f:
            for label, quantity in sorted(updated_order.items()):
                f.write(f"label {label}: {quantity}\n")
        print(f"Đã ghi đè đơn hàng vào '{file_path}'.")
    except IOError as e:
        print(f"Error saving updated order: {e}")


def draw_bounding_box(selected_object, images_dir, output_dir):
    """
    Vẽ bounding box lên hình ảnh dựa trên đối tượng đã chọn.
    
    Parameters:
    - selected_object: Đối tượng đã chọn.
    - images_dir: Thư mục chứa các hình ảnh gốc.
    - output_dir: Thư mục để lưu hình ảnh đã được vẽ bounding boxes.
    
    Trả về bounding box của đối tượng đã chọn.
    """
    if not selected_object:
        print("Không có đối tượng nào để vẽ.")
        return None
    
    image_name = selected_object.get('image')
    image_path = os.path.join(images_dir, image_name)
    
    if not os.path.exists(image_path):
        print(f"Warning: Không tìm thấy hình ảnh '{image_name}' trong '{images_dir}'. Bỏ qua.")
        return None
    
    # Tạo thư mục output nếu chưa tồn tại
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)    
    # Tải hình ảnh
    image = cv2.imread(image_path)
    if image is None:
        print(f"Warning: Không thể đọc hình ảnh '{image_name}'. Bỏ qua.")
        return None
    
    bbox = selected_object.get('bbox')
    # label_name = selected_object.get('label_name', 'N/A')
    # combine_score = selected_object.get('combine_score', 0)
    
    # if not bbox or len(bbox) != 4:
    #     print(f"Warning: Bounding box không hợp lệ cho detection trong hình '{image_name}'. Bỏ qua detection.")
    #     return None
    
    # x_min, y_min, x_max, y_max = bbox
    # cv2.rectangle(image, (x_min, y_min), (x_max, y_max), color=(0, 255, 0), thickness=2)
    # label = f"{label_name}: {combine_score:.2f}"
    
    # (text_width, text_height), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    # cv2.rectangle(image, (x_min, y_min - text_height - baseline), (x_min + text_width, y_min), (0, 255, 0), thickness=cv2.FILLED)
    # cv2.putText(image, label, (x_min, y_min - baseline), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    
    # output_path = os.path.join(output_dir, image_name)
    # cv2.imwrite(output_path, image)
    # print(f"Đã xử lý và lưu hình ảnh: {output_path}")
    
    # Trả về bounding box
    return bbox



def process_oder(oder, detections):
    # args = parse_arguments()
    print(oder)
    print(detections)
    selected_object, updated_order = select_single_object(oder, detections)
    if selected_object:
        label = selected_object.get('label')
        label_name = selected_object.get('label_name', 'N/A')
        combine_score = selected_object.get('combine_score', 0)
        print(f"Đã chọn đối tượng: Label {label} - {label_name} với combine_score {combine_score}")
    else:
        print("Không chọn được đối tượng nào.")
    
    # Ghi đè lên file gốc
    # save_selected_object(selected_object, args.selected_output)
    # save_updated_order(updated_order, args.order)
    
    # if selected_object:
    #     bbox = draw_bounding_box(selected_object, args.images_dir, args.output_dir)
    #     if bbox:
    #         print(f"\nBounding Box của đối tượng đã chọn: {bbox}")
    return updated_order, selected_object.get('bbox')

