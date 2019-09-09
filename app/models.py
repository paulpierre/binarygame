from datetime import datetime
from config import db, ma
from marshmallow import fields
from sqlalchemy.sql import func
#from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required

# class Role(db.Model, RoleMixin):
#     role_id = db.Column(db.Integer, primary_key=True)
#     role_name = db.Column(db.String(80), unique=True)
#     role_description = db.Column(db.String(255))
#
# class UserRoles(db.Model):
#     __tablename__ = "user_roles"
#     id = db.Column(db.Integer, primary_key=True)
#     role_id = db.Column(db.Integer,db.ForeignKey('role.role_id'))
#     user_id = db.Column(db.Integer,db.ForeignKey('user.user_id'))

class User(db.Model):
    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key=True)
    user_fingerprint = db.Column(db.String(100))
    user_email = db.Column(db.String(100),unique=True)
    user_password = db.Column(db.String(100))
    user_name_display = db.Column(db.String(255))
    user_name = db.Column(db.String(255),unique=True)
    user_avatar = db.Column(db.String(255))
    user_photo_id = db.Column(db.String(255))
    user_did_kyc = db.Column(db.Boolean)
    user_did_aml = db.Column(db.Boolean)
    user_status = db.Column(db.Integer, default=0) #0=unconfirmed 1=email_confirmed 2=validated (can trade) 3=suspended 4=hard ban
    user_wallet_address = db.Column(db.String(500),unique=True)
    user_wallet_address_eth = db.Column(db.String(500))
    user_wallet_address_btc = db.Column(db.String(500))
    user_wallet_address_xmr = db.Column(db.String(100))
    user_register_ip = db.Column(db.String(15))
    user_register_country = db.Column(db.String(255))
    user_register_region = db.Column(db.String(255))
    user_register_city = db.Column(db.String(255))
    user_register_timezone = db.Column(db.String(5))
    user_last_ip = db.Column(db.String(15))
    user_referral_code = db.Column(db.String(100),unique=True) # short hash of their email address
    user_tcreate = db.Column(db.DateTime(timezone=True), default=func.now())
    user_tmodified = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())
    user_tlogin = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())
    user_tconfirm = db.Column(db.DateTime(timezone=True), default=None)
    user_is_authenticated = db.Column(db.Boolean, default=False)

    # roles = db.relationship(
    #     "Role",
    #     secondary = "user_roles",
    #     backref = "user"
    # )

    pools = db.relationship(
        "Pool",
        backref="user",
        secondary="transaction",
        secondaryjoin="Transaction.user_id == User.user_id",
        primaryjoin="Pool.pool_hash == Transaction.pool_hash",
        order_by="desc(Pool.pool_tmodified)"
    )

    # Lets set the constants
    USER_UNCONFIRMED = 0
    USER_EMAIL_CONFIRMED = 1
    USER_VALIDATED = 2
    USER_SUSPENDED = 3
    USER_BANNED = 4

    # The following methods are for Flask-login

    #def __init__(self,):
    #    pass

    def is_active(self):
        return True

    def get_id(self):
        return self.user_id

    def is_authenticated(self):
        return self.user_is_authenticated

    def is_anonymous(self):
        return False


class Transaction(db.Model):
    __tablename__ = "transaction"
    transaction_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    pool_id = db.Column(db.Integer, db.ForeignKey("pool.pool_id"), nullable=True)
    pool_hash = db.Column(db.String(100), db.ForeignKey("pool.pool_hash"), nullable=True)
    transaction_amount_buy = db.Column(db.Float(precision=5,asdecimal=True),nullable=True)
    transaction_amount_sell = db.Column(db.Float(precision=5,asdecimal=True),nullable=True)
    transaction_is_deposit = db.Column(db.Boolean,nullable=True)
    transaction_wallet_to = db.Column(db.String(100), nullable=True)
    transaction_wallet_from = db.Column(db.String(100), nullable=True)
    transaction_status = db.Column(db.Integer, default=0)                   # Determines if this transaction is win/loss 0 = in progress 1 = win -1 = loss 2 = deposited
    transaction_tcreate = db.Column(db.DateTime(timezone=True), default=func.now())
    transaction_tmodified = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # pool = db.relationship(
    #     "Pool",
    #     backref="transaction",
    #     primaryjoin="Transaction.pool_id == Pool.pool_id",
    # )

    user = db.relationship(
        "User",
        backref="transaction",
        primaryjoin="Transaction.user_id == User.user_id",
    )

    # Transaction status
    TRANSACTION_IN_PROGRESS = 0
    TRANSACTION_POOL_WIN = 1
    TRANSACTION_POOL_LOSS = -1
    TRANSACTION_IS_DEPOSIT = 2
    TRANSACTION_CANCELLED = 3


