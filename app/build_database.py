import os
from datetime import datetime
from config import db
import bcrypt
from models import Transaction, User, Pool



# Data to initialize database with

TRANSACTIONS = [

    # Some deposits for the users
    {
        "user_id": 1,
        "pool_id": None,
        "pool_hash": None,
        "transaction_amount_buy": 1000,
        "transaction_amount_sell": None,
        "transaction_is_deposit": True,
        "transaction_wallet_to": "a8f5f167f44f4964e6c998dee827110c3f2f4295a5eb6ad967b832d35e048852",
        "transaction_wallet_from": None,
        "transaction_status": Transaction.TRANSACTION_IS_DEPOSIT,
        "transaction_tcreate": "2019-08-01 12:00:00",
        "transaction_tmodified": "2019-08-01 12:00:00"
    },
    {
        "user_id": 2,
        "pool_id": None,
        "pool_hash": None,
        "transaction_amount_buy": 267433.4322,
        "transaction_amount_sell": 0,
        "transaction_is_deposit": True,
        "transaction_wallet_to": "eb677810279a00c2aacde7e2f585f51e0c3f2f4295a5eb6ad967b832d35e048852",
        "transaction_wallet_from": None,
        "transaction_status": Transaction.TRANSACTION_IS_DEPOSIT,
        "transaction_tcreate": "2019-08-01 12:00:00",
        "transaction_tmodified": "2019-08-01 12:00:00"
    },
    {
        "user_id": 3,
        "pool_id": None,
        "pool_hash": None,
        "transaction_amount_buy": 221244,
        "transaction_amount_sell": None,
        "transaction_is_deposit": True,
        "transaction_wallet_to": "eb677810279a00c2aacde7e2f585f51e07b832d35e048852",
        "transaction_wallet_from": None,
        "transaction_status": Transaction.TRANSACTION_IS_DEPOSIT,
        "transaction_tcreate": "2019-08-01 12:00:00",
        "transaction_tmodified": "2019-08-01 12:00:00"
    },


    # Some activity for the users
    {
        "user_id":1,
        "pool_id":1,
        "pool_hash":"967b83",
        "transaction_amount_buy": 214134.12,
        "transaction_amount_sell": None,
        "transaction_is_deposit": False,
        "transaction_wallet_to": None,
        "transaction_wallet_from": "a8f5f167f44f4964e6c998dee827110c3f2f4295a5eb6ad967b832d35e048852",
        "transaction_status": Transaction.TRANSACTION_POOL_LOSS,
        "transaction_tcreate": "2019-08-01 12:00:00",
        "transaction_tmodified": "2019-08-01 12:00:00"
    },
    {
        "user_id": 2,
        "pool_id": 1,
        "pool_hash": "967b83",
        "transaction_amount_buy": 54,
        "transaction_amount_sell": None,
        "transaction_is_deposit": False,
        "transaction_wallet_to": None,
        "transaction_wallet_from": "eb677810279a00c2aacde7e2f585f51e0c3f2f4295a5eb6ad967b832d35e048852",
        "transaction_status": Transaction.TRANSACTION_POOL_WIN,
        "transaction_tcreate": "2019-08-01 12:00:00",
        "transaction_tmodified": "2019-08-01 12:00:00"
    },
    {
        "user_id": 3,
        "pool_id": 1,
        "pool_hash": "967b83",
        "transaction_amount_buy": None,
        "transaction_amount_sell": 3334,
        "transaction_is_deposit": False,
        "transaction_wallet_to": None,
        "transaction_wallet_from": "eb677810279a00c2aacde7e2f585f51e07b832d35e048852",
        "transaction_status": Transaction.TRANSACTION_POOL_WIN,
        "transaction_tcreate": "2019-08-01 12:00:00",
        "transaction_tmodified": "2019-08-01 12:00:00"
    },
]

