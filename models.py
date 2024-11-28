from datetime import datetime
from pytz import timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from db import db


class User (UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Problem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    languages = db.Column(db.String(150), nullable=False)
    forbidden_words = db.Column(db.String(150), nullable=True)
    recursive = db.Column(db.Boolean, nullable=False)
    input_params = db.Column(db.Text, nullable=False)
    output_type = db.Column(db.String(50), nullable=False)
    examples = db.Column(db.Text, nullable=False)
    test_cases = db.Column(db.Text, nullable=False)


class Solution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    problem_id = db.Column(db.Integer, db.ForeignKey(
        'problem.id'), nullable=False)
    code = db.Column(db.Text, nullable=False)
    result = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User', backref=db.backref('solutions', lazy=True))
    problem = db.relationship(
        'Problem', backref=db.backref('solutions', lazy=True))

    def __init__(self, **kwargs):
        super(Solution, self).__init__(**kwargs)
        local_tz = timezone('America/Bogota')
        current_time = datetime.now(local_tz)
        # Format time as HH:MM:SS
        self.timestamp = current_time.replace(
            tzinfo=None).replace(microsecond=0)
