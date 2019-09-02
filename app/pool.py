"""
This is the people module and supports all the REST actions for the
people data
"""

from flask import make_response, abort
from config import db
from models import User, Transaction, TransactionSchema, Pool, PoolSchema



def read_user_pools(user_id):
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

        pools = Pool.query\
            .filter(Transaction.user_id == user_id)\
            .outerjoin(Pool, Transaction.pool_id == Pool.pool_id)\
            .order_by(db.desc(Pool.pool_tmodified)).all()

        # Serialize the list of notes from our data
        pool_schema = PoolSchema(many=True, exclude=[])
        data = pool_schema.dump(pools).data
        return data


    # Otherwise, nope, didn't find that person
    else:
        abort(404, "Pool not found for user ID: {user_id}")

def read_all(pool_ids=None):
    """
    This function responds to a request for /api/people/notes
    with the complete list of notes, sorted by note timestamp

    :return:                json list of all notes for all people
    """
    # Query the database for all the notes

    if not pool_ids:
        pools = Pool.query.order_by(db.desc(Pool.pool_tmodified)).all()
    else:
        pools = Pool.query \
        .filter(Pool.pool_id.in_(pool_ids)) \
        .all()

    # Serialize the list of notes from our data
    pool_schema = PoolSchema(many=True, exclude=[])
    data = pool_schema.dump(pools).data
    return data


def read_one(pool_id):
    """
    This function responds to a request for
    /api/user/{user_id}/pools/{pool_id}
    with one matching note for the associated person

    :param person_id:       Id of person the note is related to
    :param note_id:         Id of the note
    :return:                json string of note contents
    """
    # Query the database for the note
    pool = (
        Pool.query.filter(Pool.pool_id == pool_id)
            .outerjoin(Transaction, Transaction.pool_id == pool_id) \
            .outerjoin(User, Transaction.user_id == User.user_id) \
            .one_or_none()
    )

    # Was a note found?
    if pool is not None:
        pool_schema = PoolSchema()
        data = pool_schema.dump(pool).data
        return data

    # Otherwise, nope, didn't find that note
    else:
        abort(404, "Pool not found for ID: {pool_id}".format(pool_id=pool_id))


def create(user_id, pool):
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
    schema = PoolSchema()
    new_pool = schema.load(pool, session=db.session).data

    # Add the note to the person and database
    user.pool.append(new_pool)
    db.session.commit()

    # Serialize and return the newly created note in the response
    data = schema.dump(new_pool).data

    return data, 201


def update(user_id, pool_id, pool):
    """
    This function updates an existing note related to the passed in
    person id.

    :param person_id:       Id of the person the note is related to
    :param note_id:         Id of the note to update
    :param content:            The JSON containing the note data
    :return:                200 on success
    """
    update_pool = (
        Pool.query.filter(User.user_id == user_id)
        .filter(Pool.pool_id == pool_id)
        .one_or_none()
    )

    # Did we find an existing note?
    if update_pool is not None:

        # turn the passed in note into a db object
        schema = PoolSchema()
        update = schema.load(pool, session=db.session).data

        # Set the id's to the note we want to update
        update.user_id = update_pool.user_id
        update.pool_id = update_pool.pool_id

        # merge the new object into the old and commit it to the db
        db.session.merge(update)
        db.session.commit()

        # return updated note in the response
        data = schema.dump(update_pool).data

        return data, 200

    # Otherwise, nope, didn't find that note
    else:
        abort(404, "Pool not found for Id: {pool_id}".format(pool_id=pool_id))


def delete(user_id, pool_id):
    """
    This function deletes a note from the note structure

    :param person_id:   Id of the person the note is related to
    :param note_id:     Id of the note to delete
    :return:            200 on successful delete, 404 if not found
    """
    # Get the note requested
    pool = (
        Pool.query.filter(User.user_id == user_id)
        .filter(Pool.pool_id == pool_id)
        .one_or_none()
    )

    # did we find a note?
    if pool is not None:
        db.session.delete(pool)
        db.session.commit()
        return make_response(
            "Note {pool_id} deleted".format(pool_id=pool_id), 200
        )

    # Otherwise, nope, didn't find that note
    else:
        abort(404, "Pool not found for Id: {pool_id}".format(pool_id=pool_id))
