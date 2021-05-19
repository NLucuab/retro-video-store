from flask import current_app
from app import db
from sqlalchemy import DateTime
from .customer import Customer

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    release_date = db.Column(db.DateTime, nullable=True)
    total_inventory = db.Column(db.Integer)
    available_invenotry = db.Column(db.Integer)