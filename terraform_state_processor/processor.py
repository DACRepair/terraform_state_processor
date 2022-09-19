import os
import click

from terraform_state_processor.terraform.tfstate import TerraformState
from terraform_state_processor.template.environment import TemplateEnv


class StateProcessor:
    tfstate = None
    template = None

    def __init__(self, tfstate: str = None, template_path: str = None, processor_path: str = None):
        # State
        with open(tfstate, "r") as fp:
            self.tfstate = TerraformState(fp.read(), custom_base=processor_path)

        # Templates
        cwd_templates = os.path.abspath(os.path.join(os.path.abspath(os.getcwd()), 'templates'))
        home_path = os.path.join(os.path.join(os.path.abspath('~'), '.tfstate_processor'), 'templates')

        template_paths = []
        if template_path is not None:
            if os.path.isdir(template_path) or os.path.isfile(template_path):
                template_paths.append(template_path)
        if os.path.isdir(cwd_templates):
            template_paths.append(cwd_templates)
        if os.path.isdir(home_path):
            template_paths.append(home_path)

        self.template = TemplateEnv(template_paths)

    def render_template(self, template: str = 'debug'):
        abspath = False
        if os.path.isfile(os.path.abspath(template)):
            abspath = True
        return self.template.render_template(template, abs_path=abspath,
                                             format_version=self.tfstate.format_version,
                                             terraform_version=self.tfstate.terraform_version,
                                             resources=self.tfstate.resources,
                                             raw_entries=self.tfstate.entries)


@click.command()
@click.option("--tfstate", default="./tfstate.json",
              help="The terraform state json file path (default: ./tfstate.json).")
@click.option("--processors", default="./resource_types", help="Add custom processors")
@click.option("--template", default="debug", help="The template you would like to generate.")
@click.option("--outfile", default=None, help="The file to write the output to (default is to stdout).")
def tfstate_processor(tfstate, processors, template, outfile):
    """Generates text data from the terraform state."""
    tfstate = os.path.normpath(os.path.abspath(tfstate))
    if not os.path.isfile(tfstate):
        click.echo(f"File '{tfstate}' missing.")
        exit(1)
    processor = StateProcessor(tfstate=tfstate, processor_path=processors)
    template_data = processor.render_template(template)
    if outfile:
        outfile = os.path.normpath(os.path.abspath(outfile))
        with open(outfile, "w") as fp:
            fp.write(template_data)
            fp.close()
        click.echo(f"Wrote data to {outfile}.")
    else:
        click.echo(template_data)
