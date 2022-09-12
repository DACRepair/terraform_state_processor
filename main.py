from pprint import pprint

from terraform_state_processor.terraform.tfstate import TerraformState
from terraform_state_processor.template.environment import TemplateEnv


class CurrentState:
    tfstate = None
    template = None

    def __init__(self, path: str = None, tfstate_package_base: str = None, template_path: str = None):
        with open(path, "r") as fp:
            self.tfstate = TerraformState(fp.read(), tfstate_package_base)

        self.template = TemplateEnv(template_path)

    def render_template(self, template: str = 'debug'):
        template = self.template.find_template(template)
        return self.template.render_template(*template,
                                             format_version=self.tfstate.format_version,
                                             terraform_version=self.tfstate.terraform_version,
                                             data=self.tfstate.data, resources=self.tfstate.resources,
                                             raw_entries=self.tfstate.entries)


path = "./tfstate.json"
test = CurrentState(path)

print(test.tfstate)
print(test.render_template())
# print(test.tfstate.entries)
# print(test.tfstate.data)
# print(test.tfstate.resources)
