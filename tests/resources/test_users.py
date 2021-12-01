from .view_test import ViewTest
from faker import Faker
import json
import responses
from mib import create_app


class TestUsers(ViewTest):
    faker = Faker('it_IT')

    @classmethod
    def setUpClass(cls):
        super(TestUsers, cls).setUpClass()

    '''
    def test_delete_user(self):
        user = self.login_test_user()
        rv = self.client.delete('/user/%d' % user.id)
        assert rv.status_code == 202
    '''

    def test_01_register_and_get(self):
        # get a non-existent user
        data = {'requester_id': 1}
        rv = self.client.get('/users/0', json=data)
        assert rv.status_code == 404

        # registering a new user
        json_user = { 'email' : 'prova4@mail.com' , 'firstname': 'Barbara', 'lastname': 'Verdi', 
        'password' : 'prova123', 'date_of_birth': '1990-05-25'} 
        rv = self.client.post('/register', json = json_user)
        self.assertEqual(rv.status_code, 201)

        # retrieving the user by her email to check her id
        rv = self.client.get('/users/prova4@mail.com')

        assert rv.status_code == 200
        test_id = rv.get_json()['user']

        # get an existent user
        #user = self.login_test_user()
        data = {'requester_id' : test_id['id']}
        rv = self.client.get('/users/%s'% (str(test_id['id'])), json=data)
        assert rv.status_code == 200
        
    
    def test_02_get_user_by_email(self):

        # get a non-existent user with faked email
        data = {'requester_id': 1}
        rv = self.client.get('/users/%s' % TestUsers.faker.email(),
                             json=data)
        assert rv.status_code == 404
        # get an existent user
        user = self.login_test_user()
        rv = self.client.get('/users/%s' % user.email)
        assert rv.status_code == 200


    def test_03_modify_user_data(self):
        
        # retrieve Barbara Verdi, our test dummy
        rv = self.client.get('/users/prova4@mail.com')
        
        assert rv.status_code == 200
        test_id = rv.get_json()['user']

        # personal data modification variables
        json_user_success = { 'requester_id' : test_id['id'] , 'firstname': 'Barbaro', 'lastname': 'Verde', 'date_of_birth': '1991-06-26'} 
        json_user_failure = { 'requester_id' : 200, 'firstname': 'Barbara', 'lastname': 'Verdi', 'date_of_birth': '1990-05-25'} 
        
        # try with wrong id and expect a 404 response
        rv = self.client.patch('/profile/data', json = json_user_failure)
        self.assertEqual(rv.status_code, 404)

        # try with correct id 
        rv = self.client.patch('/profile/data', json = json_user_success)
        self.assertEqual(rv.status_code, 200)

        # login with Barbara
        json_login = { 'email' : 'prova4@mail.com' , 'password': 'prova123'} 
        rv = self.client.post('/login', json = json_login)
        self.assertEqual(rv.status_code, 200)
  

        # password modification variables
        json_user_password_success= { 'requester_id' : test_id['id']  , 'old_password': 'prova123', 'new_password': 'abcd1234', 'repeat_new_password': 'abcd1234'} 
        json_user_password_wrong_id= { 'requester_id' : 200 , 'old_password': 'prova123', 'new_password': 'abcd1234', 'repeat_new_password': 'abcd1234'}
        json_user_password_wrong_old_pwd= { 'requester_id' : test_id['id']  , 'old_password': 'prova12345', 'new_password': 'abcd1234', 'repeat_new_password': 'abcd1234'}
        json_user_password_unchanged= { 'requester_id' : test_id['id']  , 'old_password': 'prova123', 'new_password': 'prova123', 'repeat_new_password': 'abcd1234'}
        json_user_password_not_corresponding= { 'requester_id' : test_id['id']  , 'old_password': 'prova123', 'new_password': 'abcd1234', 'repeat_new_password': 'wrongpwd'}
   
        # passing wrong id
        rv = self.client.patch('/profile/password', json = json_user_password_wrong_id)
        self.assertEqual(rv.status_code, 404)

        # passing wrong old password
        rv = self.client.patch('/profile/password', json = json_user_password_wrong_old_pwd)
        self.assertEqual(rv.status_code, 401)

        # passing the same password as the new one
        rv = self.client.patch('/profile/password', json = json_user_password_unchanged)
        self.assertEqual(rv.status_code, 400)

        # repeating wrongly the new password 
        rv = self.client.patch('/profile/password', json = json_user_password_not_corresponding)
        self.assertEqual(rv.status_code, 400)

        # passing everything as it should be
        rv = self.client.patch('/profile/password', json = json_user_password_success)
        self.assertEqual(rv.status_code, 200)

        # changing content filter test variables
        json_content_filter_enabling = {'requester_id': test_id['id'] , 'content_filter': True}
        json_content_filter_disabling = {'requester_id': test_id['id'] , 'content_filter': False}
        json_content_filter_wrong_id = {'requester_id': 200 , 'content_filter': True}

        # passing wrong id
        rv = self.client.patch('/profile/content_filter', json = json_content_filter_wrong_id)
        self.assertEqual(rv.status_code, 404)
        
        # enabling content filter
        rv = self.client.patch('/profile/content_filter', json = json_content_filter_enabling)
        self.assertEqual(rv.status_code, 200)

        # disabling content filter
        rv = self.client.patch('/profile/content_filter', json = json_content_filter_disabling)
        self.assertEqual(rv.status_code, 200)


    def test_04_pictures(self):

        # retrieve Barbara Verdi, our test dummy
        rv = self.client.get('/users/prova4@mail.com')
        
        assert rv.status_code == 200
        test_id = rv.get_json()['user']

        # modify profile picture test variables
        json_pfp_wrong_id = {'requester_id': 200, 'image': 'whatever'}
        rv = self.client.put('/profile/picture', json = json_pfp_wrong_id)
        self.assertEqual(rv.status_code, 404)

        #TODO: add testing for the rest of /profile/picture updating Barbara pfp

        # retrieving a profile picture with a wrong id
        rv = self.client.get('/users/200', json = {'requester_id': 200})
        self.assertEqual(rv.status_code, 404)

        #TODO: add testing for the rest of /profile/<current_user_id>/picture/<current_user_id> for retrieving Barbara pfp

    @responses.activate
    def test_05_get_recipients_list(self):
        # required mocking blacklist

        # retrieve Barbara Verdi, our test dummy
        rv = self.client.get('/users/prova4@mail.com')
        
        assert rv.status_code == 200
        test_id = rv.get_json()['user']

        # retrieving recipients list for a non-existing user
        rv = self.client.get('/users', json = {'requester_id': 200})
        self.assertEqual(rv.status_code, 404)

        # retrieving recipients list without having the Blacklist microservice mocked
        rv = self.client.get('/users',  json = {'requester_id': test_id['id']})
        self.assertEqual(rv.status_code, 500)

        # mocking
        app = create_app()

        BLACKLIST_ENDPOINT = app.config['BLACKLIST_MS_URL']
        REQUESTS_TIMEOUT_SECONDS = app.config['REQUESTS_TIMEOUT_SECONDS']

        responses.add(responses.GET, "%s/blacklist/%s" % (BLACKLIST_ENDPOINT, str(test_id['id'])),
                  json={ "blacklist": "[]", 
                         "message": "Blacklist successfully retrieved", 
                        "status": "success"
                       }, 
                       status=200)

        rv = self.client.get('/users',  json = {'requester_id': test_id['id']})
        self.assertEqual(rv.status_code, 200)
        print(rv.get_json())

    def test_get_arbitrary_user_info(self):
        # required mocking blacklist
        pass

    def test_unregister(self):
        pass
