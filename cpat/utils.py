import re
import os
import sys
import datetime

import logger
# from . import logger


lgr = logger.init()


def get_datetime():
    date_time = datetime.datetime.strftime(
        datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
    date, time = date_time.split(' ')
    return date_time, date, time


def get_version(repo_dir):
    """Retrieves the module version from setup.py.

    setup.py holds the python version
    therefore need to change the return version to build version.
    For example python version:3.2a1 build version: 3.2m1
    """
    setup_file = os.path.join(repo_dir, 'setup.py')
    if os.path.exists(setup_file):
        ver = os.popen("python {0}/setup.py --version".format(repo_dir)).\
            read().strip('\n')
        if ver:
            return ver.replace('a', 'm')
    else:
        return None


def get_module_name(repo_dir):
    """Retrieves the module name from setup.py.

    """
    setup_file = os.path.join(repo_dir, 'setup.py')
    if os.path.exists(setup_file):
        name = os.popen("python {0}/setup.py --name".format(repo_dir)).\
            read().strip('\n')
        if name:
            return name
    else:
        return None


def get_env_variable(variable_name):
    """Get environment variable and exit if not found"""
    value = os.environ.get(variable_name, None)
    if not value:
        lgr.error('%s not set in environment', variable_name)
        sys.exit(1)
    return value


def is_match(pattern, str):
    return re.match(pattern, str)
