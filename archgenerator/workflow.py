from pathlib import Path

UPDATE_WORKFLOW = """\
name: Update

on:
  schedule:
    - cron:  '0 1 * * *'
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 3

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python 3.11
        uses: actions/setup-python@v2
        with:
          python-version: 3.11

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          python -m pip install git+https://github.com/uriyyo/archgenerator.git

      - name: Update solutions
        env:
          CODEWARS_EMAIL: ${{ secrets.CODEWARS_EMAIL }}
          CODEWARS_PASSWORD: ${{ secrets.CODEWARS_PASSWORD }}
          LEETCODE_EMAIL: ${{ secrets.LEETCODE_EMAIL }}
          LEETCODE_PASSWORD: ${{ secrets.LEETCODE_PASSWORD }}
        run: |
          archgenerator codewars
          archgenerator leetcode

      - name: Generate docs
        run: |
          archgenerator docs

      - name: Commit and push changes
        env:
          USER_NAME: ${{ secrets.USER_NAME }}
          USER_EMAIL: ${{ secrets.USER_EMAIL }}
        run: |
          git config core.autocrlf input
          git config core.whitespace cr-at-eol
          git config user.name ${USER_NAME}
          git config user.email ${USER_EMAIL}
          archgenerator commit --push
"""


def init_workflow(root: Path | None = None) -> None:
    workflow_file: Path = (root or Path.cwd()) / ".github" / "workflows" / "update.yml"
    workflow_file.parent.mkdir(parents=True, exist_ok=True)

    workflow_file.write_text(UPDATE_WORKFLOW, encoding="utf-8")


__all__ = [
    "init_workflow",
]
