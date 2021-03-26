#!/usr/bin/env python3

import json
import os
import re
import sys
import time

import click
from git import Repo
import git.remote
from git.exc import InvalidGitRepositoryError
from loguru import logger
#import ghapi

if not os.path.exists("results/"):
    os.mkdir("results")
SOURCEREPO = 'sourcerepo'
SIGNATURE_DIR = f"{SOURCEREPO}/_data/signed"

USER_FINDERS = [
    re.compile(r"(?i)(http(s|))://(www\.|)github\.com/(?P<github_username>[^/\?]+)"),
    re.compile(r"(?i)(http(s|))://(www\.|)gitlab\.com/(?P<gitlab_username>[^/\?]+)"),
    re.compile(r"(?i)(http(s|))://(www\.|)twitter\.com/(?P<twitter_username>[^/\?]+)"),
    re.compile(r"(?i)(http(s|))://(www\.|)vk\.com/(?P<vk_username>[^/\?]+)"),
    re.compile(r"(?i)(http(s|))://(www\.|)linkedin\.com/in/(?P<linkedin_username>[^/\?]+)"),
]

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

def handle_link(link: str):
    """ handle a link """
    link = link.strip()
    for user_finder in USER_FINDERS:
        results = user_finder.match(link)
        if results:
            logger.debug(results.groupdict())
            return results.groupdict()

    if link.startswith("mailto:"):
        bits = link.split(":",maxsplit=1)
        if len(bits) > 1:
            email = bits[1]
            return { 'email' : email }
    return { 'link' : link }

def handle_signature_file(filename:str):
    """ handles a file """
    logger.debug(filename)

    toenail_data = {}
    with open(filename, 'r') as file_handle:
        contents = [ line.strip() for line in file_handle.readlines() if line.strip() != "" ]
        if len(contents) != 2:
            logger.error("Contents length != 2: {}", contents)
            return False
        logger.debug(contents)
        for line in contents:
            elements = [ el.strip() for el in line.split(":", maxsplit=1)]
            logger.debug(elements)
            if len(elements) != 2:
                logger.error("Wrong length for elements: {}", elements)
                return False
            key, value = elements
            if key in toenail_data:
                logger.error("Duplicate key found: {} in data: {}", key, contents)
                return False
            if key == 'link':
                linkdata = handle_link(value)
                if linkdata:
                    toenail_data.update(linkdata)
            else:
                toenail_data[key] = value
    logger.debug(toenail_data)
    return toenail_data



@click.command()
@click.option('--debug','-d', is_flag=True, default=True)
@click.option('--update','-u', is_flag=True, default=False)
def cli(debug:bool, update:bool):
    """ do the needful """
    setup_logging(debug, logger)

    if not os.path.exists(SOURCEREPO):
        os.mkdir(SOURCEREPO)

    repo = Repo(SOURCEREPO)

    #repo = 'rms-support-letter/rms-support-letter.github.io'

    # print(dir(repo))

    if update:
        for remote in repo.remotes:
            #if remote.name == 'origin':
            #print(dir(remote))
            #print(remote.name)
            if remote.name == 'origin':
                logger.info("Pulling origin")
                logger.debug(remote.pull())
                logger.info("Done.")

    if not os.path.exists(SIGNATURE_DIR):
        logger.error("Can't find signatures dir: {}", SIGNATURE_DIR)
        sys.exit(1)


    seen_keys = []
    hangnail_data = []
    for filename in os.listdir(SIGNATURE_DIR):
        full_filename = os.path.join(SIGNATURE_DIR,filename)
        signature = handle_signature_file(full_filename)
        logger.debug(signature)
        for key in signature:
            if key not in seen_keys:
                seen_keys.append(key)
        hangnail_data.append(signature)

    runtime = str(round(time.time(),0))
    runfile = f'results/{runtime}.json'
    logger.info("Keys seen: {}", seen_keys)

    writefile = True
    if os.path.exists('hangnail_data.json'):
        oldfile = open('hangnail_data.json', 'r').read()
        if json.dumps(hangnail_data) == oldfile:
            logger.warning("No change to data, no file to be written.")
            writefile = False
    if writefile:
        logger.info("Writing file...")
        with open(runfile, 'w') as file_handle:
            json.dump(obj=hangnail_data,
                      fp=file_handle,
                      )
        if os.path.exists('hangnail_data.json'):
            os.unlink('hangnail_data.json')
        os.symlink(runfile,'hangnail_data.json')

if __name__ == '__main__':
    cli()
