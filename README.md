# Terraform State Processor

## Overview

The Terraform State Processor is a tool used to extract and manipulate the Terraform state.
This is typically for use with automation, reporting, and data analysis tools.
Note: This tool is a one way tool designed to read the tf state only. It does not allow for direct modification of
the state.

The application is split into two areas: input and output

Input:
This is done through the use of abstraction classes using a JSON/XMLPath-like markup and is written in Python.

Output:
This is done through the use of the Jinja2 template engine.

## Quick Start

### Installation

The supported path for this application is using the provided Docker image

```
> docker pull ghcr.io/dacrepair/terraform_state_processor:latest
```

You can also install it directly to an existing Python 3.10 environment using

```
> pip install git+https://github.com/DACRepair/terraform_state_processor
```

Once this has been completed, usage is simple by executing a docker container via:

```
> docker run --rm -it -b ${PWD}:/data ghcr.io/dacrepair/terraform_state_processor:latest
```

### Configuration and usage

#### State File

The `terraform_state_processor` command by default looks for a `tfstate.json` file. On the docker image this would be
`/data/tfstate.json`. This can be easily generated by running something like `terraform show --json > tfstate.json`.
You can also specify an arbitrary state file with `--tfstate <state file path>`

#### Processing

This is done through a python class that extends the `BaseResource` class. The majority of the field handling is done
dynamically so extending should be extremely straightforward. Naming should follow this standard:

```tf
# resource_types/vsphere.py

# All classes should be title-case, and should only have alphanumeric characters 
# (-_ should be removed, numerics in their spelled format, 1 -> One)
# All classes should refrain from having the provider name (IE: vsphere_virtual_machine -> VirtualMachine)

Examples:
terraform {
  required_providers {
    vsphere = {} # vsphere.py
  }
}

data "vsphere_folder" "some_folder" {} # FolderData(BaseResource)

resource "vsphere_virtual_machine" "virtual_machine" {} # VirtualMachineResource(BaseResource)
```

Writing an extension is fairly straightforward as well:

```python
from terraform_state_processor.terraform.resource_types import BaseResource


class VirtualMachineResource(BaseResource):
    __datatype__ = 'vsphere_virtual_machine'

    name = "values.name"  # values are separated by '.'
    index = None
    uuid = "values.uuid"
    ip_address = "values.default_ip_address"
    config_servergroups = "values.extra_config.guestinfo..config_servergroups"  # '..' is used to escape a period
    config_serverroles = "values.extra_config.guestinfo..config_serverroles"
```

To get a better understanding, simply run the command without a template specified, and it will dump the json out to
console including the base processed data.

#### Templating

By default, the application only comes with a debugging template that shows the individual entries

You can specify a custom template by using the `--template` option

Using a default template:

```
> terraform_state_processor --template my_cool_template
```

Using an arbitrary template (must be an absolute path)

```
> terraform_state_processor --template /data/templates/my_custom_template.j2
```

The template file is simply a flat representation of the output, using jinja2 to replace the areas you would like
extracted from the state:

```
DEBUG DUMP
Terraform Format Version: {{ format_version }}
Terraform Application Version: {{ terraform_version }}

[Data Output: raw_entries]
{%- for entry in raw_entries %}
{{ entry }}
{%- endfor %}

[Processed Resources]
{%- for entry in data %}
{{ entry }}
{%- endfor %}
```

For more information on how jinja2 works, see
here: [Jinja Designer Documentation](https://jinja.palletsprojects.com/en/3.0.x/templates/)
