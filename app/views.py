from flask import (render_template, flash, redirect, url_for, g, jsonify,
                   session)
from flask.ext.login import request, login_required
from flask.ext.security import (Security, SQLAlchemyUserDatastore,
                                UserMixin, RoleMixin, roles_required,
                                login_user, logout_user, current_user)
from . import lm, app, user_datastore, security, db
from .forms import LoginForm, RegisterForm
from .models import User, Tickets
from .auth import OAuthSignIn
from datetime import datetime
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
@login_required
def index():
    """Handles calls to / and /index, return the panel"""

    print("Index:CurrentUser:\t", current_user)

    return render_template(
        "index.html",
        form=LoginForm(),
        username=session["username"],
        role="pro"
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
    user_id, username, email = oauth.callback()
    session["user_id"] = user_id
    session["username"] = username
    session["email"] = email
    session["provider"] = provider

    if user_id is None:
        flash("OAuth Authentication failed :( Please try again later!")
        return redirect(url_for("index"))
    user = User.query.filter_by(provider_id="{}${}".format(provider,
                                                           user_id)).first()
    if not user:
        # User doesn't exist yet, so we'll create it, then redirect to index
        registered, e = register()
        if register:
            return redirect(url_for("index"))
        else:
            # TODO: Make this redirect to an error page
            return jsonify({"error": 3, "data": jsonify(e.args)})

    else:
        # User exists, so login and redirect to index
        login_user(user, True)
        return redirect(url_for("index"))


def register():
    try:
        user_role = user_datastore.find_or_create_role("user")
        user = user_datastore.create_user(
            username=session["username"],
            password="",  # None, because it's required for
                          # Flask-Login's auth key setup
            email=session["email"],
            confirmed_at=datetime.now(),
            roles=[user_role, ],
            provider_id="{pid}${uid}".format(pid=session["provider"],
                                             uid=session["user_id"]),
            active=True     # Mark them as active so they're logged in
            )

        user = User.query.filter_by(
            provider_id="{}${}".format(session["provider"],
                                       session["user_id"])
            ).first()

        db.session.commit()

        if user is not None:
            login_user(user, True)
            return True, None
        else:
            return False, None
    except Exception as e:
        return False, e


@app.route("/login")
def login():
    return oauth_authorize("beam")


@app.route("/logout", methods=["GET"])
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route('/admin', methods=["GET"])
@login_required
def admin():
    return render_template('admin.html')


@app.route('/support/create', methods=["GET", "POST"])
def create_ticket():
    if request.method == "GET":
        return render_template('directives/CreateSupportTicket.html')
    elif request.method == "POST":
        data = json.loads(request.data.decode("utf-8"))

        ticket_id = str(uuid4())

        new_ticker = Tickets(
                        who=session["username"],
                        issue=data["issue"],
                        details=data["details"],
                        ticket_id=ticket_id
                        )
        db.session.add(new_ticker)
        db.session.commit()

        ticket = Tickets.query.filter_by(ticket_id=ticket_id).first()

        if ticket is not None:
            print(ticket)

            return jsonify({"success": True})
        else:
            return jsonify({"success": False})
    else:
        return "Method not supported."


@app.route('/support/respond', methods=["GET", "POST"])
def ticket_response():
    if request.method == "GET":
        return render_template('directives/RespondToTicket.html')
    elif request.method == "POST":
        return "THINGS! #BlamePara"
    else:
        return "Method not supported."


@app.route('/c-emoji', methods=["GET"])
def emoji():
    return render_template('directives/c-emoji.html')


@app.route('/command/create')
def create_command():
    return render_template(
        'directives/AddCommand.html',
        username=session["username"],
        role="pro")


@app.route('/tab/dash')
def dash():
    return render_template(
        'directives/tabs/Dashboard.html',
        username=session["username"],
        role="pro")


@app.route('/tab/commands')
def commands():
    return render_template(
        'directives/tabs/Commands.html',
        username=session["username"],
        role="pro")


@app.route('/tab/botsettings')
def bot_settings():
    return render_template(
        'directives/tabs/BotSettings.html',
        username=session["username"],
        role="pro")


@app.route('/tab/support')
def support():
    return render_template(
        'directives/tabs/Support.html',
        username=session["username"],
        role="pro")


@app.route('/tab/usersettings')
def user_settings():
    return render_template(
        'directives/tabs/UserSettings.html',
        username=session["username"],
        role="pro")