POOLS = [
    {
        "pool_hash": "967b83",
        "pool_pair": "btcusd",
        "pool_timeframe": "5m",
        "pool_locked_price":10024.12,
        "pool_close_price": 10024.12,
        "pool_amount_buy": 4939.43404,
        "pool_amount_sell": 446.54439,
        "pool_multiplier_buy": 1.31,
        "pool_multiplier_sell": 0.33,
        "pool_fee_type":Pool.POOL_FEE_PERCENT,
        "pool_fee_amount":0.20,
        "pool_status": Pool.POOL_STATE_CLOSED,
        "pool_tcreate":"2019-08-01 12:00:00",
        "pool_tmodified": "2019-08-01 12:00:00",
    },
    {
        "pool_hash": "67b83",
        "pool_pair": "btcusd",
        "pool_timeframe": "5m",
        "pool_locked_price": 10024.12,
        "pool_close_price": 10024.12,
        "pool_amount_buy": 4939.43404,
        "pool_amount_sell": 446.54439,
        "pool_multiplier_buy": 1.31,
        "pool_multiplier_sell": 0.33,
        "pool_fee_type": Pool.POOL_FEE_FIXED,
        "pool_fee_amount": 2500,
        "pool_status": Pool.POOL_STATE_CLOSED,
        "pool_tcreate": "2019-08-01 12:05:00",
        "pool_tmodified": "2019-08-01 12:05:00",
    },
    {
        "pool_hash": "35e04",
        "pool_pair": "btcusd",
        "pool_timeframe": "5m",
        "pool_locked_price": 10024.12,
        "pool_close_price": 10024.12,
        "pool_amount_buy": 4939.43404,
        "pool_amount_sell": 446.54439,
        "pool_multiplier_buy": 1.31,
        "pool_multiplier_sell": 0.33,
        "pool_fee_type": Pool.POOL_FEE_PERCENT,
        "pool_fee_amount": 0.20,
        "pool_status": Pool.POOL_STATE_CLOSED,
        "pool_tcreate": "2019-08-01 12:10:00",
        "pool_tmodified": "2019-08-01 12:10:00",
    },

]


USERS = [
    {
        "user_fingerprint": "3f2f4295a5eb6ad967b832d35e048852",
        "user_email": "barry@hbo.com",
        "user_password":bcrypt.hashpw("abc123", bcrypt.gensalt()),
        "user_name": "crypto_barry",
        "user_name_display": "Crypto Barry",
        "user_avatar": "https://tvseriesfinale.com/wp-content/uploads/2017/12/barry-hbo-590x346.png",
        "user_photo_id":"https://tvseriesfinale.com/wp-content/uploads/2017/12/barry-hbo-590x346.png",
        "user_did_kyc":True,
        "user_did_aml":True,
        "user_status":0,
        "user_wallet_address":"a8f5f167f44f4964e6c998dee827110c3f2f4295a5eb6ad967b832d35e048852",
        "user_wallet_address_eth": "a8f5f167f44f4964e6c998dee827110c3f2f4295a5eb6ad967b832d35e048852",
        "user_wallet_address_btc": "a8f5f167f44f4964e6c998dee827110c3f2f4295a5eb6ad967b832d35e048852",
        "user_wallet_address_xmr": "a8f5f167f44f4964e6c998dee827110c3f2f4295a5eb6ad967b832d35e048852",
        "user_register_ip":"127.0.0.1",
        "user_last_ip":"127.0.0.1",
        "user_referral_code":"3F49A",
        "user_tcreate":"2019-08-01 12:00:00",
        "user_tmodified":"2019-08-01 12:00:00",
        "user_tconfirm": "2019-08-01 12:00:00",
        "user_tlogin":"2019-08-01 12:00:00",
    },
    {
        "user_fingerprint": "eb677810279a00c2aacde7e2f585f51e",
        "user_email": "john_grisham@penguinpublishers.com",
        "user_password":bcrypt.hashpw("abc123", bcrypt.gensalt()),
        "user_name": "jgrish1975",
        "user_name_display": "Johnathan Grisham",
        "user_avatar": "https://images-na.ssl-images-amazon.com/images/I/71JrhQGPrOL._US230_.jpg",
        "user_photo_id": "https://images-na.ssl-images-amazon.com/images/I/71JrhQGPrOL._US230_.jpg",
        "user_did_kyc": True,
        "user_did_aml": True,
        "user_status": 0,
        "user_wallet_address": "eb677810279a00c2aacde7e2f585f51e0c3f2f4295a5eb6ad967b832d35e048852",
        "user_wallet_address_eth": "eb677810279a00c2aacde7e2f585f51ec3f2f4295a5eb6ad967b832d35e048852",
        "user_wallet_address_btc": "a8f5f167feb677810279a00c2aacde7e2f585f51e7b832d35e043444333358852",
        "user_wallet_address_xmr": "eb677810279a00c10279a00c2aacde7e2f585f51ef2f4295a5eb6ad965e048852",
        "user_register_ip": "127.0.0.1",
        "user_last_ip": "127.0.0.1",
        "user_referral_code": "1B349A",
        "user_tcreate":"2019-08-01 12:00:00",
        "user_tmodified":"2019-08-01 12:00:00",
        "user_tconfirm": "2019-08-01 12:00:00",
        "user_tlogin":"2019-08-01 12:00:00",
    },
    {
        "user_fingerprint": "b5393d0c464ac0d63250223dc2bc54d1",
        "user_email": "cs.lewis@gmail.com",
        "user_password":bcrypt.hashpw("abc123", bcrypt.gensalt()),
        "user_name": "Louis13",
        "user_name_display": "C. S. Lewis",
        "user_avatar": "https://upload.wikimedia.org/wikipedia/en/thumb/1/1e/C.s.lewis3.JPG/220px-C.s.lewis3.JPG",
        "user_photo_id": "https://upload.wikimedia.org/wikipedia/en/thumb/1/1e/C.s.lewis3.JPG/220px-C.s.lewis3.JPG",
        "user_did_kyc": True,
        "user_did_aml": True,
        "user_status": 0,
        "user_wallet_address": "eb677810279a00c2aacde7e2f585f51e07b832d35e048852",
        "user_wallet_address_eth": "eb677810279a00c2aacde7e2f585f515eb6ad967b832d35e048852",
        "user_wallet_address_btc": "a8f5f167feb677810279a00c2aacde1e7b832d35e043444333358852",
        "user_wallet_address_xmr": "eb677810279a00c10279a00c2aacde7e2f585f51ef2eb6ad965e048852",
        "user_register_ip": "127.0.0.1",
        "user_last_ip": "127.0.0.1",
        "user_referral_code": "CB349A",
        "user_tcreate":"2019-08-01 12:00:00",
        "user_tmodified":"2019-08-01 12:00:00",
        "user_tconfirm": "2019-08-01 12:00:00",
        "user_tlogin":"2019-08-01 12:00:00",
    },
]



