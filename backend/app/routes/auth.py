from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models import User, Patient, OperationLog, VerificationCode

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'patient')
    real_name = data.get('real_name', '')
    
    if not username or not password:
        return jsonify({'code': 400, 'msg': '用户名和密码不能为空'}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({'code': 400, 'msg': '用户名已存在'}), 400
    
    user = User(
        username=username,
        password_hash=generate_password_hash(password),
        role=role,
        real_name=real_name,
        phone=data.get('phone', ''),
        email=data.get('email', '')
    )
    db.session.add(user)
    db.session.commit()
    
    # 如果是患者，创建患者信息
    if role == 'patient':
        patient = Patient(user_id=user.id, gender=data.get('gender'), age=data.get('age'))
        db.session.add(patient)
        db.session.commit()
    
    return jsonify({'code': 200, 'msg': '注册成功', 'data': user.to_dict()})

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'code': 401, 'msg': '用户名或密码错误'}), 401
    
    if not user.is_active:
        return jsonify({'code': 403, 'msg': '账户已被禁用'}), 403
    
    token = create_access_token(identity=str(user.id))
    
    # 记录登录日志
    log = OperationLog(user_id=user.id, action='login', detail='用户登录', ip_address=request.remote_addr)
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'code': 200, 'msg': '登录成功', 'data': {'token': token, 'user': user.to_dict()}})

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'msg': '用户不存在'}), 404
    return jsonify({'code': 200, 'data': user.to_dict()})

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    data = request.get_json()
    
    if data.get('real_name'):
        user.real_name = data['real_name']
    if data.get('phone'):
        user.phone = data['phone']
    if data.get('email'):
        user.email = data['email']
    
    db.session.commit()
    return jsonify({'code': 200, 'msg': '更新成功', 'data': user.to_dict()})


@auth_bp.route('/send-code', methods=['POST'])
def send_code():
    """发送验证码（手机号或邮箱）"""
    data = request.get_json()
    contact = data.get('contact', '').strip()

    if not contact:
        return jsonify({'code': 400, 'msg': '请输入手机号或邮箱'}), 400

    # 查找该联系方式是否存在于用户表中
    user = User.query.filter(
        db.or_(User.phone == contact, User.email == contact)
    ).first()
    if not user:
        return jsonify({'code': 404, 'msg': '该手机号或邮箱未注册'}), 404

    # 生成6位随机验证码
    import random
    code = ''.join([str(random.randint(0, 9)) for _ in range(6)])

    # 存储验证码，60秒过期
    from datetime import datetime, timedelta
    vc = VerificationCode(
        contact=contact,
        code=code,
        expires_at=datetime.now() + timedelta(seconds=60)
    )
    db.session.add(vc)
    db.session.commit()

    # 开发环境直接返回验证码，生产环境改为发送邮件/短信
    return jsonify({
        'code': 200,
        'msg': '验证码已生成',
        'data': {'code': code}  # 生产环境应移除此行
    })


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """通过验证码重置密码"""
    data = request.get_json()
    contact = data.get('contact', '').strip()
    code = data.get('code', '').strip()
    new_password = data.get('new_password', '')

    if not contact or not code or not new_password:
        return jsonify({'code': 400, 'msg': '参数不完整'}), 400

    if len(new_password) < 6:
        return jsonify({'code': 400, 'msg': '密码长度不能少于6位'}), 400

    # 查找有效验证码
    from datetime import datetime
    vc = VerificationCode.query.filter(
        VerificationCode.contact == contact,
        VerificationCode.code == code,
        VerificationCode.used == False
    ).order_by(VerificationCode.created_at.desc()).first()

    if not vc:
        return jsonify({'code': 400, 'msg': '验证码错误'}), 400

    if vc.expires_at < datetime.now():
        return jsonify({'code': 400, 'msg': '验证码已过期，请重新获取'}), 400

    # 查找对应用户
    user = User.query.filter(
        db.or_(User.phone == contact, User.email == contact)
    ).first()
    if not user:
        return jsonify({'code': 404, 'msg': '用户不存在'}), 404

    # 更新密码
    user.password_hash = generate_password_hash(new_password)
    vc.used = True
    db.session.commit()

    return jsonify({'code': 200, 'msg': '密码重置成功，请使用新密码登录'})
