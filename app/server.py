
"""
Main module of the server file

 - virtualenv --python=/usr/local/Cellar/python@2/2.7.16/bin/python --clear  --always-copy --no-wheel --no-pip --no-setuptools --no-download venv
 - pip install -t venv/lib -r requirements.txt
 - source venv/bin/activate
 - redis-server --daemonize yes

"""
#from google.appengine.ext import vendor
#vendor.add("lib")
# 3rd party modules

from flask import render_template, redirect, Response, url_for, request

from models import User
from form import LoginForm, RegisterForm
# Local modules
import config, json
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_required, login_user, current_user
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, validators,PasswordField
from tokens import generate_confirmation_token, confirm_token, pool_hasher, referral_hasher


# Get the application instance
connex_app = config.connex_app

bcrypt = Bcrypt(connex_app.app)
login_manager = LoginManager()
login_manager.init_app(connex_app.app)
login_manager.login_view = "home"


# Read the swagger.yml file to configure the endpoints
connex_app.add_api("swagger.yml")

def confirm_required(func):
    def wrapper():
        #print 'current user_status: %s' % str(current_user.user_status)
        if current_user.user_status == 0:
            return redirect("/confirm", code=302)
        func()
    return wrapper

@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)

# Create a URL route in our application for "/"
@connex_app.route("/")
def home():
    """
    This function just responds to the browser URL
    localhost:5000/

    :return:        the rendered template "home.html"
    """
    login_form = LoginForm()
    register_form = RegisterForm()
    return render_template("home.html",login_form=login_form,register_form=register_form)

@login_manager.unauthorized_handler
def unauthorized():
    return redirect("/home", code=302)

@connex_app.route("/login",methods=["GET","POST"])
def login():
   form = LoginForm(request.form)
   print json.dumps(request.form,indent=4)

   if form.validate_on_submit():
       print 'form validated'
       user_email = request.form['user_email'].encode('utf-8')
       user_password = request.form['user_password'].encode('utf-8')
       user = User.query.filter(User.user_email == user_email).one_or_none()
       #user = config.db.session.query(User).filter_by(user_email=user_email).first()
       print 'email: %s user: %s' % (str(user_email),str(user))
       if user:
           print 'user found: %s' % user
           if bcrypt.check_password_hash(user.user_password, user_password):
               user.authenticated = True
               user.user_is_authenticated = True
               config.db.session.add(user)
               config.db.session.commit()
               login_user(user, remember=True)
               return Response("Login success", 200)
           else:
               return Response("Username / password incorrect", 401)
       else:
           return Response("Username / password incorrect", 401)

   else:
       print 'form not validated!!'
       print form.errors
       return Response("Authentication failed!", 498)


@connex_app.route("/register", methods=["GET","POST"])
def register():

    form = RegisterForm()
    print json.dumps(request.form, indent=4)

    print 'validating form'
    if form.validate_on_submit():
        print 'form validated'

        if  'user_email' not in request.form or \
            'user_password' not in request.form or \
            'user_name' not in request.form or \
            'user_timezone' not in request.form or \
            'user_name' not in request.form:
            return Response("Please make all the fields are filled", 409)


        user_email = request.form['user_email'].encode('utf-8')
        user_password = request.form['user_password'].encode('utf-8')
        user_name = request.form['user_name'].encode('utf-8')
        user_fingerprint = request.form['user_fingerprint'].encode('utf-8')
        user_ip_address = request.form['user_ip_address'].encode('utf-8')
        user_country = request.form['user_country'].encode('utf-8')
        user_region = request.form['user_region'].encode('utf-8')
        user_city = request.form['user_city'].encode('utf-8')
        user_register_timezone = request.form['user_timezone'].encode('utf-8')

        user = User.query.filter(User.user_email == user_email).one_or_none()

        if user:
            return Response("Account with that email address exists", 409)

        user = User.query.filter(User.user_name == user_name).one_or_none()

        if user:
            return Response("Account with that username exists", 409)

        user = User(
            user_name=user_name,
            user_email=user_email,
            user_password=bcrypt.generate_password_hash(user_password),
            user_fingerprint=user_fingerprint,
            user_register_ip = user_ip_address,
            user_last_ip = user_ip_address,
            user_is_authenticated = True,
            user_register_country = user_country,
            user_register_region =user_region,
            user_register_city = user_city,
            user_register_timezone = user_register_timezone,

        )
        config.db.session.add(user)
        config.db.session.commit()
        login_user(user, remember=True)
        user.user_referral_code = referral_hasher(user.user_id)
        print 'user ID: %s user_referral_code: %s' % (str(user.user_id),user.user_referral_code)
        config.db.session.add(user)
        config.db.session.commit()
        return Response("Login success", 200)
    else:
        print 'form not validated!!'
        print form.errors
        if 'csrf_token' in form.errors:
            return Response("Session expired, please refresh", 498)
        if 'user_password' in form.errors:
            return Response("Password must be at least 6 characters in length ", 498)
        if 'user_email' in form.errors:
            return Response("Must provide a valid email address", 498)

        else:
            return Response("Authentication failed!", 498)


@connex_app.route("/logout",methods=["GET","POST"])
def logout():
    return redirect("/home", code=302)


@connex_app.route("/game")
@login_required
@confirm_required
def game_home():
    print 'current user: %s ' % current_user
    return render_template("game.html",user=current_user)

# Create a URL route in our application for "/people"
@connex_app.route("/user")
@connex_app.route("/user/<int:user_id>")
def user(user_id=""):
    """
    This function just responds to the browser URL
    localhost:5000/people

    :return:        the rendered template "people.html"
    """
    pass

# Create a URL route to the notes page
@connex_app.route("/transaction")
@connex_app.route("/transactions")
@connex_app.route("/transaction/<int:transaction_id>")
def transaction(transaction_id=""):
    """
    This function responds to the browser URL
    localhost:5000/notes/<person_id>

    :param person_id:   Id of the person to show notes for
    :return:            the rendered template "notes.html"
    """
    pass

if __name__ == "__main__":
    connex_app.run(debug=True)
