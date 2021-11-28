from mib.dao.user_manager import UserManager
from flask import jsonify


def login(auth):
    """
    Authentication resource for generic user.
    :param auth: a dict with email and password keys.
    :return: the response 200 if credentials are correct
    :return: the response 404 if the user doesn't exist
    :return: the response 401 if the login failed
    """
    user = UserManager.retrieve_by_email(auth['email'])

    # user doesn't exist
    if user is None:
        response = {
            'authentication': 'failure',
            'user': None
        }
        return jsonify(response), 404

    # user no longer active or auth failed
    if not user.is_active or not user.authenticate(auth['password']):
        response = {
            'authentication': 'failure',
            'user': None
        }
        return jsonify(response), 401

    response = {
        'authentication': 'success',
        'user': user.serialize()
    }
    return jsonify(response), 200
