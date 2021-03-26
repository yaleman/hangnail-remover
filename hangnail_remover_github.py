#!/usr/bin/env python3

import json
import sys
import os

import click
from loguru import logger
from ghapi.all import GhApi

def setup_logging(debug: bool, logger_object):
    """ sets up logging """
    if os.environ.get('LOGURU_LEVEL'):
        return True
    if not debug:
        logger_object.remove()
        logger_object.add(sys.stdout,
                          level="INFO",
                          format='<level>{message}</level>' #pylint: disable=line-too-long,
                          )
    return True


@click.command()
@click.option('--debug','-d', is_flag=True, default=False)
@click.option('--update','-u', is_flag=True, default=False)
def cli(debug:bool, update:bool):
    """ do the needful """
    setup_logging(debug, logger)

    try:
        with open('hangnail_data.json', 'r') as file_handle:
            data = json.load(file_handle)
    except Exception as error_message:
        logger.error(error_message)
        sys.exit(1)

    try:
        from config import GITHUB_TOKEN
    except ImportError:
        GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    if not GITHUB_TOKEN:
        logger.error("Couldn't load github token")
        sys.exit(1)

    api = GhApi(token=GITHUB_TOKEN)
    logger.debug("Current user: {}",api.users.get_authenticated().login)

    currently_blocked = api.users.list_blocked_by_authenticated() # this doesn't work, wtf?
    for user in currently_blocked:
        logger.debug("B: {}", user)

    #for user in data:
    #    if 'github_username' in user:
    #        logger.debug("Blocking: {}", user.get('github_username'))

            #https://docs.github.com/en/rest/reference/users#block-a-user
            # block_user = users.block(username)



if __name__ == '__main__':
    cli()
