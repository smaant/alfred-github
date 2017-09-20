__author__ = 'smaant'

from github import GitHub
import json
from datetime import datetime
import xml.etree.ElementTree as ET
import sys, os

CACHE = "cache.txt"


class Cache:
    def __init__(self, fname):
        self.cache_name = fname
        self.cache = None
        self.is_changed = False

    def _load_cache(self):
        try:
            return json.load(open(self.cache_name, "rt"))
        except IOError:
            return {}

    def _get_cache(self):
        self.cache = self.cache or self._load_cache()
        return self.cache

    def get(self, key):
        return self._get_cache().get(key, {}).get('value', [])

    def put(self, key, value):
        data = {'value': value, 'added': datetime.now().strftime("%c")}
        self._get_cache()[key] = data
        self.is_changed = True

    def keys(self):
        return self._get_cache().keys()

    def save(self):
        if self.is_changed:
            json.dump(self._get_cache(), open(self.cache_name, "wt"))
            self.is_changed = False

    def has_key(self, key):
        return key in self._get_cache()


def generate_xml(items):
    root = ET.Element('items')
    owners = items.keys()
    owners.sort()
    for owner in owners:
        sub = ET.SubElement(root, 'item', {'uid': owner, 'autocomplete': items[owner][0], 'arg': items[owner][1]})
        title = ET.SubElement(sub, 'title')
        title.text = owner

    return ET.tostring(root, 'utf-8')


def generate_placeholder_xml(text):
    root = ET.Element('items')
    sub = ET.SubElement(root, 'item', {'valid': 'no'})
    title = ET.SubElement(sub, 'title')
    title.text = text
    return ET.tostring(root, 'utf8')


def get_user_url(owner):
    return 'https://github.com/' + owner + '/'


def get_repo_url(owner, repo):
    return get_user_url(owner) + repo


def suggest_owner(cache, owner):
    return {name: (name, get_user_url(name)) for name in cache.keys() if owner in name}

if __name__ == '__main__':
    github_api_key = os.getenv('GITHUB_API_KEY', '')
    if github_api_key == '':
        print "ERROR: GitHub API key is not provided (GITHUB_API_KEY env var expected)"
        sys.exit(1)

    result = []
    if len(sys.argv) == 2:
        args = sys.argv[1].split()
        owner = args[0]
        complete_owner = ' ' in sys.argv[1]
        repo_name = args[1] if len(args) > 1 else ''

        cache = Cache(CACHE)
        if complete_owner:
            github = GitHub(github_api_key)
            repos = cache.get(owner) or github.get_repos(owner)
            result = {repo: (owner + ' ' + repo, get_repo_url(owner, repo)) for repo in repos if repo_name in repo}

            if repos and not cache.has_key(owner):
                cache.put(owner, repos)
                cache.save()
        else:
            result = suggest_owner(cache, owner)

    if result:
        print generate_xml(result)
    # else:
    #     print generate_placeholder_xml("keep typing user or organization name")
