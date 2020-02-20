from flask_dance.contrib.github import make_github_blueprint
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer import oauth_authorized
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from sqlalchemy.orm.exc import NoResultFound
from webapp import db
from auth.models import OAuth, User
from flask_login import login_user, current_user
from flask import url_for, redirect, flash
from flask_dance import OAuth2ConsumerBlueprint

github_bp = make_github_blueprint(
    client_id='...',
    client_secret='...',
    storage=SQLAlchemyStorage(OAuth, db.session, user=current_user)
)

google_bp = make_google_blueprint(
    client_id='...',
    client_secret='...',
    storage=SQLAlchemyStorage(OAuth, db.session, user=current_user)
)

yandex_bp = OAuth2ConsumerBlueprint(
    "yandex", __name__,
    client_id="...",
    client_secret="...",
    base_url="...",
    token_url="...",
    authorization_url="...",
)


@oauth_authorized.connect
def logged_in(blueprint, token):
    if not token:
        flash("Failed to log in with OAuth.", category="error")
        return False
    if blueprint.name == 'google':
        resp = google.get('/oauth2/v1/userinfo')
    elif blueprint.name == 'github':
        resp = blueprint.session.get("/user")
    else:
        resp = blueprint.session.get("/info")
    if not resp.ok:
        msg = "Failed to fetch user info from Provider."
        flash(msg, category="error")
        return False

    info = resp.json()
    print(info)
    user_id = str(info["id"])

    query = OAuth.query.filter_by(
        Provider=blueprint.name,
        Provider_user_id=user_id,
    )
    try:
        oauth = query.one()
    except NoResultFound:
        oauth = OAuth(
            Provider=blueprint.name,
            Provider_user_id=user_id,
            Token=str(token),
        )

    if oauth.User:
        login_user(oauth.User)
        flash("Successfully signed in with GitHub.")

    else:
        user = User(
            Email=info.get('email', None) if info.get('email', None) else info.get('default_email'),
            Name=info["name"] if info.get('name') else info.get('real_name')
        )
        oauth.User = user
        db.session.add_all([user, oauth])
        db.session.commit()
        login_user(user)
        flash("Successfully signed in with GitHub.")

    return False


@oauth_authorized.connect
def redirect_to_next_url(blueprint, token):
    next_url = url_for('shop.main_links')
    return redirect(next_url)
