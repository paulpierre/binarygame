"""
This is the people module and supports all the REST actions for the
people data
"""

from flask import make_response, abort
from config import db
from models import User, UserSchema, Transaction, Pool, TransactionSchema





def read_all(user_ids=None):
    """
    This function responds to a request for /api/people
    with the complete lists of people

    :return:        json string of list of people
    """
    # Create the list of people from our data
    if not user_ids:
        users = User.query.order_by(User.user_id).all()
    else:
        users = User.query \
        .filter(User.user_id.in_(user_ids)) \
        .all()
    # Serialize the data for the response
    user_schema = UserSchema(many=True,exclude=["transactions","pools","pool"])
    data = user_schema.dump(users).data
    return data


def read_one(user_id):
    """
    This function responds to a request for /api/people/{person_id}
    with one matching person from people

    :param person_id:   Id of person to find
    :return:            person matching id
    """
    # Build the initial query
    user = (
        User.query.filter(User.user_id == user_id)
        .one_or_none()
    )

    # Did we find a person?
    if user is not None:

        # Serialize the data for the response
        user_schema = UserSchema( exclude=["transactions","pools","pool"])
        data = user_schema.dump(user).data
        return data

    # Otherwise, nope, didn't find that person
    else:
        abort(404, "User not found for Id: {user_id}")


def create(user):
    """
    This function creates a new person in the people structure
    based on the passed in person data

    :param person:  person to create in people structure
    :return:        201 on success, 406 on person exists
    """
    user_email = user.get("user_email")
    user_name = user.get("user_name")
    user_fingerprint = user.get("user_fingerprint")
    user_register_ip = user.get("user_register_ip")

    existing_user = (
        User.query.filter(User.user_email == user_email)
        .filter(User.user_name == user_name)
        .one_or_none()
    )

    # Can we insert this person?
    if existing_user is None:

        # Create a person instance using the schema and the passed in person
        schema = UserSchema()
        new_user = schema.load(user, session=db.session).data

        #lets add additional information in registration
        new_user.user_email = user_email
        new_user.user_fingerprint = user_fingerprint
        new_user.user_register_ip = user_register_ip
        new_user.user_name = user_name


        # Add the person to the database
        db.session.add(new_user)
        db.session.commit()

        # Serialize and return the newly created person in the response
        data = schema.dump(new_user).data

        return data, 201

    # Otherwise, nope, person exists already
    else:
        abort(409, "User {user_email} exists already".format(user_email=user_email))


def update(user_id, user):
    """
    This function updates an existing person in the people structure

    :param person_id:   Id of the person to update in the people structure
    :param person:      person to update
    :return:            updated person structure
    """
    # Get the person requested from the db into session
    update_user = User.query.filter(
        User.user_id == user_id
    ).one_or_none()

    # Did we find an existing person?
    if update_user is not None:

        # turn the passed in person into a db object
        schema = UserSchema()
        update = schema.load(user, session=db.session).data

        # Set the id to the person we want to update
        update.user_id = update_user.user_id

        # merge the new object into the old and commit it to the db
        db.session.merge(update)
        db.session.commit()

        # return updated person in the response
        data = schema.dump(update_user).data

        return data, 200

    # Otherwise, nope, didn't find that person
    else:
        abort(404, "User not found for Id: {user_id}".format(user_id=user_id))


def delete(user_id):
    """
    This function deletes a person from the people structure

    :param person_id:   Id of the person to delete
    :return:            200 on successful delete, 404 if not found
    """
    # Get the person requested
    user = User.query.filter(User.person_id == user_id).one_or_none()

    # Did we find a person?
    if user is not None:
        db.session.delete(user)
        db.session.commit()
        return make_response("User {user_id} deleted".format(user_id=user_id), 200)

    # Otherwise, nope, didn't find that person
    else:
        abort(404, "User not found for Id: {user_id}".format(user_id=user_id))
