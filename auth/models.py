from webapp import db, login
from flask_login import UserMixin,AnonymousUserMixin
from flask import current_app
from webapp import login

class OAuth(db.Model):
    Provider = db.Column(db.String(80), nullable=False, primary_key=True)
    Provider_user_id = db.Column(db.String(80), nullable=False, primary_key=True)
    Token = db.Column(db.String(80), nullable=False, primary_key=True)
    User_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    User = db.relationship('User', uselist=False)


class User(UserMixin, db.Model):
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.Email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
        if self.role is None:
            self.role = Role.query.filter_by(default=True).first()

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(80), nullable=False, unique=False)
    Email = db.Column(db.String(80), unique=True)
    Address = db.Column(db.String(300), unique=False, nullable=True)
    OAuth = db.relationship('OAuth', uselist=False)
    is_active = db.Column(db.Boolean, default=True)
    orders = db.relationship('Order', backref=db.backref('User', lazy='subquery'), lazy='dynamic')
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

    def to_dict(self):
        message = {'Name': self.Name,
                   'Email': self.Email,
                   'Address': self.Address, }
        return message

    def update_user_info(self, data):
        if data['Name']:
            self.Name = data['Name']
        if data['Address']:
            self.Address = data['Address']
        if data['Email']:
            self.Email = data['Email']
        db.session.add(self)
        db.session.commit()

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login.anonymous_user = AnonymousUser


class Permission:
    STAFF = 1
    ADD = 2
    REMOVE = 4
    UPDATE = 8
    ADMIN = 16


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    @staticmethod
    def insert_roles():
        roles = {
            'User': [],
            'Moderator': [Permission.STAFF, Permission.ADD,
                          Permission.UPDATE, Permission.REMOVE],
            'Administrator': [Permission.STAFF, Permission.ADD,
                              Permission.UPDATE, Permission.REMOVE,
                              Permission.ADMIN],
        }

        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
