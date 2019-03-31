import testtools
import cpat.slack_handler
from mock import patch

# Job no parenthesis
slack_data = {'type': 'message',
              'text': 'run-test_linux'}


class TestVault(testtools.TestCase):
    def test_validation(self, *_):
        err = cpat.slack_handler.SlackHandler.cmd_validation('run-jobname')
        self.assertIsNotNone(err)
        err = cpat.slack_handler.SlackHandler.cmd_validation('run-jobname()')
        self.assertIsNone(err)
        err = cpat.slack_handler.SlackHandler.cmd_validation('run-jobname(key1=a,key2=b)')
        self.assertIsNone(err)
        err = cpat.slack_handler.SlackHandler.params_validation('a,b')
        self.assertIn("Illegal params", err)
        err = cpat.slack_handler.SlackHandler.params_validation('key1=a,key2=b')
        self.assertNotIn("Illegal params", err)

    @patch('cpat.slack_handler.SlackHandler.post_message', return_value='run-test_linux')
    def test_job_no_parenthesis(self, *_):
        result = cpat.slack_handler.is_valid_jenkins_cmd(cpat.slack_handler.SlackHandler, slack_data)
        self.assertIn("Illegal cmd:", str(result))
