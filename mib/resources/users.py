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
from werkzeug.security import check_password_hash

BLACKLIST_ENDPOINT = app.config['BLACKLIST_MS_URL']
REQUESTS_TIMEOUT_SECONDS = app.config['REQUESTS_TIMEOUT_SECONDS']

def register():
    """
    This method allows the registration of a new user.
    Called by /register.
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


def unregister():
    """
    Unregister the user.
    Called by /unregister.
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
    Called by /profile/data
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
    Called by /profile/password
    if it succeeds return {'status': 'success','message': 'Modified'}
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


def modify_content_filter():
    """
    Used to enable/disable content_filter 
    Called by /profile/content_filter
    if it succeds, returns {'status': 'success','message': 'Modified', 'enabled': True/False}
    if it fails return {'status': 'failure','message': 'User not found'}
    """
    post_data = request.get_json()
    id = post_data.get('id')
    content_filter = post_data.get('content_filter')

    user = UserManager.retrieve_by_id(id)

    if user is None:
        response_object = {
            'status': 'failure',
            'message': 'User not found',
        }
        return jsonify(response_object), 404
    
    user.content_filter_enabled = content_filter
    UserManager.update_user(user)
    
    response_object = {
        'status': 'success',
        'message': 'Modified',
        'enabled': content_filter
    }
    return jsonify(response_object), 200
    

def modify_profile_picture():
    '''
    TODO ADD FEATURE INSIDE API GATEWAY WHICH SERIALIZES THE IMAGE IN A JSON { id: <id>, base64: <base64>}

    data = {}
    with open('some.gif', mode='rb') as file:
        img = file.read()
    data['img'] = base64.encodebytes(img).decode('utf-8')

    print(json.dumps(data))
    '''

    """
    Used to modify profile picture 
    Called by /profile/picture
    if it succeds return {'status': 'success','message': 'Modified'}
    if it fails return {'status': 'failure','message': 'User not found'}
    """
    post_data = request.get_json()
    id = post_data.get('id')
    img_base64 = post_data.get('image')

    user = UserManager.retrieve_by_id(id)

    if user is None:
        response_object = {
            'status': 'failure',
            'message': 'User not found',
        }
        return jsonify(response_object), 404
    
    # decoding image
    img_data = BytesIO(base64.b64decode(img_base64))
    
    # store it, in case of a previously inserted image it's going to be overwritten
    try:

        # save image in 256x256
        img = Image.open(img_data)
        img = img.convert('RGB') # in order to support also Alpha transparency images such as PNGs
        img = img.resize([256, 256], Image.ANTIALIAS)
        path_to_save = os.path.join(os.getcwd(), 'mib', 'static', 'pictures', str(id) + '.jpeg')
        img.save(path_to_save, "JPEG", quality=100, subsampling=0)

        # save image in 100x100
        img = Image.open(img_data)
        img = img.convert('RGB')  # in order to support also Alpha transparency images such as PNGs
        img = img.resize([100, 100], Image.ANTIALIAS)
        path_to_save = os.path.join(os.getcwd(), 'mib', 'static', 'pictures', str(id) + '_100.jpeg')
        img.save(path_to_save, "JPEG", quality=100, subsampling=0)

    except Exception:
        response_object = {
            'status': 'failure',
            'message': 'Error in saving the image',
        }
        return jsonify(response_object), 500
    
    user.has_picture = True
    UserManager.update_user(user)

    response_object = {
        'status': 'success',
        'message': 'Modified',
    }
    return jsonify(response_object), 200


def get_profile_picture(current_user_id,user_id):

    
    user = UserManager.retrieve_by_id(user_id)

    if user is None:
        response_object = {
            'status': 'failure',
            'message': 'User not found',
        }
        return jsonify(response_object), 404
    
    current_user = UserManager.retrieve_by_id(current_user_id)
    if current_user is None:
        response = {'status': 'Current user not present'}
        return jsonify(response), 404

    blacklist = None

    try:
        blacklist_response = requests.get("%s/blacklist/%s" % (BLACKLIST_ENDPOINT, str(current_user_id)),
                                timeout=REQUESTS_TIMEOUT_SECONDS)
        json_payload = blacklist_response.json()
        if blacklist_response.status_code == 200:
            blacklist = json.loads(json_payload['blacklist'])
        else:
            raise RuntimeError('Server has sent an unrecognized status code %s' % blacklist_response.status_code)

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        response_object = {
        'status': 'failure',
        'message': 'Error in retrieving blacklist',
        }
        return jsonify(response_object),500

    if user.id in blacklist:
        response_object = {
        'status': 'failure',
        'message': 'Unauthorized',
        }
        return jsonify(response_object),401

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
            'message': 'Error while retrieve the images',
        }
        return jsonify(response_object), 500

    response_object = {
        'status': 'success',
        'image': data_img,
        'image_100': data_img_100
    }

    return jsonify(response_object), 200


# /users -> /users_list/<user_id>
def get_users_list(current_user_id):
    # TODO should be provided with the request
    # TODO COMMENTS
    # blacklisted = [3, 4]

    user = UserManager.retrieve_by_id(current_user_id)

    if user is None:
        response_object = {
            'status': 'failure',
            'message': 'User not found',
        }
        return jsonify(response_object), 404
    
    blacklist = None

    try:
        blacklist_response = requests.get("%s/blacklist/%s" % (BLACKLIST_ENDPOINT, str(current_user_id)),
                                timeout=REQUESTS_TIMEOUT_SECONDS)
        json_payload = blacklist_response.json()
        if blacklist_response.status_code == 200:
            blacklist = json.loads(json_payload['blacklist'])
        else:
            raise RuntimeError('Server has sent an unrecognized status code %s' % blacklist_response.status_code)

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        response_object = {
            'status': 'failure',
            'message': 'Error in retrieving blacklist',
        }
        return jsonify(response_object), 500

    
    users = UserManager.retrieve_users_by_blacklist(current_user_id, blacklist)

    users_json = [user.serialize() for user in users]

    response_object = {
        'status': 'success',
        'message': 'Users list retrived',
        'users' : users_json
    }
    
    return jsonify(response_object), 200


# /users/<user_id> or /profile
def get_user(current_user_id,user_id):
    """
    Get a user by its current id.

    :param user_id: user it
    :return: json response
    """

    user = UserManager.retrieve_by_id(user_id)
    if user is None:
        response = {'status': 'User not present'}
        return jsonify(response), 404

    current_user = UserManager.retrieve_by_id(current_user_id)
    if current_user is None:
        response = {
            'status': 'Current user not present'
        }
        return jsonify(response), 404

    blacklist = None

    if current_user_id != user_id:

        try:
            blacklist_response = requests.get("%s/blacklist/%s" % (BLACKLIST_ENDPOINT, str(current_user_id)),
                                    timeout=REQUESTS_TIMEOUT_SECONDS)
            json_payload = blacklist_response.json()
            if blacklist_response.status_code == 200:
                blacklist = json.loads(json_payload['blacklist'])
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % blacklist_response.status_code)

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            response_object = {
                'status': 'failure',
                'message': 'Error in retrieving blacklist',
            }
            return jsonify(response_object), 500

        if user.id in blacklist:
            response_object = {
                'status': 'failure',
                'message': 'Unauthorized',
            }
            return jsonify(response_object), 401

    return jsonify(user.serialize()), 200


# TODO controllare se serve
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