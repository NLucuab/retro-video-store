from flask import current_app
from app import db
from sqlalchemy import DateTime

class Customer(db.Model):
    customer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    postal_code = db.Column(db.String)
    phone = db.Column(db.String)
    registered_at = db.Column(db.DateTime)
    video_checked_out_count = db.Column(db.Integer, default=0)

    def to_json(self):
        return {
            "id": self.customer_id,
            "name": self.name,
            "postal_code": self.postal_code,
            "phone": self.phone,
            "registered_at": self.registered_at,
            "video_checked_out_count": self.video_checked_out_count
        }
