"""dragonfly-idaice commands which will be added to dragonfly command line interface."""
import click
from dragonfly.cli import main

from .translate import translate


# command group for all idaice extension commands.
@click.group(help='dragonfly idaice commands.')
@click.version_option()
def idaice():
    pass


idaice.add_command(translate)

# add ies sub-commands to honeybee CLI
main.add_command(idaice)
