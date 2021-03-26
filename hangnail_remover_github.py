#!/usr/bin/env python3

import json
import sys
import os

import click
from loguru import logger
import ghapi

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
        with open(os.path.join('./',os.readlink('hangnail_data.json')), 'r') as file_handle:
            data = json.load(file_handle)
    except Exception as error_message:
        logger.error(error_message)
        sys.exit(1)

    for user in data:
        if 'github_username' in user:
            logger.debug("Blocking: {}", user.get('github_username'))




if __name__ == '__main__':
    cli()
