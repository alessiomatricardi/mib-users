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

    def test_get_user_by_id(self):
        # get a non-existent user
        data = {'requester_id': 1}
        rv = self.client.get('/users/0', json=data)
        assert rv.status_code == 404
        # get an existent user
        user = self.login_test_user()

        # mocking
        app = create_app()

        BLACKLIST_ENDPOINT = app.config['BLACKLIST_MS_URL']

        responses.add(responses.GET,
                      "%s/blacklist/%s" % (BLACKLIST_ENDPOINT, str(user.id)),
                      json={'status': 'Current user not present'},
                      status=200)

        rv = self.client.get('/users/%d' % user.id, json=data)
        assert rv.status_code == 200

    def test_get_user_by_email(self):
        # get a non-existent user with faked email
        data = {'requester_id': 1}
        rv = self.client.get('/users/%s' % TestUsers.faker.email(),
                             json=data)
        assert rv.status_code == 404
        # get an existent user
        user = self.login_test_user()

        # mocking
        app = create_app()

        BLACKLIST_ENDPOINT = app.config['BLACKLIST_MS_URL']

        responses.add(responses.GET,
                      "%s/blacklist/%s" %
                      (BLACKLIST_ENDPOINT, str(user.id)),
                      json={'status': 'Current user not present'},
                      status=200)

        rv = self.client.get('/users/%s' % user.email, json=data)
        assert rv.status_code == 200