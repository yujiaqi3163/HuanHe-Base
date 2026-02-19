from flask import Blueprint, render_template
from app.models import User, RegisterSecret

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    users = User.query.all()
    register_secrets = RegisterSecret.query.all()
    return render_template('index.html', users=users, register_secrets=register_secrets)
