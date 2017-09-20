# coding: utf-8
import json
import logging
import platform
from datetime import datetime

import requests

#import cmdpr


GITHUB_API_HOST = 'https://api.github.com'
USER_AGENT = 'alfred github plugin'

ORGANIZATIONS = "/orgs/"
USERS = "/users/"
REPOS = "/repos"

logger = logging.getLogger(__name__)


class GitHub:

    def __init__(self, token=None):
        self.session = requests.Session()
        self.session.headers = {'User-Agent': USER_AGENT}

        if token is not None:
            self.session.auth = (token, '')

    def _do_get(self, url):
        """
        :rtype: requests.Response
        """
        return self.session.get(GITHUB_API_HOST + url)

    def get_repos(self, name):
        base_url = ORGANIZATIONS if self.is_organization(name) else USERS
        repo_names = []

        page = 1
        response = self._do_get(base_url + name + REPOS + '?per_page=100&page={}'.format(page))
        while response.status_code == 200:
            repos = response.json()
            for repo in repos:
                repo_names += [repo['name']]

            if self._has_next(response):
                page += 1
                response = self._do_get(base_url + name + REPOS + '?per_page=100&page={}'.format(page))
            else:
                break

        return repo_names

    def _has_next(self, response):
        return 'link' in response.headers and 'rel="next"' in response.headers['link']

    def is_organization(self, name):
        response = self._do_get(ORGANIZATIONS + name)
        return response.status_code == 200


class GitHubException(Exception):
    def __init__(self, message):
        super(GitHubException, self).__init__(message)
