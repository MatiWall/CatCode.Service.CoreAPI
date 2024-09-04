from pydantic import BaseModel


class CatCodeRepoEntry(BaseModel):
    repo: str
    repo_path: str
    user: str
    url: str
    sha: str

    @property
    def name(self):
        return f'{self.repo}/{self.repo_path}'

class Repository(BaseModel):
    repo_url: str
    html_url: str
    branch: str
    name: str
    sha: str
