#!/usr/bin/env python3

import os
from setuptools import setup

SETUP_VERSION = os.getenv("SETUP_VERSION", "development")

setup(
    name="terrform_state_processor",
    version=SETUP_VERSION,
    description="Generates text data from the terraform state.",
    author="Derek Vance",
    author_email="dacrepair@gmail.com",
    url="https://github.com/DACRepair/terraform_state_processor",

    install_requires=['click', 'jinja2'],

    packages=['terraform_state_processor',
              'terraform_state_processor.template',
              'terraform_state_processor.terraform',
              'terraform_state_processor.terraform.resource_types'],
    package_data={"terraform_state_processor.template": ["default/*.j2"]},

    entry_points={'console_scripts': [
        'tfstate_processor = terraform_state_processor.cli_app:cli_app'
    ]}
)
