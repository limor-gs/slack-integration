#####
# ChatBot for Slack
#####
import re
import os
import json
import time
from slackclient import SlackClient

import utils
import logger
import jenkins_handler
# from . import utils
# from . import logger
# from . import jenkins_handler


CMD_PREFIX = 'run-'
CMD_PATTERN = r'{}\w+(\(.*)\)'.format(CMD_PREFIX)
JOB_PATTERN = r'{}(.*)\('.format(CMD_PREFIX)
PARAMS_PATTERNS = r'\((.*)\)'

lgr = logger.init()


class SlackHandler():
    def __init__(self, channel_name):
        self.bot_token = utils.get_env_variable('SLACK_BOT_TOKEN')
        self.http_proxy = utils.get_env_variable('HTTP_PROXY')
        self.jenkins_url = utils.get_env_variable('JENKINS_URL')
        self.jenkins_user = utils.get_env_variable('JENKINS_USER')
        self.jenkins_pwd = utils.get_env_variable('JENKINS_PWD')
        self.channel_name = channel_name
        lgr.info('Connecting Slack...')
        self.connection = SlackClient(
            self.bot_token, proxies={"http": self.http_proxy, "https": self.http_proxy})
        lgr.info(self.connection)
        # self.bot_id = self.connection.api_call("auth.test")["user_id"]
        self.channel_list = self.connection.api_call("channels.list").get("channels", [])
        self.channel_id = self.find_channels_id()
        self.jenkins = jenkins_handler.JenkinsHandler(
            url=self.jenkins_url, username=self.jenkins_user, password=self.jenkins_pwd)

    def post_message(self, text):
        self.connection.api_call(
            "chat.postMessage",
            channel=self.channel_id,
            text=text
        )

    def find_channels_id(self):
        """Find channel id by its name

        channel_name (string): name of finding channel
        channel_list (list): all channel list in the workspace
        return -> channel_id
        """
        match = [ch.get("id") for ch in self.channel_list if ch.get("name") == self.channel_name]
        return match[0]

    @staticmethod
    def get_jenkins_job(cmd):
        result = re.search(JOB_PATTERN, cmd)
        return result.group(1)

    @staticmethod
    def get_valid_jenkins_params(cmd):
        params_match = re.search(PARAMS_PATTERNS, cmd)
        if params_match and params_match.group(1):
            params = params_match.group(1)
            return SlackHandler.params_validation(params)
        else:
            return ''

    @staticmethod
    def cmd_validation(cmd):
        if not utils.is_match(CMD_PATTERN, cmd):
            err_msg = f"Illegal cmd: {cmd}, must be of format: {CMD_PREFIX}<jobname>(params)\n" \
                f"e.g job with params {CMD_PREFIX}blade_publish(key=value)\n" \
                f"e.g job without params {CMD_PREFIX}blade_publish()"
            return err_msg
        else:
            return None

    @staticmethod
    def params_validation(params):
        try:
            params_dict = dict(x.split('=') for x in params.split(';'))
            return params_dict
        except Exception as e:
            return f"Illegal params ({e})"


def is_valid_jenkins_cmd(sc, new_data):
    cmd = new_data.get("text")
    err = SlackHandler.cmd_validation(cmd)
    if err:
        lgr.error(err)
        sc.post_message(err)
        return err, None
    else:
        job = SlackHandler.get_jenkins_job(cmd)
        params = SlackHandler.get_valid_jenkins_params(cmd)
        if "Illegal params" in params:
            os.environ['http_proxy'] = utils.get_env_variable('HTTP_PROXY')
            os.environ['https_proxy'] = utils.get_env_variable('HTTP_PROXY')
            try:
                params_list = sc.jenkins.get_param_list(job)
            except Exception as e:
                err_msg = f'Jenkins failed: {e}'
                lgr.error(err_msg)
                sc.post_message(err_msg)
                return err_msg, None
            err_msg = f"{params}, must be in the format: key1=value;key2=value\n" \
                f"job: {job}, actual params list: {json.dumps(params_list)}"
            lgr.error(err_msg)
            sc.post_message(err_msg)
            return err_msg, None
        else:
            return job, params


if __name__ == "__main__":
    """Running Bot
    """
    channel_name = utils.get_env_variable('CHANNEL_NAME')
    sc = SlackHandler(channel_name=channel_name)
    if sc.connection.rtm_connect(with_team_state=False):
        lgr.info(f"I'm online, please order me on channel [{channel_name}]...")

        while True:
            data = sc.connection.rtm_read()
            if not data or \
                    data[0].get("type") != "message" or \
                    data[0].get("subtype") == "bot_message" or \
                    not data[0].get("text").startswith(CMD_PREFIX):
                pass
            else:
                jenkins_job, jenkins_params = is_valid_jenkins_cmd(sc, data[0])
                if "Illegal" not in jenkins_job:
                    try:
                        os.environ['http_proxy'] = utils.get_env_variable('HTTP_PROXY')
                        os.environ['https_proxy'] = utils.get_env_variable('HTTP_PROXY')
                        msg = f"Running job: {jenkins_job}..."
                        sc.post_message(msg)
                        sc.jenkins.build(jenkins_job, jenkins_params)
                    except Exception as e:
                        err_msg = f'Jenkins failed: {e}'
                        lgr.error(err_msg)
                        sc.post_message(err_msg)
            time.sleep(1)
    else:
        lgr.error('Something wrong, please check your internet connection!')
