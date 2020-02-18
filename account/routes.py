from flask import Blueprint, request
from flask_login import logout_user, login_required, current_user


account = Blueprint('account', __name__)


@account.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
        return {'status': 'Success logout'}
    return {'status': 'You are not authenticated'}


@account.route('/', methods=['GET', 'POST'])
@login_required
def account_page():
    if request.method == 'GET':
        return current_user.to_dict()
    data = request.get_json()
    current_user.update_user_info(data)
    return current_user.to_dict()
