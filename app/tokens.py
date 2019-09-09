from itsdangerous import URLSafeTimedSerializer
from config import app
from hashids import Hashids


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=86400): #give the usere 24 hours
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email

def pool_hasher(text):
    hasher = Hashids(min_length=7,alphabet='1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ',salt=app.config['SECRET_KEY'])
    return hasher.encode(text)

def referral_hasher(text):
    hasher = Hashids(min_length=5,alphabet='1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ',salt=app.config['SECRET_KEY'])
    return hasher.encode(text)