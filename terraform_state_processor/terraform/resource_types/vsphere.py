from terraform_state_processor.terraform.resource_types import BaseResource


class VirtualMachineResource(BaseResource):
    __datatype__ = 'vsphere_virtual_machine'

    name = "values.name"
    index = None
    uuid = "values.uuid"
    ip_address = "values.default_ip_address"
    config_servergroups = "values.extra_config.guestinfo..config_servergroups"
    config_serverroles = "values.extra_config.guestinfo..config_serverroles"
