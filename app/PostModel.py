# PostModel.py
from app import db

class Post(db.Model):
    __tablename__ = 'posts'
    post_id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    translated_content = db.Column(db.Text)
    status = db.Column(db.String(50), nullable=False)
