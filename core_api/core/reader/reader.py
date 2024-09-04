from core_api.core.reader.readers.github import GithubReader
from settings import config


class RepositoryReader:
    def __init__(
            self,
            reader_implementation: GithubReader
    ):
        self.reader = reader_implementation

    def files(self):
        return self.reader.files()

    def get_file_content(self, repo):
        return self.reader.get_file_content(repo)


repo_reader = RepositoryReader(reader_implementation=GithubReader(username=config.username, token=config.github_token))