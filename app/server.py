
"""
Main module of the server file

 Setup
 - virtualenv --python=/usr/local/Cellar/python@2/2.7.16/bin/python --clear  --always-copy --no-wheel --no-pip --no-setuptools --no-download venv
 - pip install -t venv/lib -r requirements.txt

 Running
 - source venv/bin/activate
 - redis-server --daemonize yes
 - python server.py
"""


from flask import render_template, redirect, Response, url_for, request
from gmail import Gmail
from models import User
from form import LoginForm, RegisterForm, ConfirmationForm
# Local modules
import config, json
from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_required, login_user, current_user

from tokens import generate_confirmation_token, confirm_token, pool_hasher, referral_hasher


# Get the application instance
connex_app = config.connex_app

bcrypt = Bcrypt(connex_app.app)
login_manager = LoginManager()
login_manager.init_app(connex_app.app)
login_manager.login_view = "home"


# Read the swagger.yml file to configure the endpoints
connex_app.add_api("swagger.yml")


# def confirm_required(func):
#     print '### confirm_required()'
#     print 'current_user: %s' % str(current_user)
#
#
#     def wrapper_confirm_required(*args, **kwargs):
#
#         return func(*args, **kwargs)
#
#     return wrapper_confirm_required

@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)

# Create a URL route in our application for "/"
@connex_app.route("/")
@connex_app.route("/home")
def home():
    """
    This function just responds to the browser URL
    localhost:5000/

    :return:        the rendered template "home.html"
    """
    login_form = LoginForm()
    register_form = RegisterForm()
    return render_template("home.html", login_form=login_form, register_form=register_form)


def send_confirmation(user_email=None):
    print 'sending email confirmation'
    if user_email is None:
        print 'Email not provided for send_confirmation()'
        Response("Email address not provided", 200)



    token = generate_confirmation_token(user_email)
    url = "http://0.0.0.0:5000/confirm?confirm_token=%s&user_email=%s" % (token,user_email)
    gmail = Gmail(gmail_user="***********@gmail.com",gmail_password="*********!")
    gmail.mail_from_name = "Crypto Bot"
    gmail.mail_from = "***********@gmail.com"
    gmail.mail_subject = "Please confirm your account"
    gmail.mail_to = user_email
    gmail.mail_body = "<strong>Thank you for signing up with **************</strong><br>Click the URL below to activate your account <a href='%s'>%s</a>" % (url,url)
    gmail.send()

@connex_app.route("/confirm", methods=["GET","POST"])
def confirm():

    form = ConfirmationForm(request.form)
    print json.dumps(request.form, indent=4)

    if form.validate_on_submit():
        print 'form validated'
        user_email = request.form['user_email'].encode('utf-8')
        user_confirmation_code = request.form['user_confirmation_code'].encode('utf-8')
        user = User.query.filter(User.user_email == user_email).one_or_none()

        is_valid = confirm_token(user_confirmation_code)
        print 'is_valid: %s' % str(is_valid)
        if not is_valid:
            return Response("Token is invalid or has expired. Please request another.", 401)

        if user:
            print 'is User! Setting status!'
            user.user_status = 1
            user.user_tlogin = datetime.utcnow()
            user.user_tconfirm = datetime.utcnow()
            config.db.session.add(user)
            config.db.session.commit()
            return Response("User email is confirmed", 200)
        else:
            return Response("Invalid email, please register", 401)


    else:
        return render_template("confirm.html", confirmation_form=form)


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


@connex_app.route("/register", methods=["GET", "POST"])
def register():

    form = RegisterForm()
    print 'FORM SUBMIT DATA: %s' % json.dumps(request.form, indent=4)

    print 'validating form'
    if form.validate_on_submit():
        print 'form validated'

        if 'user_email' not in request.form or \
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
            user_register_ip=user_ip_address,
            user_last_ip=user_ip_address,
            user_is_authenticated=True,
            user_register_country=user_country,
            user_register_region=user_region,
            user_register_city=user_city,
            user_register_timezone=user_register_timezone,

        )
        config.db.session.add(user)
        config.db.session.commit()
        login_user(user, remember=True)
        user.user_referral_code = referral_hasher(user.user_id)
        print 'user ID: %s user_referral_code: %s' % (str(user.user_id),user.user_referral_code)
        config.db.session.add(user)
        config.db.session.commit()
        send_confirmation(user.user_email)
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


@login_required
@connex_app.route("/game")
def game_home():
    try:
        if current_user.user_status == 0:
            return redirect("/confirm", code=302)
    except Exception:
        pass
    print 'current user: %s ' % current_user
    return render_template("game.html", user=current_user)

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
    connex_app.run(host='0.0.0.0',debug=True)
