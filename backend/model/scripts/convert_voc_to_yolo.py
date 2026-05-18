"""VOC XML标注转YOLO TXT格式，并按train/val划分复制图片"""
import xml.etree.ElementTree as ET
import os
import shutil

# 路径配置
VOC_ROOT = r'D:\qjwy\jzx\TN5000\TN5000'
OUTPUT_ROOT = r'D:\qjwy\jzx\backend\model\datasets\thyroid'

ANNOTATIONS_DIR = os.path.join(VOC_ROOT, 'Annotations')
IMAGES_DIR = os.path.join(VOC_ROOT, 'JPEGImages')
IMAGESETS_DIR = os.path.join(VOC_ROOT, 'ImageSets', 'Main')

def convert_voc_to_yolo(xml_path, img_w, img_h):
    """将VOC XML中的bbox转为YOLO格式"""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    labels = []
    for obj in root.findall('object'):
        bbox = obj.find('bndbox')
        xmin = int(bbox.find('xmin').text)
        ymin = int(bbox.find('ymin').text)
        xmax = int(bbox.find('xmax').text)
        ymax = int(bbox.find('ymax').text)
        
        # 转为YOLO格式: class x_center y_center width height (归一化)
        x_center = (xmin + xmax) / 2.0 / img_w
        y_center = (ymin + ymax) / 2.0 / img_h
        w = (xmax - xmin) / img_w
        h = (ymax - ymin) / img_h
        labels.append(f"0 {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}")
    return labels

def get_image_size(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)
    return w, h

def process_split(split_name):
    """处理一个数据集划分"""
    split_file = os.path.join(IMAGESETS_DIR, f'{split_name}.txt')
    if not os.path.exists(split_file):
        print(f"跳过 {split_name}: 文件不存在")
        return 0
    
    with open(split_file, 'r') as f:
        ids = [line.strip() for line in f.readlines() if line.strip()]
    
    # val和test都放到val目录
    out_split = 'val' if split_name in ('val', 'test') else 'train'
    img_out = os.path.join(OUTPUT_ROOT, 'images', out_split)
    lbl_out = os.path.join(OUTPUT_ROOT, 'labels', out_split)
    
    count = 0
    for img_id in ids:
        xml_path = os.path.join(ANNOTATIONS_DIR, f'{img_id}.xml')
        img_path = os.path.join(IMAGES_DIR, f'{img_id}.jpg')
        
        if not os.path.exists(xml_path) or not os.path.exists(img_path):
            continue
        
        # 获取图像尺寸并转换标注
        w, h = get_image_size(xml_path)
        labels = convert_voc_to_yolo(xml_path, w, h)
        
        # 复制图片
        shutil.copy2(img_path, os.path.join(img_out, f'{img_id}.jpg'))
        
        # 写入YOLO标签
        with open(os.path.join(lbl_out, f'{img_id}.txt'), 'w') as f:
            f.write('\n'.join(labels))
        
        count += 1
    
    return count

if __name__ == '__main__':
    print("开始转换TN5000数据集...")
    
    train_count = process_split('train')
    print(f"训练集: {train_count} 张")
    
    val_count = process_split('val')
    print(f"验证集: {val_count} 张")
    
    test_count = process_split('test')
    print(f"测试集(合并到val): {test_count} 张")
    
    print(f"\n总计: {train_count + val_count + test_count} 张")
    print("转换完成！")
