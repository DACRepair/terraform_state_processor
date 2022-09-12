import os
import click
from terraform_state_processor.processor import StateProcessor


@click.command()
@click.option("--tfstate", default="./tfstate.json", help="The terraform state file (json formatted).")
@click.option("--tfstate-package-base", default=None, help="Package containing the resource processors.")
@click.option("--template", default="debug", help="The template you would like to generate.")
@click.option("--outfile", default=None, help="The file to write the output to (default is to stdout).")
def cli_app(tfstate, tfstate_package_base, template, outfile):
    """Generates text data from the terraform state."""
    tfstate = os.path.normpath(os.path.abspath(tfstate))
    if not os.path.isfile(tfstate):
        click.echo(f"File '{tfstate}' missing.")
        exit(1)
    processor = StateProcessor(tfstate=tfstate, tfstate_package_base=tfstate_package_base)
    template_data = processor.render_template(template)
    if outfile:
        outfile = os.path.normpath(os.path.abspath(outfile))
        with open(outfile, "w") as fp:
            fp.write(template_data)
            fp.close()
        click.echo(f"Wrote data to {outfile}.")
    else:
        click.echo(template_data)
