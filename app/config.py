import os

import connexion
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

basedir = os.path.abspath(os.path.dirname(__file__))


# Create the connexion application instance
connex_app = connexion.App(__name__, specification_dir=basedir)

# Get the underlying Flask app instance
app = connex_app.app

# Build the Sqlite ULR for SqlAlchemy
mysql_url = "mysql+pymysql://root:00g4B00g4!@localhost/artemis"

# Configure the SqlAlchemy part of the app instance
app.config["SQLALCHEMY_ECHO"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = mysql_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["SECRET_KEY"] = "F8E41A071F501D0A193B7AAC866BE72331BDB039" #Sha1 00g4B00g4!2019
app.config["SECURITY_PASSWORD_SALT"] = "DD2EDB87EA9EB7A32FD4057276D3A1FAB861C1D5" #Sha1 fuckyou

# Create the SqlAlchemy db instance
db = SQLAlchemy(app)

# Initialize Marshmallow
ma = Marshmallow(app)
