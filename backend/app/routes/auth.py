from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models import User, Patient, OperationLog

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
