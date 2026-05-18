from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('doctor', 'patient', 'admin'), nullable=False, default='patient')
    real_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'real_name': self.real_name,
            'phone': self.phone,
            'email': self.email,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'is_active': self.is_active
        }

class Patient(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    gender = db.Column(db.Enum('male', 'female'))
    age = db.Column(db.Integer)
    medical_history = db.Column(db.Text)

class Diagnosis(db.Model):
    __tablename__ = 'diagnoses'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    image_path = db.Column(db.String(500), nullable=False)
    result_image_path = db.Column(db.String(500))
    ai_result = db.Column(db.Enum('benign', 'malignant'))
    ai_confidence = db.Column(db.Float)
    bbox_x = db.Column(db.Integer)
    bbox_y = db.Column(db.Integer)
    bbox_w = db.Column(db.Integer)
    bbox_h = db.Column(db.Integer)
    doctor_opinion = db.Column(db.Text)
    risk_level = db.Column(db.Enum('low', 'medium', 'high'))
    status = db.Column(db.Enum('pending', 'completed', 'reviewed'), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    patient = db.relationship('User', foreign_keys=[patient_id], backref='patient_diagnoses')
    doctor = db.relationship('User', foreign_keys=[doctor_id], backref='doctor_diagnoses')

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'image_path': self.image_path,
            'result_image_path': self.result_image_path,
            'ai_result': self.ai_result,
            'ai_confidence': self.ai_confidence,
            'bbox': {'x': self.bbox_x, 'y': self.bbox_y, 'w': self.bbox_w, 'h': self.bbox_h},
            'doctor_opinion': self.doctor_opinion,
            'risk_level': self.risk_level,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'patient_name': self.patient.real_name if self.patient else None,
            'doctor_name': self.doctor.real_name if self.doctor else None
        }

class OperationLog(db.Model):
    __tablename__ = 'operation_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False)
    detail = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.now)

    user = db.relationship('User', backref='logs')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'action': self.action,
            'detail': self.detail,
            'ip_address': self.ip_address,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
