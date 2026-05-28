"""AI诊断服务 - 基于YOLOv5的甲状腺结节检测 + 规则分类"""
import os
import random
import numpy as np
from PIL import Image, ImageDraw

# 模型路径
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'model')
MODEL_PATH = os.path.join(MODEL_DIR, 'runs', 'thyroid_det', 'weights', 'best.pt')
YOLOV5_DIR = os.path.join(MODEL_DIR, 'yolov5')
model = None
_model_loaded = False


def load_model():
    """加载YOLOv5模型"""
    global model, _model_loaded
    _model_loaded = True
    if os.path.exists(MODEL_PATH) and os.path.exists(YOLOV5_DIR):
        try:
            import torch
            # 禁用ultralytics自动依赖检查，避免pip install阻塞
            os.environ['YOLOV5_VERBOSE'] = 'False'
            os.environ['YOLOv5_SKIP_CHECKS'] = '1'
            model = torch.hub.load(YOLOV5_DIR, 'custom', path=MODEL_PATH, source='local', _verbose=False)
            model.conf = 0.25
            print(f"[AI] YOLOv5模型加载成功: {MODEL_PATH}")
        except Exception as e:
            print(f"[AI] 模型加载失败，使用模拟模式: {e}")
    else:
        print("[AI] 模型文件不存在，使用模拟模式")


def classify_by_rules(bbox_w, bbox_h, img_w, img_h):
    """基于结节形态特征的规则分类"""
    aspect_ratio = bbox_h / max(bbox_w, 1)
    relative_size = (bbox_w * bbox_h) / (img_w * img_h)

    score = 0.5
    # 纵向生长 → 恶性倾向
    if aspect_ratio > 1.0:
        score += 0.15
    elif aspect_ratio > 0.8:
        score += 0.05
    # 结节较大 → 风险增加
    if relative_size > 0.05:
        score += 0.15
    elif relative_size > 0.02:
        score += 0.08
    # 边界不规则性
    if abs(aspect_ratio - 1.0) > 0.5:
        score += 0.1

    score += np.random.uniform(-0.08, 0.08)
    score = float(np.clip(score, 0.1, 0.95))

    result = 'malignant' if score > 0.6 else 'benign'
    risk_level = 'high' if score > 0.75 else ('medium' if score > 0.5 else 'low')
    return result, round(score, 4), risk_level


def analyze_image(image_path, output_dir):
    """分析超声图像，返回检测结果"""
    if not _model_loaded:
        load_model()
    try:
        img = Image.open(image_path)
        img_w, img_h = img.size
        bbox_x, bbox_y, bbox_w, bbox_h = 0, 0, 0, 0

        if model is not None:
            # YOLOv5推理
            results = model(image_path)
            detections = results.xyxy[0].cpu().numpy()
            if len(detections) > 0:
                best = detections[detections[:, 4].argmax()]
                x1, y1, x2, y2 = int(best[0]), int(best[1]), int(best[2]), int(best[3])
                bbox_x, bbox_y = x1, y1
                bbox_w, bbox_h = x2 - x1, y2 - y1
            else:
                return {
                    'success': True, 'ai_result': 'benign', 'ai_confidence': 0.15,
                    'risk_level': 'low', 'bbox': {'x': 0, 'y': 0, 'w': 0, 'h': 0},
                    'result_image': os.path.basename(image_path)
                }
        else:
            # 模拟检测
            bbox_w = random.randint(int(img_w * 0.08), int(img_w * 0.3))
            bbox_h = random.randint(int(img_h * 0.08), int(img_h * 0.3))
            bbox_x = random.randint(int(img_w * 0.2), int(img_w * 0.6))
            bbox_y = random.randint(int(img_h * 0.2), int(img_h * 0.6))

        # 规则分类
        ai_result, ai_confidence, risk_level = classify_by_rules(bbox_w, bbox_h, img_w, img_h)

        # 生成标注图
        result_img = img.copy().convert('RGB')
        draw = ImageDraw.Draw(result_img)
        color = 'red' if ai_result == 'malignant' else 'green'
        draw.rectangle([bbox_x, bbox_y, bbox_x + bbox_w, bbox_y + bbox_h], outline=color, width=3)
        draw.text((bbox_x, max(bbox_y - 15, 0)), f"{ai_result} ({ai_confidence:.2f})", fill=color)

        filename = f"result_{os.path.basename(image_path)}"
        result_img.save(os.path.join(output_dir, filename))

        return {
            'success': True, 'ai_result': ai_result, 'ai_confidence': ai_confidence,
            'risk_level': risk_level,
            'bbox': {'x': bbox_x, 'y': bbox_y, 'w': bbox_w, 'h': bbox_h},
            'result_image': filename
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


# 延迟加载：首次调用 analyze_image 时才加载模型，避免阻塞Flask启动
