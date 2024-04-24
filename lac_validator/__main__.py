import importlib
import os
from pathlib import Path

import click
import pytest

from lac_validator import lac_validator
from lac_validator.ingress import read_from_text
from lac_validator.report import Report
from lac_validator.utils import process_uploaded_files


@click.group()
def cli():
    pass


# LIST
@cli.command(name="list")
@click.option(
    "--ruleset",
    "-r",
    default="lac2023_24",
    help="validation year, e.g lac2023_24",
)
def list_cmd(ruleset):
    """
    :param str ruleset: validation year whose version of rules should be run.

    :return cli output: list of rules in validation year.
    """
    module = importlib.import_module(f"lac_validator.rules.{ruleset}")
    ruleset_registry = getattr(module, "registry")
    for _, rule in ruleset_registry.items():
        click.echo(f"{rule.code}\t{rule.message}")


# TEST
@cli.command(name="test")
@click.option(
    "--ruleset",
    "-r",
    default="lac2023_24",
    help="validation year, e.g lac2023_24",
)
def test_cmd(ruleset):
    """
    Runs pytest of rules specified
    :param str ruleset: validation year whose rules should be run
    :return: classic pytest output
    """
    module = importlib.import_module(f"lac_validator.rules.{ruleset}")
    module_folder = Path(module.__file__).parent
    # May 2023. There are 288 rule files.
    test_files = [
        str(p.absolute()) for p in module_folder.glob("*.py") if p.stem != "__init__"
    ]
    pytest.main(test_files)


# TEST one rule
@cli.command(name="test_one_rule")
@click.argument("code", type=str, required=True)
@click.option(
    "--ruleset",
    "-r",
    default="lac2023_24",
    help="validation year, e.g lac2023_24",
)
def test_one_rule(code, ruleset):
    """
    Runs pytest of rules specified
    :param str ruleset: validation year whose rules should be run
    :return: classic pytest output
    """
    module = importlib.import_module(f"lac_validator.rules.{ruleset}")
    module_folder = Path(module.__file__).parent

    file_path = os.path.join(module_folder, f"rule_{code}.py")

    pytest.main([file_path])


# RUN
@cli.command(name="run")
@click.argument("p4a_path", type=click.File("rt"), required=True)
@click.argument("ad1_path", type=click.File("rt"), required=True)
@click.option(
    "--ruleset",
    "-r",
    default="lac2023_24",
    help="validation year e.g lac2022_23",
)
@click.option("--select", "-s", default=None)
def run_all(p4a_path, ad1_path, ruleset, select):
    """
    created with code from offlinedebug.py

    CLI command:
    python -m lac_validator run <filepath_>

    :param str ruleset: validation year.
    :param str select: code of specific rule that should be run.
    """
    # p4a_path = "tests\\fake_data\placed_for_adoption_errors.csv"
    # ad1_path = "tests\\fake_data\\ad1.csv"
    # frontend_files_dict = {"This year":[p4a_path, ad1_path], "Prev year": [p4a_path]}

    frontend_files_dict = {"This year": [p4a_path, ad1_path]}
    files_list = process_uploaded_files(frontend_files_dict)

    # the rest of the metadata is added in read_from_text() when instantiating Validator
    metadata = {"collectionYear": "2022", "localAuthority": "E09000027"}
    module = importlib.import_module(f"lac_validator.rules.{ruleset}")
    ruleset_registry = getattr(module, "registry")

    v = lac_validator.LacValidator(
        metadata=metadata,
        files=files_list,
        registry=ruleset_registry,
        selected_rules=None,
    )
    results = v.ds_results

    click.echo(v.ds_results)
    click.echo(f"skipped {v.skips}")
    click.echo(f"done: {v.dones}")

    r = Report(results, ruleset_registry)
    # click.echo(f"*****************Error report******************")
    # click.echo(r.error_report)
    # click.echo(f"****************Error summary******************")
    # click.echo(r.error_summary)
    # full_issue_df = lac_validator.create_issue_df(r.report, r.error_report)
    # click.echo(f"*****************full issue df******************")
    # click.echo(full_issue_df)


# RUN
@cli.command(name="run-offline")
@click.argument("filename", required=True)
@click.option(
    "--ruleset",
    "-r",
    default="lac2023_24",
    help="validation year e.g lac2023_24",
)
@click.option("--select", "-s", default=None)
def run_all(filename: str, ruleset, select):
    """
    CLI command to run the validator offline, primarily to test ingress

    CLI command:
    python -m lac_validator run-offline <filepath_>

    :param str ruleset: validation year.
    :param str select: code of specific rule that should be run.
    """
    ad1 = f"{filename}/ad1.csv"
    episodes = f"{filename}/episodes.csv"
    header = f"{filename}/header.csv"
    missing = f"{filename}/missing.csv"
    oc2 = f"{filename}/oc2.csv"
    oc3 = f"{filename}/oc3.csv"
    p4a = f"{filename}/placed_for_adoption_errors.csv"
    previous_permanence = f"{filename}/previous_permanence.csv"
    reviews = f"{filename}/reviews.csv"
    uasc = f"{filename}/uasc.csv"
    sw_episodes = f"{filename}/sw_episodes.csv"

    frontend_files_dict = {
        "This year": [
            ad1,
            episodes,
            header,
            missing,
            oc2,
            oc3,
            p4a,
            previous_permanence,
            reviews,
            uasc,
            sw_episodes,
        ]
    }
    files_list = process_uploaded_files(frontend_files_dict)

    # the rest of the metadata is added in read_from_text() when instantiating Validator
    metadata = {"collectionYear": "2023", "localAuthority": "E09000027"}
    module = importlib.import_module(f"lac_validator.rules.{ruleset}")
    ruleset_registry = getattr(module, "registry")

    v = lac_validator.LacValidator(
        metadata=metadata,
        files=files_list,
        registry=ruleset_registry,
        selected_rules=None,
    )

    click.echo(v.dfs)

    results = v.ds_results

    r = Report(results, ruleset_registry)
    full_issue_df = lac_validator.create_issue_df(r.report, r.error_report)
    click.echo(full_issue_df)


# XML to tables
@cli.command(name="xmltocsv")
@click.argument("p4a_path", type=click.File("rt"), required=True)
def xmltocsv(p4a_path):
    with open(p4a_path.name, "rb") as f:
        p4a_filetext = f.read()
    files_list = [
        dict(name=p4a_path.name, description="This year", file_content=p4a_filetext),
    ]

    data_files, _ = read_from_text(files_list)
    click.echo(data_files)


if __name__ == "__main__":
    cli()