class Pool(db.Model):
    __tablename__ = "pool"
    pool_id = db.Column(db.Integer, primary_key=True)
    pool_hash = db.Column(db.String(100), nullable=False, unique=True)
    pool_pair = db.Column(db.String(10), nullable=False)
    pool_timeframe = db.Column(db.String(10), nullable=False)
    pool_locked_price = db.Column(db.Float(precision=2,asdecimal=True),nullable=False)
    pool_close_price = db.Column(db.Float(precision=2,asdecimal=True),nullable=False)
    pool_amount_buy = db.Column(db.Float(precision=5,asdecimal=True),nullable=False)
    pool_amount_sell = db.Column(db.Float(precision=5,asdecimal=True),nullable=False)
    pool_multiplier_buy = db.Column(db.Float(precision=2,asdecimal=True),nullable=False)
    pool_multiplier_sell = db.Column(db.Float(precision=2,asdecimal=True),nullable=False)
    pool_fee_type = db.Column(db.Integer,nullable=False)
    pool_fee_amount = db.Column(db.Float(precision=2,asdecimal=True),nullable=False)
    pool_status = db.Column(db.Integer,nullable=False) # 0 = not started 1 = open  2 = confirming  3 = closed  4 = under review
    pool_tcreate = db.Column(db.DateTime(timezone=True), default=func.now())
    pool_tmodified = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())
    pool_start = db.Column(db.DateTime(timezone=True), default=None, nullable=True)
    pool_topen = db.Column(db.DateTime(timezone=True), default=None, nullable=True)
    pool_tlock = db.Column(db.DateTime(timezone=True), default=None, nullable=True)
    pool_texpire = db.Column(db.DateTime(timezone=True), default=None, nullable=True)
    pool_tclose = db.Column(db.DateTime(timezone=True), default=None, nullable=True)
    pool_treview = db.Column(db.DateTime(timezone=True), default=None, nullable=True)



    transactions = db.relationship(
        "Transaction",
        backref="pool",
        primaryjoin="Transaction.pool_id == Pool.pool_id",
        order_by="desc(Transaction.transaction_tmodified)",
    )

    # Pool state
    POOL_STATE_NOT_STARTED = 0 # No betting allowed yet
    POOL_STATE_OPEN = 1 # Open for betting
    POOL_STATE_LOCKED = 2 # No more betting, pool has begun
    POOL_STATE_EXPIRED = 3 # Time expired, no payouts yet
    POOL_STATE_CLOSED = 4  # Payouts complete
    POOL_STATE_UNDER_REVIEW = 5 # Oops, there's a problem

    # Pool Fees
    POOL_FEE_NONE = 0
    POOL_FEE_FIXED = 1
    POOL_FEE_PERCENT = 2


class UserSchema(ma.ModelSchema):
    def __init__(self, **kwargs):
        super(UserSchema, self).__init__(**kwargs)

    class Meta:
        model = User
        sqla_session = db.session

    # transactions = fields.Nested("UserTransactionSchema", default=[], many=True)
    # pools = fields.Nested("UserPoolSchema", default=[], many=True)



class TransactionSchema(ma.ModelSchema):
    def __init__(self, **kwargs):
        super(TransactionSchema,self).__init__(**kwargs)

    class Meta:
        model = Transaction
        sqla_session = db.session

    user = fields.Nested("TransactionUserSchema", default=None)
    pool = fields.Nested("TransactionPoolSchema", default=None)

