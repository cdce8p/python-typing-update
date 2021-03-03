from setuptools import setup

from python_typing_update.const import version_str


with open('requirements.txt') as fp:
    requirements = [
        line.strip().split(' ', 1)[0] for line in fp.read().splitlines()
        if line.strip() != '' and not line.startswith('#')
    ]

setup(
    version=version_str,
    packages=['python_typing_update'],
    install_requires=requirements,
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'python-typing-update = python_typing_update.__main__:main',
        ],
    }
)
