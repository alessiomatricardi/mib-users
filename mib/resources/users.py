import datetime
import base64
import os
import requests
import json

from mib import app
from flask import request, jsonify
from mib.dao.user_manager import UserManager
from mib.models.user import User
from PIL import Image
from io import BytesIO
from werkzeug.security import check_password_hash, generate_password_hash

BLACKLIST_ENDPOINT = app.config['BLACKLIST_MS_URL']
REQUESTS_TIMEOUT_SECONDS = app.config['REQUESTS_TIMEOUT_SECONDS']


def register():
    """
    This method allows the registration of a new user.
    Called by /register.
    if it succeeds return {'user': user.serialize(), 'status': 'success', 'description': 'Successfully registered'}
    if it fails return{'status': 'failure', 'description' : 'Already present'}
    """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    searched_user = UserManager.retrieve_by_email(email)

    if searched_user is not None:
        return jsonify({
            'status': 'failure',
            'descrition': 'Already present'
        }), 200

    user = User()

    date_of_birth = datetime.datetime.strptime(data.get('date_of_birth'),
                                               '%Y-%m-%d')
    user.set_email(email)
    user.set_password(password)
    user.set_first_name(data.get('firstname'))
    user.set_last_name(data.get('lastname'))
    user.set_birthday(date_of_birth)
    UserManager.create_user(user)

    response_object = {
        'user': user.serialize(),
        'status': 'success',
        'description': 'Successfully registered',
    }

    return jsonify(response_object), 201


def unregister():
    """
    Unregister the user.
    Called by /unregister.
    if it fails return {'status': 'success', 'description': 'Successfully unregistered'}
    if it fails return {'status': 'failure', 'description': 'user not found'} or {'status': 'failure','description': 'Unauthorized'}
    """
    data = request.get_json()
    id = data.get('requester_id')
    password = data.get('password')

    user = UserManager.retrieve_by_id(id)

    if user is None:
        response_object = {
            'status': 'failure',
            'description': 'User not found',
        }
        return jsonify(response_object), 404

    password_is_right = check_password_hash(user.password, password)
    if password_is_right:
        user.is_active = False
        UserManager.update_user(user)
        response_object = {
            'status': 'success',
            'description': 'Successfully unregistered',
        }
        return jsonify(response_object), 200
    else:
        response_object = {
            'status': 'failure',
            'description': 'Unauthorized',
        }
        return jsonify(response_object), 401


def modify_data():
    """
    Modify personal data of the user.
    Called by /profile/data
    if it succeeds return {'status': 'success','description': 'Modified'}
    if it fails return {'status': 'failure','description': 'User not found'}
    """
    data = request.get_json()
    id = data.get('requester_id')
    firstname = data.get('firstname')
    lastname = data.get('lastname')
    date_of_birth = data.get('date_of_birth')

    user = UserManager.retrieve_by_id(id)

    if user is None:
        response_object = {
            'status': 'failure',
            'description': 'User not found',
        }
        return jsonify(response_object), 404

    user.firstname = firstname
    user.lastname = lastname
    user.date_of_birth = datetime.datetime.strptime(date_of_birth, '%Y-%m-%d')

    UserManager.update_user(user)

    response_object = {
        'status': 'success',
        'description': 'Modified',
    }
    return jsonify(response_object), 200


