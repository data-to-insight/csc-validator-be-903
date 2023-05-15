import click
import importlib
import pytest

from pathlib import Path

import lac_validator.lac_validator_class as lac_class
from lac_validator.ruleset import create_registry

from validator903.validator import Validator
from validator903.report import Report

@click.group()
def cli():
    pass

# LIST
@cli.command(name="list")
@click.option(
    "--ruleset", 
    "-r",
    default="lac2022_23",
    help="validation year, e.g lac_2022_23",
)
def list_cmd(ruleset):
    """
    :param str ruleset: validation year whose version of rules should be run.

    :return cli output: list of rules in validation year. 
    """
    registry = create_registry(ruleset=ruleset)
    for rule in registry:
        click.echo(f"{rule.code}\t{rule.message}")

# TEST
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

# RUN
@cli.command(name="run")
@click.argument("p4a_path", type=click.File("rt"), required=True)
@click.argument("ad1_path", type=click.File("rt"), required=True)
@click.option("--ruleset", "-r", default="lac_2022_23", help="validation year e.g lac_2022_23",)
@click.option("--select", "-s", default=None)
def run_all(p4a_path, ad1_path, ruleset, select):
    """
    created with code from offlinedebug.py

    :param str ruleset: validation year.
    :param str select: code of specific rule that should be run.
    """
    # p4a_path = "tests\\fake_data\placed_for_adoption_errors.csv"
    # ad1_path = "tests\\fake_data\\ad1.csv"

    # construct 'files' list of dicts (nb filetexts are bytes not str)
    with open(p4a_path.name, 'rb') as f:
        p4a_filetext = f.read()

    with open(ad1_path.name, 'rb') as f:
        ad1_filetext = f.read()

    files_list = [
        dict(name=p4a_path.name, description='This year', fileText=p4a_filetext),
        dict(name=ad1_path.name, description='This year', fileText=ad1_filetext),
    ]

    # the rest of the metadata is added in read_from_text() when instantiating Validator
    metadata = {'collectionYear': '2022',
                'localAuthority': 'E09000027'}

    v = lac_class.LacValidationSession(metadata=metadata, files=files_list, ruleset=ruleset, selected_rules=None)
    results = v.ds_results
    # print(results)

    # print()
    # print('-- AD1 Columns --')
    # print(results['AD1'].columns)
    # print()
    # print(f"*****************AD1 with selected cols******************")
    # print(results['AD1'][['DATE_MATCH', 'ERR_523']])
    # print('-- PlacedAdoption Columns --')
    # print(results['PlacedAdoption'].columns)
    # print()
    # print(f"*****************AD1 full in ds_results******************")
    # print(results['PlacedAdoption'], ['DATE_PLACED', 'ERR_523'])    

    r = Report(results)
    print(f"*****************Report******************")
    print(r.report)
    print(f"*****************Error report******************")
    print(r.error_report)
    # print(f"****************Error summary******************")
    # print(r.error_summary)

    full_issue_df = lac_class.create_issue_df(r.report, r.error_report)
    print(full_issue_df)


if __name__ == "__main__":
    cli()