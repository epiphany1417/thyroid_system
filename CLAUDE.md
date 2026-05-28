# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 快速启动

```bash
# 后端 (127.0.0.1:5000)
cd backend && pip install -r requirements.txt && python run.py

# 前端 (localhost:3000, API代理到127.0.0.1:5000)
cd frontend && npm install && npm run dev
```

数据库无需手动创建，`run.py` 启动时自动创建数据库 `thyroid_system`、表结构和默认管理员（`admin/admin123`）。

## 技术栈

- 前端：Vue 3 (Composition API) + Vite + Element Plus + Pinia + Axios
- 后端：Flask (app工厂模式) + Flask-SQLAlchemy + Flask-JWT-Extended + Flask-CORS
- 数据库：MySQL 8.0 + PyMySQL
- AI模型：YOLOv5s（从 `yolov5s.pt` 预训练权重微调）
- LLM：DeepSeek（OpenAI兼容接口），用于生成诊断参考意见

## 项目架构

```
jzx/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Flask工厂，注册Blueprint + db/jwt/CORS初始化
│   │   ├── config.py            # 配置（DB/JWT密钥、上传路径、LLM配置）
│   │   ├── models/__init__.py   # User / Patient / Diagnosis / OperationLog / VerificationCode
│   │   ├── routes/              # 按角色拆分: auth/doctor/patient/admin
│   │   └── services/
│   │       ├── ai_service.py    # AI推理（YOLOv5检测 + 规则分类）
│   │       └── llm_service.py   # LLM诊断意见生成（DeepSeek/OpenAI兼容）
│   ├── model/
│   │   ├── yolov5/              # ultralytics/yolov5（已禁用check_requirements）
│   │   ├── datasets/thyroid/    # 转换后的YOLO格式数据
│   │   ├── runs/thyroid_det/weights/best.pt  # 训练产出（.gitignore）
│   │   └── scripts/             # VOC→YOLO转换 + 训练脚本
│   ├── uploads/                 # 用户上传图像（.gitignore）
│   └── run.py                   # 入口：create_app() + db初始化 + 模型预加载
├── frontend/
│   ├── src/
│   │   ├── api/index.js         # Axios实例：/api baseURL + JWT拦截器（登录接口排除401跳转）
│   │   ├── router/index.js      # 按角色分组路由 + beforeEach守卫
│   │   ├── stores/user.js       # Pinia：user/token状态，localStorage持久化
│   │   ├── views/Layout.vue     # 侧栏+顶部栏布局，按角色渲染不同菜单
│   │   ├── views/Login.vue / Register.vue / ForgotPassword.vue
│   │   └── views/doctor/ patient/ admin/  # 各角色页面组件
│   └── vite.config.js           # 端口3000, /api → 127.0.0.1:5000 代理
├── database/init.sql            # 手动建库建表参考（可选，Flask自动创建）
└── TN5000/                      # 原始VOC格式数据集（.gitignore）
```

## 核心设计要点

### AI服务（延迟加载）

`ai_service.py` 中 `load_model()` 采用延迟加载策略：
- 模型在 `run.py` 启动的 reloader 子进程中预加载（通过 `WERKZEUG_RUN_MAIN` 判断）
- 模型文件存在 → 加载YOLOv5做真实目标检测
- 模型不存在 → 随机生成bbox模拟检测
- `hubconf.py` 已禁用 `check_requirements()`，避免 pip 自动更新阻塞请求

分类不依赖模型：检测出bbox后，通过 `classify_by_rules()` 基于形态特征（纵横比、相对面积、边界不规则度）的规则判定良恶性/风险等级。

### LLM诊断意见生成

`llm_service.py` 在AI分类完成后调用大模型生成诊断参考意见：
- 每种分类结果（良性/恶性 × 低/中/高风险）有固定模板描述
- 模板 + 检测数据组成 prompt 输入 DeepSeek 生成专业诊断文本
- 使用 OpenAI 兼容接口（`https://api.deepseek.com`）
- LLM 调用失败不影响主流程，仅跳过意见生成

### API路由与权限

- URL前缀：`/api/auth`、`/api/doctor`、`/api/patient`、`/api/admin`
- JWT认证：除登录/注册外，所有API需要 `Bearer token`
- 角色校验：每个路由内部通过 `user.role` 检查权限，前端路由守卫做重定向保护
- 诊断流程分两步：`POST /api/doctor/diagnose/:id` 执行AI诊断（保存AI结果），`POST /api/doctor/diagnose/:id/submit` 医生提交意见完成诊断
- 患者可以自行上传图像并指定医生，也可由医生代为上传

### 前端路由分组

路由路径按角色前缀：`/doctor/*`、`/patient/*`、`/admin/*`，共用 `Layout.vue` 框架组件。`beforeEach` 守卫检查token存在性和角色匹配，不匹配时重定向到该角色首页。

### 数据库关系

- `User` ← `Diagnosis.patient_id` (诊断的患者)
- `User` ← `Diagnosis.doctor_id` (负责医生，可空)
- `User` ← `Patient.user_id` (患者扩展信息：性别/年龄/病史)
- `OperationLog.user_id` → `User` (操作日志)

### 关键配置

- `backend/app/config.py`：数据库连接字符串需改为本地MySQL密码
- `vite.config.js`：开发时 `/api` 请求代理到 `127.0.0.1:5000`（注意不要用localhost，避免IPv6问题）
- 图像上传限制 16MB，允许 jpg/png/jpeg
- JWT token有效期 86400秒（24小时）
- LLM配置：`LLM_API_KEY`、`LLM_BASE_URL`、`LLM_MODEL` 在 config.py 或环境变量中设置
