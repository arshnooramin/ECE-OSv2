import os
from flask import Flask, flash, redirect, url_for
from . import db, auth, project, admin, order
from flask_login import LoginManager, current_user
from ordersys.user import User

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY"),
        DATABASE=os.path.join(app.instance_path, 'ordersdb.sqlite'),
    )

    lh = LoginManager()
    lh.init_app(app)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(project.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(order.bp)

    @lh.user_loader
    def load_user(user_id): 
        return User.get(user_id)
    
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            if current_user.is_admin(): # super user / admin
                return redirect(url_for('admin.index'))
            else:
                return redirect(url_for('project.index'))
        else:
            return redirect(url_for('auth.login'))
    
    @app.context_processor
    def utility_processor():
        def get_username(email):
            if email:
                return email.split('@')[0]
            else:
                return None
        return dict(get_username=get_username)

    return app