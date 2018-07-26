import configparser
import json
import logging
import time

from github import Github


class GitHubBaseMonitor:
    def __init__(self, repository):
        self.repository_name = repository
        self.github = Github()

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)


class GithubReleaseMonitor(GitHubBaseMonitor):
    def __init__(self, repository, latest_release_id=None):
        super().__init__(repository)
        self.latest_release_id = latest_release_id

    def check(self):
        self.logger.info('Checking {} for new releases...'.format(self.repository_name))
        repository = self.github.get_repo(self.repository_name)
        latest_release = repository.get_latest_release()
        if self.latest_release_id != latest_release.id:
            self.logger.warning('NEW RELEASE {} {} {}'.format(
                self.repository_name, latest_release.tag_name, latest_release.url))
            self.latest_release_id = latest_release.id


class GithubCommitMonitor(GitHubBaseMonitor):
    def __init__(self, repository, branch_name='master', latest_commit_sha=None):
        super().__init__(repository)
        self.branch_name = branch_name
        self.latest_commit_sha = latest_commit_sha

    def check(self):
        self.logger.info('Checking {} for new commits...'.format(self.repository_name))
        repository = self.github.get_repo(self.repository_name)
        branch = repository.get_branch(self.branch_name)
        commit = branch.commit
        if self.latest_commit_sha != commit.sha:
            self.logger.warning('NEW COMMIT {}#{} {} {}'.format(
                self.repository_name, self.branch_name, commit.sha, commit.html_url))
            self.latest_commit_sha = commit.sha


class GithubActionMonitor:
    def __init__(self, config_filename='config.ini', latest_data_filename='data.json', delay_between_checks_in_s=60):
        self.delay_between_checks_in_s = delay_between_checks_in_s
        self.config = configparser.ConfigParser()
        self.config.read(config_filename)
        self.latest_data = json.load(open(latest_data_filename))
        self.monitors = []

        for section in self.config.sections():
            repository_name = section

            if self.config[section]['action'] == 'release':
                latest_release_id = self.latest_data[section]['release_id']
                github_release_monitor = GithubReleaseMonitor(repository_name, latest_release_id)
                self.monitors.append(github_release_monitor)

            elif self.config[section]['action'] == 'commit':
                latest_commit_sha = self.latest_data[section]['commit_sha']
                branch_name = self.config[section]['branch']
                github_commit_monitor = GithubCommitMonitor(repository_name, branch_name, latest_commit_sha)
                self.monitors.append(github_commit_monitor)

    def monitor_loop(self):
        while True:
            for monitor in self.monitors:
                monitor.check()
                time.sleep(self.delay_between_checks_in_s)


if __name__ == '__main__':
    gam = GithubActionMonitor()
    gam.monitor_loop()
