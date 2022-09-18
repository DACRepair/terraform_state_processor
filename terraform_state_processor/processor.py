import os

from terraform_state_processor.terraform.tfstate import TerraformState
from terraform_state_processor.template.environment import TemplateEnv


class StateProcessor:
    tfstate = None
    template = None

    def __init__(self, tfstate: str = None, template_path: str = None, processor_path: str = None):
        with open(tfstate, "r") as fp:
            self.tfstate = TerraformState(fp.read(), custom_base=processor_path)

        local_templates = os.path.abspath(os.path.join(os.getcwd(), 'templates'))
        if template_path is None and os.path.isdir(local_templates):
            template_path = local_templates
        self.template = TemplateEnv(template_path)

    def render_template(self, template: str = 'debug'):
        template = self.template.find_template(template)
        if template:
            return self.template.render_template(*template,
                                                 format_version=self.tfstate.format_version,
                                                 terraform_version=self.tfstate.terraform_version,
                                                 resources=self.tfstate.resources,
                                                 raw_entries=self.tfstate.entries)
        else:
            return "No Template Found."
