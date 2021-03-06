from __future__ import annotations

from setuptools import setup

from python_typing_update.const import version_str


def load_requirements_file(filename: str) -> list[str]:
    with open(filename) as fp:
        return [
            line.strip().split(' ', 1)[0] for line in fp.read().splitlines()
            if line.strip() != '' and not line.startswith('#')
        ]


setup(
    version=version_str,
    install_requires=load_requirements_file('requirements.txt'),
    extras_require={
        'black': load_requirements_file('requirements_black.txt'),
    },
)
