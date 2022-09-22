import json
from terraform_state_processor.terraform.resource_types import BaseResource, StateField


class VirtualMachineResource(BaseResource):
    __datatype__ = 'vsphere_virtual_machine'

    name = StateField("values.name")
    uuid = StateField("values.uuid")
    ip_address = StateField("values.default_ip_address")
    config_servergroups = StateField("values.extra_config.guestinfo..config_servergroups", json.loads)
    config_serverroles = StateField("values.extra_config.guestinfo..config_serverroles", json.loads)
