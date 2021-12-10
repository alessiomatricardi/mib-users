from mib.background import lottery_notification
import unittest

class CeleryTest(unittest.TestCase):

    def test_task(self):

        task = lottery_notification.apply()
        self.assertEqual(task.result,True)