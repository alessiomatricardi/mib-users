import unittest

from faker import Faker

from .model_test import ModelTest


class TestUser(ModelTest):

    faker = Faker()

    @classmethod
    def setUpClass(cls):
        super(TestUser, cls).setUpClass()

        from mib.models import user
        cls.user = user

    @staticmethod
    def assertUserEquals(value, expected):
        t = unittest.FunctionTestCase(TestUser)
        t.assertEqual(value.email, expected.email)
        t.assertEqual(value.password, expected.password)
        t.assertEqual(value.is_active, expected.is_active)
        t.assertEqual(value.authenticated, False)
        t.assertEqual(value.is_anonymous, expected.is_anonymous)

    @staticmethod
    def generate_random_user():
        email = TestUser.faker.email()
        firstname = TestUser.faker.first_name()
        lastname = TestUser.faker.last_name()
        date_of_birth = TestUser.faker.date()
        password = TestUser.faker.password()
        is_active = TestUser.faker.boolean()
        is_admin = TestUser.faker.boolean()
        authenticated = TestUser.faker.boolean()
        is_anonymous = TestUser.faker.boolean()
        

        from mib.models import User

        user = User(
            email=email,
            password=password,
            is_active=is_active,
            is_admin=is_admin,
            authenticated=authenticated,
            is_anonymous=is_anonymous,
            firstname=firstname,
            lastname=lastname,
            date_of_birth =date_of_birth,
            has_picture = False,
            lottery_points = 0,
            content_filter_enabled = False
        )

        return user

    def test_set_password(self):
        user = TestUser.generate_random_user()
        password = self.faker.password(length=15, special_chars=False, upper_case=False)
        #password = 'prova123'
        user.set_password(password)

        self.assertEqual(user.authenticate(password),True)
    
    def test_set_email(self):
        user = TestUser.generate_random_user()
        email = self.faker.email()
        user.set_email(email)
        self.assertEqual(email, user.email)

    def test_is_authenticated(self):
        user = TestUser.generate_random_user()
        self.assertFalse(user.is_authenticated())