def modify_password():
    """
    Used to modify password 
    Called by /profile/password
    if it succeeds return {'status': 'success','description': 'Modified'}
    if it fails return {'status': 'failure','description': 'User not found'}
    """
    data = request.get_json()
    id = data.get('requester_id')
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    repeat_new_password = data.get('repeat_new_password')

    user = UserManager.retrieve_by_id(id)

    if user is None:
        response_object = {
            'status': 'failure',
            'description': 'User not found',
        }
        return jsonify(response_object), 404

    # check that the actual password is right
    if not check_password_hash(user.password, old_password):
        response_object = {
            'status': 'failure',
            'description': 'Unauthorized',
        }
        return jsonify(response_object), 401

    # check that the old and new password are not the same
    if check_password_hash(user.password, new_password):
        response_object = {
            'status': 'failure',
            'description': 'Password not changed',
        }
        return jsonify(response_object), 400

    # check that the new password and the repeated new password are different
    if new_password != repeat_new_password:
        response_object = {
            'status': 'failure',
            'description': 'New and repeated passwords are different',
        }
        return jsonify(response_object), 400

    user.set_password(new_password)
    UserManager.update_user(user)

    response_object = {
        'status': 'success',
        'description': 'Modified',
    }
    return jsonify(response_object), 200


def modify_content_filter():
    """
    Used to enable/disable content_filter 
    Called by /profile/content_filter
    if it succeds, returns {'status': 'success','description': 'Modified', 'enabled': True/False}
    if it fails return {'status': 'failure','description': 'User not found'}
    """
    data = request.get_json()
    id = data.get('requester_id')
    content_filter = data.get('content_filter')

    user = UserManager.retrieve_by_id(id)

    if user is None:
        response_object = {
            'status': 'failure',
            'description': 'User not found',
        }
        return jsonify(response_object), 404

    user.content_filter_enabled = content_filter
    UserManager.update_user(user)

    response_object = {
        'status': 'success',
        'description': 'Modified',
        'enabled': content_filter
    }
    return jsonify(response_object), 200


def modify_profile_picture():
    """
    Used to modify profile picture 
    Called by /profile/picture
    if it succeds return {'status': 'success','description': 'Modified'}
    if it fails return {'status': 'failure','description': 'User not found'}
    """
    data = request.get_json()
    id = data.get('requester_id')
    img_base64 = data.get('image')

    user = UserManager.retrieve_by_id(id)

    if user is None:
        response_object = {
            'status': 'failure',
            'description': 'User not found',
        }
        return jsonify(response_object), 404

    # decoding image
    img_data = BytesIO(base64.b64decode(img_base64))

    # store it, in case of a previously inserted image it's going to be overwritten
    try:

        # save image in 256x256
        img = Image.open(img_data)
        img = img.convert(
            'RGB'
        )  # in order to support also Alpha transparency images such as PNGs
        img = img.resize([256, 256], Image.ANTIALIAS)
        path_to_save = os.path.join(os.getcwd(), 'mib', 'static', 'pictures',
                                    str(id) + '.jpeg')
        img.save(path_to_save, "JPEG", quality=100, subsampling=0)

        # save image in 100x100
        img = Image.open(img_data)
        img = img.convert(
            'RGB'
        )  # in order to support also Alpha transparency images such as PNGs
        img = img.resize([100, 100], Image.ANTIALIAS)
        path_to_save = os.path.join(os.getcwd(), 'mib', 'static', 'pictures',
                                    str(id) + '_100.jpeg')
        img.save(path_to_save, "JPEG", quality=100, subsampling=0)

    except Exception:
        response_object = {
            'status': 'failure',
            'description': 'Error in saving the image',
        }
        return jsonify(response_object), 500

    user.has_picture = True
    UserManager.update_user(user)

    response_object = {
        'status': 'success',
        'description': 'Modified',
    }
    return jsonify(response_object), 200


