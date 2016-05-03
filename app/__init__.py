from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, request
from flask_socketio import SocketIO
from flask_wtf.csrf import CsrfProtect
from flask_mail import Mail
from flask_security import (Security, SQLAlchemyUserDatastore,
                            UserMixin, RoleMixin, login_required,
                            login_user, logout_user, current_user)

app = Flask(__name__, instance_relative_config=True)

app.config.from_object("config")
app.config.from_pyfile("config.py", True)

mail = Mail(app)
mail.init_app(app)

db = SQLAlchemy(app)

lm = LoginManager()

lm.init_app(app)
lm.login_view = "login"

csrf_protect = CsrfProtect(app)

socketio = SocketIO(app)

from . import models
from .util import assets

user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
security = Security(app, user_datastore)

from . import views
