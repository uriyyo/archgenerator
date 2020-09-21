import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from git import Repo, Diff

from . import context
from .consts import LANG_TO_EMOJI


class ChangeType(str, Enum):
    UPDATE = "M"
    ADD = "A"
    DELETE = "D"

    @classmethod
    def _missing_(cls, _):
        return cls.ADD

    def __str__(self):
        return self.name.title()


TASK_NAME_REGEX = re.compile(r"(?:## \[)(.*?)(?:\])")
LANG_EMOJI_REGEX = re.compile(r"(?:#### )(.*)")


@dataclass
class UpdateInfo:
    file: Path
    change_type: ChangeType
    diff: Diff

    @property
    def commit_message(self) -> str:
        return f'{self.emojies} {self.change_type!s} docs for "{self.task_name}"'

    @property
    def task_name(self) -> str:
        def get_name(source: str) -> str:
            return (m := TASK_NAME_REGEX.search(source)) and m.group(1)

        return get_name(self.commit_diff) or get_name(self.file_content)

    @property
    def emojies(self) -> str:
        def get_emojies(source: str) -> str:
            return "".join(
                LANG_TO_EMOJI[lang.lower()]
                for *_, lang in map(str.split, LANG_EMOJI_REGEX.findall(source))
                if lang.lower() in LANG_TO_EMOJI
            )

        return get_emojies(self.commit_diff) or get_emojies(self.file_content)

    @property
    def file_content(self):
        return self.file.read_text("utf-8")

    @property
    def commit_diff(self) -> str:
        return self.diff.diff.decode("utf-8")


def configure_repo(repo: Repo):
    for option, value in (
        ("name", context.GIT_USERNAME.get()),
        ("email", context.GIT_EMAIL.get()),
    ):
        if value:
            repo.config_writer().set_value("user", option, value).release()


def get_dirty_task_docs(repo: Repo):
    for diff in repo.head.commit.diff(create_patch=True):
        file: Path = Path(repo.working_dir) / (diff.b_path or diff.a_path)

        if file.suffix == ".md" and file.stem != "SUMMARY":
            yield UpdateInfo(file, ChangeType(diff.change_type), diff)


def commit_docs(repo_path: Path, push_commit: bool = False):
    repo = Repo(repo_path)
    repo.git.add(repo_path)
    configure_repo(repo)

    commit_message = "\n".join(
        info.commit_message for info in get_dirty_task_docs(repo)
    )

    if commit_message:
        repo.index.commit(commit_message)

        if push_commit:
            repo.remote().push()


__all__ = ["commit_docs"]
