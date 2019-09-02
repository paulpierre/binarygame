from wtforms import BooleanField, StringField, validators,PasswordField
from flask_wtf import FlaskForm


class LoginForm(FlaskForm):
    user_email = StringField("User email", [validators.Length(min=4, max=50)],render_kw={"placeholder": "Email address"})
    user_password = PasswordField("User password", [validators.Length(min=6, max=50)],render_kw={"placeholder": "Password"})
\
class RegisterForm(FlaskForm):
    user_email = StringField("User email", [validators.Email(),validators.Length(min=4, max=50)],render_kw={"placeholder": "Email address"})
    user_password = PasswordField("User password", [validators.Length(min=6, max=50)],render_kw={"placeholder": "Password"})
    user_name = StringField("Username", [validators.Length(min=4, max=50)],render_kw={"placeholder": "Username (unique)"})


