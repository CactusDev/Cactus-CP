from flask import (render_template, flash, redirect, session, url_for, request,
                   g, jsonify, abort)
from flask.ext.login import (login_user, logout_user, current_user,
                             login_required)
from flask.ext.socketio import SocketIO, emit
from app import app, db, lm, socketio
from .forms import LoginForm, RegisterForm
from .models import User
from .auth import *
import json
from uuid import uuid4


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_request
def before_request():
    """Set the Flask session object's user to Flask-Login's current_user"""
    g.user = current_user


@app.route("/")
@app.route("/index")
def index():
    """Handles calls to / and /index, return the panel"""
    return render_template(
        "index.html",
        title="CactusPanel",
        form=LoginForm()
    )


@app.route("/authorize/<provider>")
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for("index"))

    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route("/callback/<provider>")
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for("index"))

    oauth = OAuthSignIn.get_provider(provider)
    user_id, username = oauth.callback()
    if user_id is None:
        flash("OAuth Authentication failed :(")
        return redirect(url_for("index"))
    user = User.query.filter_by(provider_id="{}${}".format(provider,
                                                           user_id)).first()
    if not user:
        # User does not exist, so redirect to registration page
        redirect(url_for("register"))
    else:
        login_user(user, True)
        return redirect(url_for("index"))


@app.route("/register")
def register():
    return "Not implemented yet!"


@app.route("/login")
def login():
    return oauth_authorize("beam")


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))
