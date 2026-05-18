# 基于超声图像的甲状腺结节辅助诊断系统

## 系统简介

本系统是一个基于Web的甲状腺结节辅助诊断平台，集成YOLOv5深度学习检测模型，支持医生、患者、管理员三种角色。系统接收甲状腺超声图像，自动检测结节位置并输出良恶性分类与风险评估。

## 系统架构

```
┌─────────────┐     HTTP/REST      ┌──────────────────┐     SQLAlchemy     ┌─────────┐
│  Vue3 前端   │ ◄──────────────► │   Flask 后端      │ ◄───────────────► │  MySQL  │
│  (Vite)     │     API + JWT     │                  │                    │         │
└─────────────┘                    │  ┌────────────┐  │                    └─────────┘
                                   │  │ AI Service │  │
                                   │  │  YOLOv5    │  │
                                   │  └────────────┘  │
                                   └──────────────────┘
```

**技术栈：**
- 前端：Vue 3 + Vite + Element Plus + Pinia + Axios
- 后端：Flask + Flask-SQLAlchemy + Flask-JWT-Extended + Flask-CORS
- 数据库：MySQL 8.0
- AI模型：YOLOv5s（基于TN5000数据集微调）
- 分类策略：YOLOv5检测结节位置 + 基于形态特征的规则分类（良恶性/风险等级）

## 快速启动

### 1. 环境要求

- Python 3.10+
- Node.js 16+
- MySQL 8.0
- PyTorch 2.0+

### 2. 数据库配置

确保MySQL已启动，修改 `backend/app/config.py` 中的连接信息：
```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:你的密码@localhost:3306/thyroid_system?charset=utf8mb4'
```
系统首次启动会自动创建数据库和表。

### 3. 启动后端

```bash
cd backend
pip install -r requirements.txt
python run.py
```
后端运行在 http://localhost:5000

### 4. 启动前端

```bash
cd frontend
npm install
npm run dev
```
前端运行在 http://localhost:3000

## 默认账户

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |

其他账户可通过注册页面创建，或由管理员在后台创建。

## AI模型训练

### 数据集

使用 TN5000 甲状腺结节超声图像数据集（Pascal VOC格式）：
- 5000张超声图像 + XML标注
- 单类别目标检测：`nodule`（结节）
- 划分：train 3500 / val 500 / test 1000

### 数据预处理（VOC → YOLO格式转换）

```bash
python backend/model/scripts/convert_voc_to_yolo.py
```

该脚本将：
- 读取 `TN5000/TN5000/Annotations/` 中的VOC XML标注
- 转换为YOLO格式（归一化的 `class x_center y_center width height`）
- 按train/val划分复制图像和标签到 `backend/model/datasets/thyroid/`

### 模型微调训练

```bash
# 设置环境变量（Windows解决OpenMP冲突）
$env:KMP_DUPLICATE_LIB_OK='TRUE'

# 启动训练（GPU）
python backend/model/yolov5/train.py \
  --img 640 \
  --batch 16 \
  --epochs 50 \
  --data backend/model/datasets/thyroid/thyroid.yaml \
  --weights yolov5s.pt \
  --project backend/model/runs \
  --name thyroid_det \
  --exist-ok

# CPU训练（无GPU时）
python backend/model/yolov5/train.py \
  --img 640 \
  --batch 8 \
  --epochs 50 \
  --data backend/model/datasets/thyroid/thyroid.yaml \
  --weights yolov5s.pt \
  --project backend/model/runs \
  --name thyroid_det \
  --exist-ok \
  --workers 0 \
  --device cpu
```

训练输出保存在 `backend/model/runs/thyroid_det/`：
- `weights/best.pt` — 最优模型权重（系统自动加载）
- `weights/last.pt` — 最新checkpoint
- `results.csv` — 训练指标记录
- `results.png` — 训练曲线图

### 模型推理测试

```bash
python backend/model/yolov5/detect.py \
  --weights backend/model/runs/thyroid_det/weights/best.pt \
  --source backend/model/datasets/thyroid/images/val/000001.jpg \
  --img 640 \
  --conf 0.25
```

### 模型集成说明

系统启动时自动检测 `backend/model/runs/thyroid_det/weights/best.pt`：
- 若存在 → 加载YOLOv5模型进行真实检测
- 若不存在 → 回退到模拟检测模式

## 功能模块

### 医生模块
- 上传患者超声图像进行AI诊断
- 查看AI检测结果（结节位置、良恶性分类、风险概率）
- 输入/修改诊断意见
- 查看历史诊断记录

### 患者模块
- 注册登录、上传个人检查图像
- 查看诊断结果（AI结果 + 医生意见）
- 风险等级解释

### 管理员模块
- 用户管理、数据管理、操作日志、系统统计

## 项目结构

```
jzx/
├── backend/                    # Flask后端
│   ├── app/
│   │   ├── __init__.py         # Flask应用工厂
│   │   ├── config.py           # 数据库/JWT配置
│   │   ├── models/             # SQLAlchemy数据模型
│   │   ├── routes/             # API路由
│   │   │   ├── auth.py         # 登录/注册/JWT认证
│   │   │   ├── doctor.py       # 医生：上传图像、诊断、历史
│   │   │   ├── patient.py      # 患者：查看结果、历史
│   │   │   └── admin.py        # 管理员：用户/数据/日志
│   │   └── services/
│   │       └── ai_service.py   # AI推理服务（YOLOv5+规则分类）
│   ├── model/
│   │   ├── yolov5/             # YOLOv5框架（git clone）
│   │   ├── datasets/thyroid/   # YOLO格式数据集
│   │   │   ├── images/train/   # 训练图像(3500张)
│   │   │   ├── images/val/     # 验证图像(1500张)
│   │   │   ├── labels/train/   # 训练标签
│   │   │   ├── labels/val/     # 验证标签
│   │   │   └── thyroid.yaml    # 数据集配置
│   │   ├── runs/thyroid_det/   # 训练输出
│   │   │   └── weights/best.pt # 最优模型权重
│   │   └── scripts/
│   │       ├── convert_voc_to_yolo.py  # 数据格式转换
│   │       └── train.py                # 训练启动脚本
│   ├── uploads/                # 用户上传图像存储
│   ├── requirements.txt
│   └── run.py                  # Flask启动入口
├── frontend/                   # Vue3前端
│   ├── src/
│   │   ├── api/index.js        # Axios封装+JWT拦截器
│   │   ├── router/index.js     # 路由+权限守卫
│   │   ├── stores/user.js      # Pinia用户状态
│   │   └── views/
│   │       ├── Login.vue       # 登录页
│   │       ├── Register.vue    # 注册页
│   │       ├── Layout.vue      # 布局框架
│   │       ├── doctor/         # 医生页面组件
│   │       ├── patient/        # 患者页面组件
│   │       └── admin/          # 管理员页面组件
│   ├── package.json
│   └── vite.config.js          # Vite配置+API代理
├── TN5000/TN5000/              # 原始数据集（VOC格式）
│   ├── Annotations/            # 5000个XML标注
│   ├── JPEGImages/             # 5000张超声图像
│   └── ImageSets/Main/         # train/val/test划分
├── database/init.sql           # 数据库初始化SQL
└── README.md
```
