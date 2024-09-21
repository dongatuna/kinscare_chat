"""
Setup script for the backend service of Kinscare Chat.
Ensures Python 3.10 or newer is used and sets up the package.
"""

import sys
from setuptools import find_packages, setup

# Enforcing Python version requirement
assert sys.version_info[0] == 3 and sys.version_info[1] >= 10, \
    "Kinscare Chat requires Python 3.10 or newer"

# TODO: freeze packages

setup(
    name='kinscare_chat',
    version='1.1.0',
    description="Kinscare Chat Backend.",
    long_description=open('README.md', 'r', encoding='UTF-8').read(),
    packages=find_packages(exclude=['scripts']),
    install_requires=[
        'requests',
        'openai',
        'pandas',
        'fastapi',
        'uvicorn',
        'apscheduler',
        'fastapi[security]',
        'psycopg2-binary',
        'pydantic[email]',
        'sendgrid',
        'openpyxl',
        'pymongo'
    ],
    entry_points={
        'console_scripts': [
            'kinscare_chat = kinscare_chat.run_bot:run'
        ]
    }
)
