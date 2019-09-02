"""
This is the people module and supports all the REST actions for the
people data
"""

from flask import make_response, abort
from config import db
from models import User, Transaction, TransactionSchema, Pool



def read_user_transactions(user_id):
    """
    This function responds to a request for /api/people
    with the complete lists of people

    :return:        json string of list of people
    """
    # Create the list of people from our data
    user = (
        User.query.filter(User.user_id == user_id)
        .one_or_none()
    )

    # Did we find a person?
    if user is not None:

        transactions = Transaction.query\
            .filter(Transaction.user_id == user_id)\
            .outerjoin(Pool, Pool.pool_id == Transaction.pool_id)\
            .order_by(db.desc(Transaction.transaction_tmodified)).all()

        # Serialize the list of notes from our data
        transaction_schema = TransactionSchema(many=True, exclude=["pool.pool_users","user"])
        data = transaction_schema.dump(transactions).data
        return data


    # Otherwise, nope, didn't find that person
    else:
        abort(404, "User not found for user ID: {user_id}")

def read_all(transaction_ids=None):
    """
    This function responds to a request for /api/people/notes
    with the complete list of notes, sorted by note timestamp

    :return:                json list of all notes for all people
    """
    # Query the database for all the notes
    if not transaction_ids:
        transactions = Transaction.query.order_by(db.desc(Transaction.transaction_tmodified)).all()
    else:
        transactions = Transaction.query \
        .filter(Transaction.transaction_id.in_(transaction_ids)) \
        .all()
    # Serialize the list of notes from our data
    transaction_schema = TransactionSchema(many=True, exclude=["pool.pool_users"])
    data = transaction_schema.dump(transactions).data
    return data


def read_one(transaction_id):
    """
    This function responds to a request for
    /api/user/{user_id}/transactions/{transaction_id}
    with one matching note for the associated person

    :param person_id:       Id of person the note is related to
    :param note_id:         Id of the note
    :return:                json string of note contents
    """
    # Query the database for the note
    transaction = (
        Transaction.query.filter(Transaction.transaction_id == transaction_id)
        .one_or_none()
    )

    # Was a note found?
    if transaction is not None:
        transaction_schema = TransactionSchema()
        data = transaction_schema.dump(transaction).data
        return data

    # Otherwise, nope, didn't find that note
    else:
        abort(404, "Transaction not found for Id: {transaction_id}".format(transaction_id=transaction_id))


def create(user_id, transaction):
    """
    This function creates a new note related to the passed in person id.

    :param person_id:       Id of the person the note is related to
    :param note:            The JSON containing the note data
    :return:                201 on success
    """
    # get the parent person
    user = User.query.filter(User.user_id == user_id).one_or_none()

    # Was a person found?
    if user is None:
        abort(404, "User not found for Id: {user_id}".format(user_id=user_id))

    # Create a note schema instance
    schema = TransactionSchema()
    new_transaction = schema.load(transaction, session=db.session).data

    # Add the note to the person and database
    user.transactions.append(new_transaction)
    db.session.commit()

    # Serialize and return the newly created note in the response
    data = schema.dump(new_transaction).data

    return data, 201


def update(user_id, transaction_id, transaction):
    """
    This function updates an existing note related to the passed in
    person id.

    :param person_id:       Id of the person the note is related to
    :param note_id:         Id of the note to update
    :param content:            The JSON containing the note data
    :return:                200 on success
    """
    update_transaction = (
        Transaction.query.filter(User.user_id == user_id)
        .filter(Transaction.transaction_id == transaction_id)
        .one_or_none()
    )

    # Did we find an existing note?
    if update_transaction is not None:

        # turn the passed in note into a db object
        schema = TransactionSchema()
        update = schema.load(transaction, session=db.session).data

        # Set the id's to the note we want to update
        update.user_id = update_transaction.user_id
        update.transaction_id = update_transaction.transaction_id

        # merge the new object into the old and commit it to the db
        db.session.merge(update)
        db.session.commit()

        # return updated note in the response
        data = schema.dump(update_transaction).data

        return data, 200

    # Otherwise, nope, didn't find that note
    else:
        abort(404, "Transaction not found for Id: {transaction_id}".format(transaction_id=transaction_id))


def delete(user_id, transaction_id):
    """
    This function deletes a note from the note structure

    :param person_id:   Id of the person the note is related to
    :param note_id:     Id of the note to delete
    :return:            200 on successful delete, 404 if not found
    """
    # Get the note requested
    transaction = (
        Transaction.query.filter(User.user_id == user_id)
        .filter(Transaction.transaction_id == transaction_id)
        .one_or_none()
    )

    # did we find a note?
    if transaction is not None:
        db.session.delete(transaction)
        db.session.commit()
        return make_response(
            "Note {transaction_id} deleted".format(transaction_id=transaction_id), 200
        )

    # Otherwise, nope, didn't find that note
    else:
        abort(404, "Transaction not found for Id: {transaction_id}".format(transaction_id=transaction_id))
