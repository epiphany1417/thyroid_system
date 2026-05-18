from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app import db
from app.models import User, Diagnosis, OperationLog
import os, uuid

patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/diagnoses', methods=['GET'])
@jwt_required()
def get_my_diagnoses():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if user.role != 'patient':
        return jsonify({'code': 403, 'msg': '无权限'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pagination = Diagnosis.query.filter_by(patient_id=user_id)\
        .order_by(Diagnosis.created_at.desc()).paginate(page=page, per_page=per_page)
    
    return jsonify({
        'code': 200,
        'data': {
            'items': [d.to_dict() for d in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        }
    })

@patient_bp.route('/diagnoses/<int:diag_id>', methods=['GET'])
@jwt_required()
def get_diagnosis_detail(diag_id):
    user_id = int(get_jwt_identity())
    diagnosis = Diagnosis.query.get_or_404(diag_id)
    if diagnosis.patient_id != user_id:
        return jsonify({'code': 403, 'msg': '无权查看'}), 403
    
    # 添加简单解释
    data = diagnosis.to_dict()
    if diagnosis.risk_level == 'high':
        data['explanation'] = '风险较高，建议尽快就医进一步检查'
    elif diagnosis.risk_level == 'medium':
        data['explanation'] = '存在一定风险，建议定期复查'
    else:
        data['explanation'] = '风险较低，建议定期体检观察'
    
    return jsonify({'code': 200, 'data': data})

@patient_bp.route('/doctors', methods=['GET'])
@jwt_required()
def get_doctors():
    """获取可选医生列表"""
    doctors = User.query.filter_by(role='doctor', is_active=True).all()
    return jsonify({'code': 200, 'data': [{'id': d.id, 'real_name': d.real_name or d.username} for d in doctors]})

@patient_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_self_image():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if user.role != 'patient':
        return jsonify({'code': 403, 'msg': '无权限'}), 403

    doctor_id = request.form.get('doctor_id', type=int)
    if not doctor_id:
        return jsonify({'code': 400, 'msg': '请选择医生'}), 400

    if 'image' not in request.files:
        return jsonify({'code': 400, 'msg': '未上传图像'}), 400

    file = request.files['image']
    allowed = {'png', 'jpg', 'jpeg'}
    if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed):
        return jsonify({'code': 400, 'msg': '不支持的文件格式'}), 400

    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    diagnosis = Diagnosis(
        patient_id=user_id,
        doctor_id=doctor_id,
        image_path=filename,
        status='pending'
    )
    db.session.add(diagnosis)
    db.session.commit()

    return jsonify({'code': 200, 'msg': '图像上传成功，请等待医生诊断', 'data': diagnosis.to_dict()})
