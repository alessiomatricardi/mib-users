from flask import request, jsonify
from mib.dao.user_manager import UserManager
from mib.models.user import User
import datetime
from werkzeug.security import check_password_hash

"""
/register
{
    'user': user.serialize(),
    'status': 'success',
    'message': 'Successfully registered',
}
or 
{
    'status': 'Already present'
}
"""
def register():
    """
    This method allows the registration of a new user.
    called using /register.
    if it succeeds return {'user': user.serialize(), 'status': 'success', 'message': 'Successfully registered'}
    if it fails return{'status': 'Already present'}
    """
    post_data = request.get_json()
    email = post_data.get('email')
    password = post_data.get('password')

    searched_user = UserManager.retrieve_by_email(email)
    if searched_user is not None:
        return jsonify({
            'status': 'Already present'
        }), 200

    user = User()
    date_of_birth = datetime.datetime.strptime(post_data.get('date_of_birth'),
                                          '%Y-%m-%d')
    user.set_email(email)
    user.set_password(password)
    user.set_first_name(post_data.get('firstname'))
    user.set_last_name(post_data.get('lastname'))
    user.set_birthday(date_of_birth)
    UserManager.create_user(user)

    response_object = {
        'user': user.serialize(),
        'status': 'success',
        'message': 'Successfully registered',
    }

    return jsonify(response_object), 201

# /unregister
def unregister():
    """
    Unregister the user.
    called using /unregister.
    if it fails return {'status': 'success', 'message': 'Successfully unregistered'}
    if it fails return {'status': 'failure', 'message': 'user not found'} or {'status': 'failure','message': 'Unauthorized'}
    """
    post_data = request.get_json()
    id = post_data.get('id')
    password = post_data.get('password')

    user = UserManager.retrieve_by_id(id)

    if user is None:
        response_object = {
            'status': 'failure',
            'message': 'User not found',
        }
        return jsonify(response_object), 404

    password_is_right = check_password_hash(user.password, password)
    if password_is_right:
        user.is_active = False
        UserManager.update_user(user)
        response_object = {
            'status': 'success',
            'message': 'Successfully unregistered',
        }
        return jsonify(response_object), 200
    else:
        response_object = {
            'status': 'failure',
            'message': 'Unauthorized',
        }
        return jsonify(response_object), 401


def modify_data():
    """
    Modify personal data of the user.
    called using /profile/data
    if it succeeds return {'status': 'success','message': 'Modified'}
    if it fails return {'status': 'failure','message': 'User not found'}
    """
    post_data = request.get_json()
    id = post_data.get('id')
    firstname = post_data.get('firstname')
    lastname = post_data.get('lastname')
    date_of_birth = post_data.get('date_of_birth')

    user = UserManager.retrieve_by_id(id)

    if user is None:
        response_object = {
            'status': 'failure',
            'message': 'User not found',
        }
        return jsonify(response_object), 404
    
    user.firstname = firstname
    user.lastname = lastname
    user.date_of_birth = datetime.datetime.strptime(date_of_birth, '%Y-%m-%d')
    UserManager.update_user(user)
    response_object = {
        'status': 'success',
        'message': 'Modified',
    }
    return jsonify(response_object), 200


def modify_password():
    """
    Used to modify password 
    called using /profile/password
    if it succeds return {'status': 'success','message': 'Modified'}
    if it fails return {'status': 'failure','message': 'User not found'}
    """
    post_data = request.get_json()
    id = post_data.get('id')
    old_password = post_data.get('old_password')
    new_password = post_data.get('new_password')
    repeat_new_password = post_data.get('repeat_new_password')

    user = UserManager.retrieve_by_id(id)

    if user is None:
        response_object = {
            'status': 'failure',
            'message': 'User not found',
        }
        return jsonify(response_object), 404
    
    # check if the old password is the same of the one stored in the database
    if not check_password_hash(user.password, old_password):
        response_object = {
            'status': 'failure',
            'message': 'Unauthorized',
        }
        return jsonify(response_object), 401

    # check that the old and new password are not the same
    if check_password_hash(user.password, new_password):
        response_object = {
            'status': 'failure',
            'message': 'Password not changed',
        }
        return jsonify(response_object), 409

    # check that the new password and the repeated new password are different
    if new_password != repeat_new_password:
        response_object = {
            'status': 'failure',
            'message': 'New and repeated passwords are different',
        }
        return jsonify(response_object), 403
    
    user.set_password(new_password)
    UserManager.update_user(user)
    
    response_object = {
        'status': 'success',
        'message': 'Modified',
    }
    return jsonify(response_object), 200


def modify_picture():
    pass

# /users/<user_id> or /profile
def get_user(user_id):
    """
    Get a user by its current id.

    :param user_id: user it
    :return: json response
    """
    user = UserManager.retrieve_by_id(user_id)
    if user is None:
        response = {'status': 'User not present'}
        return jsonify(response), 404

    return jsonify(user.serialize()), 200


def get_user_by_email(user_email):
    """
    Get a user by its current email.

    :param user_email: user email
    :return: json response
    """
    user = UserManager.retrieve_by_email(user_email)
    if user is None:
        response = {'status': 'User not present'}
        return jsonify(response), 404

    return jsonify(user.serialize()), 200


'''
TODO decidere se eliminare tutto :)
def delete_user(user_id):
    """
    Delete the user with id = user_id.

    :param user_id the id of user to be deleted
    :return json response
    """
    UserManager.delete_user_by_id(user_id)
    response_object = {
        'status': 'success',
        'message': 'Successfully deleted',
    }

    return jsonify(response_object), 202

'''