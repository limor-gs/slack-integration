########
# Copyright (c) 2014 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.
import click

from . import logger
from . import jenkins_handler
# import logger
# import jenkins_handler

DEFAULT_CONFIG_FILE = 'config.yaml'

lgr = logger.init()
verbose_output = False


@click.group()
@click.option('-v', '--verbose', default=False, is_flag=True)
@click.pass_context
def main(ctx, verbose):
    """Main entry point to cli
    """
    ctx.obj['VERBOSE'] = verbose


# While we can simply add the command directly in the context of the group,
# adding the commands here allows us to review the structure of the tool.
main.add_command(jenkins_handler.jenkins)
# initialize the context's `object` object so that
# it is accessible for assignments.
main(obj={})
