import os
import sys
import click
import requests

from jenkinsapi.jenkins import Jenkins
from jenkinsapi.utils.requester import Requester

import utils
import logger
# from . import utils
# from . import logger


lgr = logger.init()


class JenkinsHandler:
    def __init__(self, url, username, password, params=None):
        if not all([url, username, password]):
            lgr.error('server / username / password variables were not provided.')
            sys.exit(1)
        os.environ['http_proxy'] = utils.get_env_variable('HTTP_PROXY')
        os.environ['https_proxy'] = utils.get_env_variable('HTTP_PROXY')
        requests.packages.urllib3.disable_warnings()
        for i in range(0, 50):
            try:
                lgr.info(f"Connecting Jenkins... retry {i}")
                self.jenkins = Jenkins(url, requester=Requester(username, password, baseurl=url, ssl_verify=False))
                lgr.info(self.jenkins)
            except OSError:
                continue
            break

    def build(self, job_name, params):
        lgr.info(f"Building a Jenkins job: {job_name}, params: {params}") # noqa
        job = self.jenkins[job_name]
        job.invoke(build_params=params)
        # qi = job.invoke(build_params=params)
        # Block this script until build is finished
        # if qi.is_queued() or qi.is_running():
        #     qi.block_until_complete()
        #
        # build = qi.get_build()
        # status = build.get_status()
        # lgr.info(f'Build status: {status}')
        # return status, build

    def get_param_list(self, job_name):
        job = self.jenkins[job_name]
        return job.get_params_list()

    def get_job_info(self, job_name):
        job = self.jenkins.get_job(job_name)
        for build in job.get_build_dict():
            print(job.get_build(build).get_status())


@click.group('jenkins')
def jenkins():
    """Jenkins handling related function
    """
    pass


@click.command()
@click.option('--url', required=True,
              help='Jenkins url',
              envvar='JENKINS_URL')
@click.option('--username', required=True,
              help='Jenkins username',
              envvar='JIRA_USER')
@click.option('--password', required=True,
              help='Jenkins password',
              envvar='JENKINS_PASSWORD')
@click.option('--job-name', required=True,
              help='Jenkins job name',
              envvar='JOB_NAME')
@click.option('--params', default=None,
              help='Jenkins job parameters',
              envvar='PARAMS')
@click.option('-v', '--verbose', default=False, is_flag=True)
def build(url, username, password, job_name, params, verbose):
    logger.set_global_verbosity_level(lgr, verbose)
    jenkins = JenkinsHandler(url=url, username=username,  password=password)
    jenkins.build(job_name, params)


jenkins.add_command(build)
