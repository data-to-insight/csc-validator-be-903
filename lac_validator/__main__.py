import click
import importlib
import pytest

from pathlib import Path

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

@cli.command(name="test")
@click.option(
    "--ruleset", 
    "-r",
    default="lac_2022_23",
    help="validation year, e.g lac_2022_23",
)
def test_cmd(ruleset):
    """
    Runs pytest of rules specified
    :param str ruleset: validation year whose rules should be run
    :return: classic pytest output
    """
    module = importlib.import_module(f"lac_validator.rules.{ruleset}")
    module_folder = Path(module.__file__).parent

    test_files = [str(p.absolute()) for p in module_folder.glob("*.py") if p.stem != "__init__"]
    pytest.main(test_files)


if __name__ == "__main__":
    cli()