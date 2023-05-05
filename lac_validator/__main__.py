import click

from lac_validator.ruleset import create_registry

@click.group()
def cli():
    pass

@cli.command(name="list")
@click.option(
    "--ruleset", 
    "-r",
    default="lac2022_23",
    help="validation year, e.g lac2022_23",
)
def list_cmd(ruleset):
    """
    :param str ruleset: validation year whose version of rules should be run.

    :return cli output: list of rules in validation year. 
    """
    registry = create_registry(ruleset=ruleset)
    for rule in registry:
        click.echo(f"{rule.code}\t{rule.message}")

if __name__ == "__main__":
    cli()