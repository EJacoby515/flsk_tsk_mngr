from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from datetime import datetime, timezone
from sqlalchemy import Identity

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.String(50), primary_key = True)
    email = db.Column(db.String(100), unique = True, nullable = False)
    firstname = db.Column(db.String(50), nullable = False)
    lastname = db.Column(db.String(50), nullable = False)
    birthdate = db.Column(db.Date, nullable = True)


    def __repr__(self):
        return f'<User{self.email}>'
    
from datetime import datetime, timezone

class Task(db.Model):
    id = db.Column(db.Integer, Identity(start=1, cycle=True), primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(10), nullable=False,  default='medium')
    status = db.Column(db.String(20), nullable=False, default='open')
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    modified_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    AI_Arranged = db.Column(db.Integer, nullable=False, default=0)


class TaskSchema(Schema):
    id = fields.Int()
    user_id = fields.Str()
    title = fields.Str()
    description = fields.Str()
    priority = fields.Str()
    status = fields.Str()
    created_at = fields.DateTime()
    modified_at = fields.DateTime()
    AI_Arranged = fields.Int()


    def __repr__(self):
        return f'<Task {self.title}>'

task_schema =TaskSchema()