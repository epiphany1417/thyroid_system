"""训练YOLOv5甲状腺结节检测模型"""
import subprocess
import os

# 配置
YOLOV5_DIR = os.path.join(os.path.dirname(__file__), '..', 'yolov5')
DATA_YAML = os.path.join(os.path.dirname(__file__), '..', 'datasets', 'thyroid', 'thyroid.yaml')
PROJECT_DIR = os.path.join(os.path.dirname(__file__), '..', 'runs')

def train():
    """启动YOLOv5训练"""
    cmd = [
        'python', os.path.join(YOLOV5_DIR, 'train.py'),
        '--img', '640',
        '--batch', '16',
        '--epochs', '100',
        '--data', DATA_YAML,
        '--weights', 'yolov5s.pt',
        '--project', PROJECT_DIR,
        '--name', 'thyroid_det',
        '--exist-ok'
    ]
    print(f"执行训练命令: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=YOLOV5_DIR)

if __name__ == '__main__':
    if not os.path.exists(YOLOV5_DIR):
        print("正在克隆YOLOv5...")
        subprocess.run(['git', 'clone', 'https://github.com/ultralytics/yolov5.git', YOLOV5_DIR])
        subprocess.run(['pip', 'install', '-r', os.path.join(YOLOV5_DIR, 'requirements.txt'), '-q'])
    
    train()
