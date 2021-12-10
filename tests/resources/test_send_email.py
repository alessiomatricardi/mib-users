import unittest
from mib import create_app
from mib.emails import send_email

class TestNewMessage(unittest.TestCase):
    
    def test_send_email(self):

        app = create_app()

        with app.app_context():
            
            # email correctly sent 
            msg = f'Subject: SUBJECT\n\nTEXT.'
            result = send_email("prova@mail.com", msg)
            self.assertEqual(True, result)
            
            # email not correctly sent
            msg = f'Subject: SUBJECT\n\nTEXT.'
            result = send_email('not_an_email', msg)
            self.assertEqual(False, result)