# Create the database
db.create_all()

for user in USERS:
    u = User(
        user_fingerprint=user.get("user_fingerprint"),
        user_email=user.get("user_email"),
        user_password=user.get("user_password"),
        user_name=user.get("user_name"),
        user_name_display=user.get("user_name_display"),
        user_avatar=user.get("user_avatar"),
        user_photo_id=user.get("user_photo_id"),
        user_did_kyc=user.get("user_did_kyc"),
        user_did_aml=user.get("user_did_aml"),
        user_status=user.get("user_status"),
        user_wallet_address=user.get("user_wallet_address"),
        user_wallet_address_eth=user.get("user_wallet_address_eth"),
        user_wallet_address_btc=user.get("user_wallet_address_btc"),
        user_wallet_address_xmr=user.get("user_wallet_address_xmr"),
        user_register_ip=user.get("user_register_ip"),
        user_last_ip=user.get("user_last_ip"),
        user_referral_code=user.get("user_referral_code"),
        user_tcreate=user.get("user_tcreate"),
        user_tmodified=user.get("user_tmodified"),
        user_tlogin=user.get("user_tlogin"),
        user_tconfirm = user.get("user_tconfirm")
    )
    db.session.add(u)

for pool in POOLS:
    p = Pool(
        pool_hash = pool.get("pool_hash"),
        pool_pair=pool.get("pool_pair"),
        pool_timeframe=pool.get("pool_timeframe"),
        pool_locked_price=pool.get("pool_locked_price"),
        pool_close_price=pool.get("pool_close_price"),
        pool_amount_buy=pool.get("pool_amount_buy"),
        pool_amount_sell=pool.get("pool_amount_sell"),
        pool_multiplier_buy=pool.get("pool_multiplier_buy"),
        pool_multiplier_sell=pool.get("pool_multiplier_sell"),
        pool_fee_type=pool.get("pool_fee_type"),
        pool_fee_amount=pool.get("pool_fee_amount"),
        pool_status=pool.get("pool_status"),
        #pool_users=pool.get("pool_users"),
        pool_tcreate=pool.get("pool_tcreate"),
        pool_tmodified=pool.get("pool_tmodified"),
    )
    db.session.add(p)

for tx in TRANSACTIONS:
    t = Transaction(
        user_id = tx.get("user_id"),
        pool_id = tx.get("pool_id"),
        pool_hash = tx.get("pool_hash"),
        transaction_amount_buy = tx.get("transaction_amount_buy"),
        transaction_amount_sell = tx.get("transaction_amount_sell"),
        transaction_is_deposit = tx.get("transaction_is_deposit"),
        transaction_wallet_to = tx.get("transaction_wallet_to"),
        transaction_wallet_from = tx.get("transaction_wallet_from"),
        transaction_status = tx.get("transaction_status"),
        transaction_tcreate = tx.get("transaction_tcreate"),
        transaction_tmodified = tx.get("transaction_tmodified"),
    )
    db.session.add(t)

db.session.commit()




"""
    # Add the notes for the person
    for note in user.get("notes"):
        content, timestamp = note
        p.notes.append(
            Transaction(
                content=content,
                timestamp=datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S"),
            )
        )
"""