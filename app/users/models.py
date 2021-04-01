from sqlalchemy.dialects.postgresql import UUID
from app.mixin import ModelMixin
import uuid 
from app import db

class User(db.Model, ModelMixin):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True)
    real_name = db.Column(db.String(360))
    date_of_birth = db.Column(db.String(50))
    password_hash = db.Column(db.String(128))
    token = db.Column(db.String(32), index=True, unique=True)
    roles = db.relationship('Role', secondary='user_roles',
                backref=db.backref('user', lazy='dynamic'))

class Role(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class UserRoles(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = db.Column(UUID(as_uuid=True),  db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(UUID(as_uuid=True),  db.ForeignKey('role.id',  ondelete='CASCADE'))