def get_user_picture(user_id):

    data = request.get_json()
    requester_id = data.get('requester_id')

    user = UserManager.retrieve_by_id(user_id)

    if user is None:
        response_object = {
            'status': 'failure',
            'description': 'Searched user not found',
        }
        return jsonify(response_object), 404

    if requester_id != user_id:

        current_user = UserManager.retrieve_by_id(requester_id)
        if current_user is None:
            response_object = {
                'status': 'failure',
                'description': 'Searching user not found',
            }
            return jsonify(response_object), 404

    blacklist = None

    if requester_id != user_id:
        try:
            auth_json = {'requester_id': requester_id }
            response = requests.get("%s/blacklist" % (BLACKLIST_ENDPOINT), json=auth_json,
                                    timeout=REQUESTS_TIMEOUT_SECONDS)
            
            if response.status_code != 200:
                response_object = {
                    'status': 'failure',
                    'description': 'Error in retrieving blacklist',
                }
                return jsonify(response_object), response.status_code

            json_payload = response.json()
            blocked = json_payload['blocked']
            blocking = json_payload['blocking']

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            response_object = {
            'status': 'failure',
            'message': 'Error in retrieving blacklist',
            }
            return jsonify(response_object), 500

        if user.id in blocked or user.id in blocking:
            response_object = {
            'status': 'failure',
            'message': 'Unauthorized',
            }
            return jsonify(response_object), 401

    filename = 'default'

    # if has picture, then his filename is <id>.jpeg
    if (user.has_picture):
        filename = str(user_id)

    filename_100 = filename + "_100.jpeg"
    filename += ".jpeg"

    path_to_retrieve = os.path.join(os.getcwd(), 'mib', 'static', 'pictures', filename)
    path_to_retrieve_100 = os.path.join(os.getcwd(), 'mib', 'static', 'pictures', filename_100)

    data_img = None
    data_img_100 = None
    try:
        with open(path_to_retrieve, mode='rb') as image:
            data_img = base64.encodebytes(image.read()).decode('utf-8')

        with open(path_to_retrieve_100, mode='rb') as image_100:
            data_img_100 = base64.encodebytes(image_100.read()).decode('utf-8')
    except Exception:
        response_object = {
            'status': 'failure',
            'description': 'Error while retrieve the images',
        }
        return jsonify(response_object), 500

    response_object = {
        'status': 'success',
        'description' : 'Profile pictures retrieved',
        'image': data_img,
        'image_100': data_img_100
    }

    return jsonify(response_object), 200


def get_users_list():
    
    # Retrieving the list of available users
    
    data = request.get_json()
    requester_id = data.get('requester_id')

    user = UserManager.retrieve_by_id(requester_id)

    if user is None:
        response_object = {
            'status': 'failure',
            'description': 'User not found',
        }
        return jsonify(response_object), 404

    blacklist = None

    try:
        auth_json = {'requester_id': requester_id }
        response = requests.get("%s/blacklist" % (BLACKLIST_ENDPOINT), json=auth_json,
                                timeout=REQUESTS_TIMEOUT_SECONDS)
        
        if response.status_code != 200:
            response_object = {
                'status': 'failure',
                'description': 'Error in retrieving blacklist',
            }
            return jsonify(response_object), response.status_code

        json_payload = response.json()
        blocked = json_payload['blocked']
        blocking = json_payload['blocking']
        blacklist = []
        for ob in blocked:
            blacklist.append(ob)
        for ob in blocking:
            blacklist.append(ob)

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        response_object = {
            'status': 'failure',
            'description': 'Error in retrieving blacklist',
        }
        return jsonify(response_object), 500

    users = UserManager.retrieve_users_by_blacklist(requester_id, blacklist)

    users_json = [user.serialize() for user in users]

    response_object = {
        'status': 'success',
        'description': 'Users list retrieved',
        'users': users_json
    }

    return jsonify(response_object), 200


