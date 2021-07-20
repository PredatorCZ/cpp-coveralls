#!/usr/bin/env python3

import os
import subprocess
import re


def gitrepo(cwd):
    """Return hash of Git data that can be used to display more information to
    users.

    Example:
        "git": {
            "head": {
                "id": "5e837ce92220be64821128a70f6093f836dd2c05",
                "author_name": "Wil Gieseler",
                "author_email": "wil@example.com",
                "committer_name": "Wil Gieseler",
                "committer_email": "wil@example.com",
                "message": "depend on simplecov >= 0.7"
            },
            "branch": "master",
            "remotes": [{
                "name": "origin",
                "url": "https://github.com/lemurheavy/coveralls-ruby.git"
            }]
        }

    From https://github.com/coagulant/coveralls-python (with MIT license).

    """
    repo = Repository(cwd)
    if not repo.valid():
        return {}

    origin_remote = re.search('(\w+)\s+(.*)\(fetch\)', repo.git('remote', '-v')[1])

    return {
        'head': {
            'id': repo.gitlog('%H'),
            'author_name': repo.gitlog('%aN'),
            'author_email': repo.gitlog('%ae'),
            'committer_name': repo.gitlog('%cN'),
            'committer_email': repo.gitlog('%ce'),
            'message': repo.gitlog('%s')
        },
        'branch': os.environ.get('TRAVIS_BRANCH',
                  os.environ.get('APPVEYOR_REPO_BRANCH',
                  os.environ.get('CI_BRANCH',
                                 repo.git('rev-parse', '--abbrev-ref', 'HEAD')[1].strip()))),
        'remotes': [{'name': origin_remote.group(1).strip(), 'url': origin_remote.group(2).strip()}]
    }


class Repository(object):

    def __init__(self, cwd):
        self.cwd = cwd

    def valid(self):
        """
        :return: true if it is a valid git repository.
        """
        return self.git("log", "-1")[0] == 0

    def gitlog(self, fmt):
        return self.git('--no-pager', 'log', '-1', '--pretty=format:%s' % fmt)[1]

    def git(self, *arguments):
        """
        Return (exit code, output) from git.
        """
        process = subprocess.Popen(['git'] + list(arguments),
                                   stdout=subprocess.PIPE,
                                   cwd=self.cwd)
        out = process.communicate()[0].decode('UTF-8')
        code = process.returncode
        return code, out