class TransactionUserSchema(ma.ModelSchema):
    """
    This class exists to get around a recursion issue
    """

    def __init__(self, **kwargs):
        super(TransactionUserSchema,self).__init__(**kwargs)

    user_id = fields.Int()
    user_name_display = fields.Str()
    user_name = fields.Str()
    user_avatar = fields.Str()
    user_status = fields.Int()
    user_tcreate = fields.Str()
    user_tmodified = fields.Str()
    user_tlogin = fields.Str()

class UserTransactionSchema(ma.ModelSchema):
    """
    This class exists to get around a recursion issue
    """

    def __init__(self, **kwargs):
        super(UserTransactionSchema, self).__init__(**kwargs)

    transaction_id = fields.Int()
    user_id = fields.Int()
    pool_id = fields.Int()
    pool_hash = fields.Str()
    transaction_amount_buy = fields.Float()
    transaction_amount_sell = fields.Float()
    transaction_is_deposit = fields.Boolean()
    transaction_wallet_to = fields.Str()
    transaction_wallet_from = fields.Str()
    transaction_status = fields.Int()
    transaction_tcreate = fields.Str()
    transaction_tmodified = fields.Str()

class TransactionPoolSchema(ma.ModelSchema):
    """
    This class exists to get around a recursion issue
    """

    def __init__(self, **kwargs):
        super(TransactionPoolSchema, self).__init__(**kwargs)

    pool_id = fields.Int()
    user_id = fields.Int()
    #transaction_id = fields.Int()
    pool_hash = fields.Str()
    pool_pair = fields.Str()
    pool_timeframe = fields.Str()
    pool_locked_price = fields.Float()
    pool_close_price = fields.Float()
    pool_amount_buy = fields.Float()
    pool_amount_sell = fields.Float()
    pool_multiplier_buy = fields.Float()
    pool_multiplier_sell = fields.Float()
    pool_fee_type = fields.Int()
    pool_fee_amount = fields.Float()
    pool_status = fields.Int()
    pool_tcreate = fields.Str()
    pool_tmodified = fields.Str()

class UserPoolSchema(ma.ModelSchema):
    """
    This class exists to get around a recursion issue
    """

    def __init__(self, **kwargs):
        super(UserPoolSchema, self).__init__(**kwargs)

    pool_id = fields.Int()
    user_id = fields.Int()
    pool_hash = fields.Str()
    pool_pair = fields.Str()
    pool_timeframe = fields.Str()
    pool_locked_price = fields.Float()
    pool_close_price = fields.Float()
    pool_amount_buy = fields.Float()
    pool_amount_sell = fields.Float()
    pool_multiplier_buy = fields.Float()
    pool_multiplier_sell = fields.Float()
    pool_fee_type = fields.Int()
    pool_fee_amount = fields.Float()
    pool_status = fields.Int()
    pool_tcreate = fields.Str()
    pool_tmodified = fields.Str()


class PoolSchema(ma.ModelSchema):
    def __init__(self, **kwargs):
        super(PoolSchema,self).__init__(**kwargs)

    class Meta:
        model = Pool
        sqla_session = db.session

    users = fields.Nested("PoolUserSchema", default=None)
    transactions = fields.Nested("PoolTransactionSchema", default=None)


class PoolUserSchema(ma.ModelSchema):
    """
    This class exists to get around a recursion issue
    """

    def __init__(self, **kwargs):
        super(PoolUserSchema,self).__init__(**kwargs)

    user_id = fields.Int()
    user_name_display = fields.Str()
    user_name = fields.Str()
    user_avatar = fields.Str()
    user_status = fields.Int()
    user_tcreate = fields.Str()
    user_tmodified = fields.Str()
    user_tlogin = fields.Str()


class PoolTransactionSchema(ma.ModelSchema):
    """
    This class exists to get around a recursion issue
    """

    def __init__(self, **kwargs):
        super(PoolTransactionSchema,self).__init__(**kwargs)

    transaction_id = fields.Int()
    transaction_amount_buy = fields.Float()
    transaction_amount_sell = fields.Float()
    transaction_is_deposit = fields.Float()
    transaction_wallet_to = fields.Str()
    transaction_wallet_from = fields.Str()
    transaction_status = fields.Int()
    transaction_tcreate = fields.Str()
    transaction_tmodified = fields.Str()