from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash
from sqlalchemy import create_engine, text
from urllib.parse import urlparse, urlunparse

app = create_app()

# 先创建数据库（如果不存在），再建表
with app.app_context():
    uri = app.config['SQLALCHEMY_DATABASE_URI']
    parsed = urlparse(uri)
    db_name = parsed.path.lstrip('/')
    base_uri = urlunparse((parsed.scheme, parsed.netloc, '', '', '', ''))

    engine = create_engine(base_uri)
    with engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{db_name}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
        conn.commit()
    engine.dispose()
    print(f'数据库 {db_name} 已就绪')

    db.create_all()
    print('数据库表已就绪')

    admin = User.query.filter_by(username='admin').first()
    if admin:
        print(f'管理员账户已存在: {admin.username}')
    else:
        admin = User(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            real_name='系统管理员'
        )
        db.session.add(admin)
        db.session.commit()
        print('默认管理员已创建: admin / admin123')

if __name__ == '__main__':
    # 预加载AI模型（在reloader子进程中执行，避免请求时加载导致崩溃）
    import os
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
        from app.services.ai_service import load_model
        load_model()
    app.run(debug=True, host='0.0.0.0', port=5000)
