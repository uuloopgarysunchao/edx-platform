"""
Tests for the Sending activation email celery tasks
"""

import mock

from django.test import TestCase
from django.conf import settings
from student.tasks import send_activation_email


class SendActivationEmailTestCase(TestCase):
    """
    Test for send activation email to user
    """
    @mock.patch('time.sleep', mock.Mock(return_value=None))
    @mock.patch('student.tasks.log')
    @mock.patch('django.contrib.auth.models.User')
    def test_send_email(self, mock_user, mock_log):
        """
        Test Send activation email exception
        """
        from_address = "task_testing@edX.com"
        mock_user.email_user.side_effect = Exception
        email_max_attempts = settings.RETRY_ACTIVATION_EMAIL_MAX_ATTEMPTS

        with self.assertRaises(Exception):
            send_activation_email(mock_user, 'Task_test', 'Task_test_message', from_address)

        # Asserts sending email retry logging.
        for attempt in xrange(1, email_max_attempts):
            mock_log.info.assert_any_call(
                "Retrying sending email to user {dest_addr}, attempt # {attempt} of {max_attempts}".format(
                    dest_addr=mock_user.email,
                    attempt=attempt,
                    max_attempts=email_max_attempts
                ))
        # Asserts that the error was logged on crossing max retry attempts.
        mock_log.error.assert_called_with(
            'Unable to send activation email to user from "%s" to "%s"',
            from_address,
            mock_user.email,
            exc_info=True
        )
