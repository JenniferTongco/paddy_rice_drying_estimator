from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    first_name = db.Column(db.String(150), nullable=False)

    records = db.relationship('DryingRecord', backref='user', lazy=True)


class DryingRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())
    
    # Sensor and drying input values
    initial_weight = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    sensor_value = db.Column(db.Float, nullable=False)
    initial_moisture = db.Column(db.Float, nullable=False)
    final_moisture = db.Column(db.Float, nullable=False)
    
    # Prediction results
    drying_time = db.Column(db.String(10), nullable=False) 
    final_weight = db.Column(db.Float, nullable=False)

    # Relationship
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Crop cycle dates
    date_planted = db.Column(db.Date)
    date_harvested = db.Column(db.Date)
    date_dried = db.Column(db.Date)
