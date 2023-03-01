import os
from dotenv import load_dotenv

from flask_login import UserMixin
from ordersys.db import get_db

class User(UserMixin):
    def __init__(self, id_, email, name, auth_level, project_id):
        self.id = id_
        self.email = email
        self.name = name
        self.auth_level = auth_level
        self.project_id = project_id
    
    def is_superuser(self):
        return self.email == os.environ.get('SUPER_USER_EMAIL')

    def is_admin(self):
        return self.auth_level == 0

    @staticmethod
    def get(param, param_type=0):
        db = get_db()
        if param_type == 0:
            user = db.execute(
                "SELECT * FROM user WHERE id = ?", (param,)
            ).fetchone()
        else:
            user = db.execute(
                "SELECT * FROM user WHERE email = ?", (param,)
            ).fetchone()
        if not user:
            return None

        user = User(
            id_=user["id"], 
            email=user["email"], 
            name=user["name"],
            auth_level=user["auth_level"],
            project_id=user["project_id"]
        )
        return user

    @staticmethod
    def create(id_, email, name, auth_level, project_id):
        db = get_db()
        db.execute(
            "INSERT INTO user (id, email, name, auth_level, project_id) "
            "VALUES (?, ?, ?, ?)",
            (id_, email, name, auth_level, project_id),
        )
        db.commit()
