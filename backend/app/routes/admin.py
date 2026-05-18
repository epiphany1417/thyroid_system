from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Diagnosis, OperationLog

admin_bp = Blueprint('admin', __name__)

def check_admin(user_id):
    user = User.query.get(user_id)
    return user and user.role == 'admin'

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    if not check_admin(int(get_jwt_identity())):
        return jsonify({'code': 403, 'msg': '无权限'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    role = request.args.get('role')
    
    query = User.query
    if role:
        query = query.filter_by(role=role)
    
    pagination = query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page)
    return jsonify({
        'code': 200,
        'data': {
            'items': [u.to_dict() for u in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        }
    })

@admin_bp.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    if not check_admin(int(get_jwt_identity())):
        return jsonify({'code': 403, 'msg': '无权限'}), 403
    
    from werkzeug.security import generate_password_hash
    data = request.get_json()
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'code': 400, 'msg': '用户名已存在'}), 400
    
    user = User(
        username=data['username'],
        password_hash=generate_password_hash(data.get('password', '123456')),
        role=data.get('role', 'patient'),
        real_name=data.get('real_name', ''),
        phone=data.get('phone', ''),
        email=data.get('email', '')
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'code': 200, 'msg': '创建成功', 'data': user.to_dict()})

@admin_bp.route('/users/<int:uid>', methods=['DELETE'])
@jwt_required()
def delete_user(uid):
    if not check_admin(int(get_jwt_identity())):
        return jsonify({'code': 403, 'msg': '无权限'}), 403
    
    user = User.query.get_or_404(uid)
    user.is_active = False
    db.session.commit()
    return jsonify({'code': 200, 'msg': '已禁用'})

@admin_bp.route('/users/<int:uid>/activate', methods=['PUT'])
@jwt_required()
def activate_user(uid):
    if not check_admin(int(get_jwt_identity())):
        return jsonify({'code': 403, 'msg': '无权限'}), 403
    
    user = User.query.get_or_404(uid)
    user.is_active = True
    db.session.commit()
    return jsonify({'code': 200, 'msg': '已启用'})

@admin_bp.route('/diagnoses', methods=['GET'])
@jwt_required()
def get_all_diagnoses():
    if not check_admin(int(get_jwt_identity())):
        return jsonify({'code': 403, 'msg': '无权限'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pagination = Diagnosis.query.order_by(Diagnosis.created_at.desc()).paginate(page=page, per_page=per_page)
    return jsonify({
        'code': 200,
        'data': {
            'items': [d.to_dict() for d in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        }
    })

@admin_bp.route('/diagnoses/<int:diag_id>', methods=['DELETE'])
@jwt_required()
def delete_diagnosis(diag_id):
    if not check_admin(int(get_jwt_identity())):
        return jsonify({'code': 403, 'msg': '无权限'}), 403
    
    diagnosis = Diagnosis.query.get_or_404(diag_id)
    db.session.delete(diagnosis)
    db.session.commit()
    return jsonify({'code': 200, 'msg': '已删除'})

@admin_bp.route('/logs', methods=['GET'])
@jwt_required()
def get_logs():
    if not check_admin(int(get_jwt_identity())):
        return jsonify({'code': 403, 'msg': '无权限'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    pagination = OperationLog.query.order_by(OperationLog.created_at.desc()).paginate(page=page, per_page=per_page)
    return jsonify({
        'code': 200,
        'data': {
            'items': [l.to_dict() for l in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        }
    })

@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    if not check_admin(int(get_jwt_identity())):
        return jsonify({'code': 403, 'msg': '无权限'}), 403
    
    total_users = User.query.count()
    total_doctors = User.query.filter_by(role='doctor').count()
    total_patients = User.query.filter_by(role='patient').count()
    total_diagnoses = Diagnosis.query.count()
    benign_count = Diagnosis.query.filter_by(ai_result='benign').count()
    malignant_count = Diagnosis.query.filter_by(ai_result='malignant').count()
    
    return jsonify({
        'code': 200,
        'data': {
            'total_users': total_users,
            'total_doctors': total_doctors,
            'total_patients': total_patients,
            'total_diagnoses': total_diagnoses,
            'benign_count': benign_count,
            'malignant_count': malignant_count
        }
    })
