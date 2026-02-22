from datetime import datetime
from app import db


class TerminalSecret(db.Model):
    __tablename__ = 'terminal_secrets'

    id = db.Column(db.Integer, primary_key=True)
    secret = db.Column(db.String(100), unique=True, nullable=False, index=True)
    is_used = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)
    duration_type = db.Column(db.String(20), nullable=False, default='permanent')
    expires_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<TerminalSecret {self.secret}>'
