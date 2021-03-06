from .view_test import ViewTest
from faker import Faker


class TestAuth(ViewTest):

    faker = Faker('it_IT')

    @classmethod
    def setUpClass(cls):
        super(TestAuth, cls).setUpClass()

    def test_login(self):
        # login for a customer
        user = self.login_test_user()

        # login with a wrong password
        data = {
            'email': user.email,
            'password': TestAuth.faker.password()
        }

        # login with a wrong email
        data2 = {
            'email': 'not_an_email@ondb.it',
            'password': TestAuth.faker.password()
        }

        response = self.client.post('/login', json=data2)
        json_response = response.json
        assert response.status_code == 404


        response = self.client.post('/login', json=data)
        json_response = response.json

        assert response.status_code == 401
        assert json_response["status"] == 'failure'




    
    


