from .view_test import ViewTest
from faker import Faker


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

    def test_register_and_get_user(self):
        # get a non-existent user
        rv = self.client.get('/users/0')
        assert rv.status_code == 404

        # registering a new user
        json_user = { 'email' : 'prova4@mail.com' , 'firstname': 'Barbara', 'lastname': 'Verdi', 
        'password' : 'prova123', 'date_of_birth': '1990-05-25'} 
        rv = self.client.post('/register', json = json_user)
        self.assertEqual(rv.status_code, 201)

        # retrieving the user by her email to check her id
        rv = self.client.get('/user_email/prova4@mail.com')
        test_id = rv.get_json()
        assert rv.status_code == 200

        # get an existent user
        #user = self.login_test_user()
        rv = self.client.get('/users/%s/list/%s'% (str(test_id['id']), str(test_id['id'])))
        assert rv.status_code == 200
    
    def test_get_user_by_email(self):

        # get a non-existent user with faked email
        rv = self.client.get('/user_email/%s' % TestUsers.faker.email())
        assert rv.status_code == 404
        # get an existent user
        user = self.login_test_user()
        rv = self.client.get('/user_email/%s' % user.email)
        assert rv.status_code == 200

    def test_modify_user_data(self):
        pass
   
    def test_get_recipients_list(self):
        # required mocking blacklist
        pass

    def test_get_arbitrary_user_info(self):
        # required mocking blacklist
        pass

    def test_unregister(self):
        pass