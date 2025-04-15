from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    aveum_email = db.Column(db.String(120))
    aveum_password = db.Column(db.String(120))
    aveum_token = db.Column(db.String(500))
    device_id = db.Column(db.String(50))
    device_model = db.Column(db.String(50))
    platform_version = db.Column(db.String(10))
    mining_active = db.Column(db.Boolean, default=False)
    auto_like_active = db.Column(db.Boolean, default=False)
    last_mining_time = db.Column(db.DateTime)
    total_likes = db.Column(db.Integer, default=0)
    total_rewards = db.Column(db.Float, default=0.0)
    balance = db.Column(db.Float, default=0.0)
    last_login_time = db.Column(db.DateTime)
    last_activity_log = db.Column(db.Text)
    is_mining = db.Column(db.Boolean, default=False)
    # New fields for enhanced tracking
    mining_start_time = db.Column(db.DateTime)
    mining_end_time = db.Column(db.DateTime)
    mining_sessions_completed = db.Column(db.Integer, default=0)
    last_like_time = db.Column(db.DateTime)
    daily_likes = db.Column(db.Integer, default=0)
    daily_rewards = db.Column(db.Float, default=0.0)
    last_reward_claim_time = db.Column(db.DateTime)
    mining_errors = db.Column(db.Integer, default=0)
    like_errors = db.Column(db.Integer, default=0)
    is_banned = db.Column(db.Boolean, default=False)
    last_ban_check_time = db.Column(db.DateTime)