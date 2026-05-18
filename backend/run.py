from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

# 初始化数据库和默认管理员
with app.app_context():
    db.create_all()
    # 创建默认管理员
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            real_name='系统管理员'
        )
        db.session.add(admin)
        db.session.commit()
        print('默认管理员已创建: admin/admin123')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