def get_user_by_id(user_id):
    """
    Get a user by its id.

    :param user_id: user it
    :return: json response
    """
    data = request.get_json()
    requester_id = data.get('requester_id')

    # check that the searched user exists
    user = UserManager.retrieve_by_id(user_id)
    if user is None:
        response = {
            'status': 'failure',
            'description': 'Searched user not found',
        }
        return jsonify(response), 404

    if requester_id != user_id:

        # check that the searching user exists
        current_user = UserManager.retrieve_by_id(requester_id)
        if current_user is None:
            response = {
                'status': 'failure',
                'description': 'Requester user not found',
            }
            return jsonify(response), 404

        blacklist = None

        try:
            auth_json = {'requester_id': requester_id }
            response = requests.get("%s/blacklist" % (BLACKLIST_ENDPOINT), json=auth_json,
                                    timeout=REQUESTS_TIMEOUT_SECONDS)
            
            if response.status_code != 200:
                response_object = {
                    'status': 'failure',
                    'description': 'Error in retrieving blacklist',
                }
                return jsonify(response_object), response.status_code

            json_payload = response.json()
            blocked = json_payload['blocked']
            blocking = json_payload['blocking']

        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout):
            response_object = {
                'status': 'failure',
                'description': 'Error in retrieving blacklist',
            }
            return jsonify(response_object), 500

        if user.id in blocked or user.id in blocking:
            response_object = {
                'status': 'failure',
                'description': 'Forbidden',
            }
            return jsonify(response_object), 403

    response_object = {
        'status': 'success',
        'description': 'User retrivied',
        'user': user.serialize()
    }
    return jsonify(response_object), 200


def get_user_by_email(user_email):
    """
    Get a user by its current email.

    :param user_email: user email
    :return: json response
    """

    # check that the searched user exists
    user = UserManager.retrieve_by_email(user_email)
    if user is None:
        response = {
            'status': 'failure',
            'description': 'Searched user not found',
        }
        return jsonify(response), 404

    response_object = {
        'status': 'success',
        'description': 'User retrivied',
        'user': user.serialize()
    }
    return jsonify(response_object), 200


def search_users():

    data = request.get_json()
    requester_id = data.get('requester_id')
    firstname = data.get('firstname')
    lastname = data.get('lastname')
    email = data.get('email')

    current_user = UserManager.retrieve_by_id(requester_id)

    if current_user is None:
        response_object = {
            'status': 'failure',
            'description': 'Current user not found',
        }
        return jsonify(response_object), 404

    if firstname == '' and lastname == '' and email == '':
        response_object = {
            'status': 'failure',
            'description': 'No parameters given',
        }
        return jsonify(response_object), 400

    # retrieving blacklist
    blacklist = None

    try:
        auth_json = {'requester_id': requester_id }
        response = requests.get("%s/blacklist" % (BLACKLIST_ENDPOINT), json=auth_json,
                                timeout=REQUESTS_TIMEOUT_SECONDS)
        
        if response.status_code != 200:
            response_object = {
                'status': 'failure',
                'description': 'Error in retrieving blacklist',
            }
            return jsonify(response_object), response.status_code

        json_payload = response.json()
        blocked = json_payload['blocked']
        blocking = json_payload['blocking']
        blacklist = []
        for ob in blocked:
            blacklist.append(ob)
        for ob in blocking:
            blacklist.append(ob)

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        response_object = {
            'status': 'failure',
            'description': 'Error in retrieving blacklist',
        }
        return jsonify(response_object), 500

    # searching matching users
    matching_users = UserManager.search_users(requester_id,firstname,lastname,email,blacklist)
    
    users_json = []

    for user in matching_users:
        users_json.append(user.serialize())

    response_object = {
        'status': 'success',
        'message': 'Matching users found',
        'users': users_json
    }

    return response_object, 200


def spend_lottery_points():
    data = request.get_json()
    requester_id = data.get('requester_id')

    current_user = UserManager.retrieve_by_id(requester_id)

    if current_user is None:
        response_object = {
            'status': 'failure',
            'description': 'Current user not found',
        }
        return jsonify(response_object), 404

    if current_user.lottery_points < 10:
        response_object = {
            'status': 'failure',
            'description': 'Not enough lottery points to delete a pending message',
        }
        return jsonify(response_object), 403

    current_user.lottery_points -= 10
    UserManager.update_user(current_user)

    response_object = {
            'status': 'success',
            'description': 'Lottery points spent',
        }
    return jsonify(response_object), 200