from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app import db
from app.models import User, Diagnosis, OperationLog
from app.services.ai_service import analyze_image
from app.services.llm_service import generate_diagnosis_opinion
import os, uuid

doctor_bp = Blueprint('doctor', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@doctor_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_image():
    """医生主动上传图像，只保存不诊断"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if user.role != 'doctor':
        return jsonify({'code': 403, 'msg': '无权限'}), 403

    if 'image' not in request.files:
        return jsonify({'code': 400, 'msg': '未上传图像'}), 400

    file = request.files['image']
    patient_id = request.form.get('patient_id')

    if not patient_id:
        return jsonify({'code': 400, 'msg': '请指定患者'}), 400

    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        diagnosis = Diagnosis(
            patient_id=int(patient_id),
            doctor_id=user_id,
            image_path=filename,
            status='pending'
        )
        db.session.add(diagnosis)
        db.session.commit()

        return jsonify({'code': 200, 'msg': '图像上传成功', 'data': diagnosis.to_dict()})

    return jsonify({'code': 400, 'msg': '不支持的文件格式'}), 400

@doctor_bp.route('/pending', methods=['GET'])
@jwt_required()
def get_pending_diagnoses():
    """获取分配给当前医生的待诊断记录"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if user.role != 'doctor':
        return jsonify({'code': 403, 'msg': '无权限'}), 403

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    pagination = Diagnosis.query.filter_by(doctor_id=user_id, status='pending')\
        .order_by(Diagnosis.created_at.desc()).paginate(page=page, per_page=per_page)

    return jsonify({
        'code': 200,
        'data': {
            'items': [d.to_dict() for d in pagination.items],
            'total': pagination.total
        }
    })

@doctor_bp.route('/diagnose/<int:diag_id>', methods=['POST'])
@jwt_required()
def run_ai_diagnose(diag_id):
    """对记录执行AI诊断（只保存AI结果，不改状态）"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if user.role != 'doctor':
        return jsonify({'code': 403, 'msg': '无权限'}), 403

    diagnosis = Diagnosis.query.get_or_404(diag_id)
    if diagnosis.doctor_id != user_id:
        return jsonify({'code': 403, 'msg': '该记录未分配给您'}), 403

    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], diagnosis.image_path)
    if not os.path.exists(filepath):
        return jsonify({'code': 404, 'msg': '图像文件不存在'}), 404

    result = analyze_image(filepath, current_app.config['UPLOAD_FOLDER'])
    if not result['success']:
        return jsonify({'code': 500, 'msg': 'AI分析失败: ' + result.get('error', '')}), 500

    diagnosis.result_image_path = result['result_image']
    diagnosis.ai_result = result['ai_result']
    diagnosis.ai_confidence = result['ai_confidence']
    diagnosis.bbox_x = result['bbox']['x']
    diagnosis.bbox_y = result['bbox']['y']
    diagnosis.bbox_w = result['bbox']['w']
    diagnosis.bbox_h = result['bbox']['h']
    diagnosis.risk_level = result['risk_level']

    # 调用大模型生成诊断参考意见（不阻塞主流程）
    ai_opinion = generate_diagnosis_opinion(
        ai_result=result['ai_result'],
        ai_confidence=result['ai_confidence'],
        risk_level=result['risk_level'],
        bbox=result['bbox'],
        config=current_app.config
    )
    if ai_opinion:
        diagnosis.ai_opinion = ai_opinion

    db.session.commit()

    return jsonify({'code': 200, 'msg': 'AI诊断完成', 'data': diagnosis.to_dict()})

@doctor_bp.route('/diagnose/<int:diag_id>/submit', methods=['POST'])
@jwt_required()
def submit_diagnose(diag_id):
    """医生提交诊断意见，完成诊断"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if user.role != 'doctor':
        return jsonify({'code': 403, 'msg': '无权限'}), 403

    diagnosis = Diagnosis.query.get_or_404(diag_id)
    if diagnosis.doctor_id != user_id:
        return jsonify({'code': 403, 'msg': '该记录未分配给您'}), 403

    data = request.get_json()
    opinion = data.get('opinion', '').strip()
    if not opinion:
        return jsonify({'code': 400, 'msg': '请输入诊断意见'}), 400

    diagnosis.doctor_opinion = opinion
    diagnosis.status = 'completed'

    log = OperationLog(user_id=user_id, action='submit_diagnose', detail=f'提交诊断记录ID:{diag_id}', ip_address=request.remote_addr)
    db.session.add(log)
    db.session.commit()

    return jsonify({'code': 200, 'msg': '诊断已提交', 'data': diagnosis.to_dict()})

@doctor_bp.route('/diagnoses', methods=['GET'])
@jwt_required()
def get_diagnoses():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if user.role != 'doctor':
        return jsonify({'code': 403, 'msg': '无权限'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    patient_id = request.args.get('patient_id', type=int)
    
    query = Diagnosis.query.filter_by(doctor_id=user_id)
    if patient_id:
        query = query.filter_by(patient_id=patient_id)
    
    pagination = query.order_by(Diagnosis.created_at.desc()).paginate(page=page, per_page=per_page)
    
    return jsonify({
        'code': 200,
        'data': {
            'items': [d.to_dict() for d in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        }
    })

@doctor_bp.route('/diagnoses/<int:diag_id>', methods=['GET'])
@jwt_required()
def get_diagnosis_detail(diag_id):
    user_id = int(get_jwt_identity())
    diagnosis = Diagnosis.query.get_or_404(diag_id)
    return jsonify({'code': 200, 'data': diagnosis.to_dict()})

@doctor_bp.route('/diagnoses/<int:diag_id>/opinion', methods=['PUT'])
@jwt_required()
def update_opinion(diag_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if user.role != 'doctor':
        return jsonify({'code': 403, 'msg': '无权限'}), 403
    
    diagnosis = Diagnosis.query.get_or_404(diag_id)
    data = request.get_json()
    diagnosis.doctor_opinion = data.get('opinion', '')
    diagnosis.status = 'reviewed'
    db.session.commit()
    
    return jsonify({'code': 200, 'msg': '意见已更新', 'data': diagnosis.to_dict()})

@doctor_bp.route('/diagnoses/<int:diag_id>/ai-result', methods=['PUT'])
@jwt_required()
def update_ai_result(diag_id):
    """医生修改AI诊断结果（良恶性分类和风险等级）"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if user.role != 'doctor':
        return jsonify({'code': 403, 'msg': '无权限'}), 403

    diagnosis = Diagnosis.query.get_or_404(diag_id)
    if diagnosis.doctor_id != user_id:
        return jsonify({'code': 403, 'msg': '该记录未分配给您'}), 403

    data = request.get_json()
    new_result = data.get('ai_result')
    new_risk = data.get('risk_level')

    if new_result and new_result not in ('benign', 'malignant'):
        return jsonify({'code': 400, 'msg': '无效的分类结果'}), 400
    if new_risk and new_risk not in ('low', 'medium', 'high'):
        return jsonify({'code': 400, 'msg': '无效的风险等级'}), 400

    # 首次修改时保存原始AI结果
    if diagnosis.original_ai_result is None:
        diagnosis.original_ai_result = diagnosis.ai_result
        diagnosis.original_risk_level = diagnosis.risk_level

    if new_result:
        diagnosis.ai_result = new_result
    if new_risk:
        diagnosis.risk_level = new_risk

    log = OperationLog(user_id=user_id, action='update_ai_result',
                       detail=f'修改诊断记录ID:{diag_id} AI结果: {new_result}, 风险等级: {new_risk}',
                       ip_address=request.remote_addr)
    db.session.add(log)
    db.session.commit()

    return jsonify({'code': 200, 'msg': 'AI结果已更新', 'data': diagnosis.to_dict()})


@doctor_bp.route('/patients', methods=['GET'])
@jwt_required()
def get_patients():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if user.role != 'doctor':
        return jsonify({'code': 403, 'msg': '无权限'}), 403
    
    patients = User.query.filter_by(role='patient', is_active=True).all()
    return jsonify({'code': 200, 'data': [p.to_dict() for p in patients]})

@doctor_bp.route('/image/<filename>')
def get_image(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
