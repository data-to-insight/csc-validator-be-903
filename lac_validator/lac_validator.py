import logging
from typing import Any, Optional

import pandas as pd
from pandas import DataFrame

from lac_validator.datastore import copy_datastore, create_datastore
from lac_validator.ingress import read_from_text
from lac_validator.rule_engine import RuleDefinition
from lac_validator.types import UploadedFile

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class LacValidator:
    """
    Central location for running rules on files.
    """

    def __init__(
        self,
        metadata: dict[str, str],
        files: list[UploadedFile],
        registry: dict[str, RuleDefinition],
        selected_rules: Optional[list[str]] = None,
    ):
        self.dfs: dict[str, DataFrame] = {}
        self.dones: list[str] = []
        self.skips: list[str] = []
        self.fails: list[str] = []

        logger.info("Reading uploaded files...")
        dfs, metadata_extras = read_from_text(raw_files=files)
        self.dfs = dfs

        metadata.update(metadata_extras)
        logger.info(f'Metadata receieved: {",".join(metadata.keys())}')

        self.registry = registry
        self.metadata = metadata

        # validate
        self.validate(selected_rules)

    def get_rules_to_run(
        self,
        registry: dict[str, RuleDefinition],
        selected_rules: Optional[list[str]] = None,
    ):
        """
        Filters rules to be run based on user's selection in the frontend.
        :param dict registry: record of all existing rules in rule pack
        :param list selected_rules: array of rule codes as strings
        """
        if selected_rules:
            rules_to_run = {
                rule_code: rule
                for rule_code, rule in registry.items()
                if str(rule_code) in selected_rules
            }
            return rules_to_run
        else:
            return registry

    def validate(self, selected_rules: Optional[list[str]] = None):
        logger.info("Creating Data store...")
        data_store = create_datastore(self.dfs, self.metadata)

        rules_to_run = self.get_rules_to_run(self.registry, selected_rules)

        # this corresponds to raw_data in CINvalidationSession
        self.ds_results = copy_datastore(data_store)

        for rule_code, rule in rules_to_run.items():
            logger.info(f"Validating rule {rule_code}...")

            # get a clean copy of the files to be validated
            ds_copy = copy_datastore(data_store)

            try:
                # get the result from when the rule is run on the data.
                result: dict[str, list[Any]] = rule.func(ds_copy)
            except Exception as e:
                # document instances where the rule cannot run on the data
                logger.exception(f"Rule code {rule_code} failed to run!")
                self.fails.append(rule_code)
                continue

            if result == {}:
                # TODO replace this with behaviour that models rules skipped because of lack of data.

                # validation rules return an empty dict if the required tables are not all available.
                logger.info(f"Error code {rule.code} skipped due to missing tables")
                self.skips.append(rule.code)
            else:
                self.dones.append(rule.code)

            # map failing locations back to data files.
            for table, values in result.items():
                if len(values) > 0:
                    logger.info(f"Error code {rule.code} found {len(values)} errors")
                    nof_errors = len(values)
                    # select out only the valid values, that is remove all nans.
                    values = [
                        i for i, not_nan in zip(values, pd.notna(values)) if not_nan
                    ]
                    nof_nans = nof_errors - len(values)
                    if nof_nans != 0:
                        logger.warning(
                            f"{rule.code} returned {nof_nans} NaNs! "
                            + f"Output: {str(values)}"
                        )
                    self.ds_results[table].loc[values, f"ERR_{rule.code}"] = True


def create_issue_df(report: DataFrame, error_report: DataFrame):
    """
    creates issue_df similar to that of the CIN backend output.
    Columns should be child_id, tables_affected, columns_affected, row_id, rule_code and rule_description.

    Uses output of 903validator.report because it is closer to desired structure.

    :param df report: childID, rule_code, tables_affected and row_id will be grabbed from here
    :param df error_report: rule_description and affected_fields, per rule_code, will be grabbed from here.
    :return df full_issue_df: data to drive frontend display of issue locations.
    """
    # get rule codes from column names
    col_error_names = [c for c in report.columns if c[:4] == "ERR_"]

    # loop through rule codes and fetch rule data from error_report each time.
    issue_dfs_per_rule = []
    for col_name in col_error_names:
        rule_code = col_name[4:]

        # child, table, row where rule fails.
        rule_table = report[report[col_name] == True][
            [
                "Table",
                "RowID",
                "CHILD",
            ]
            + [col_name]
        ]
        rule_table["Code"] = rule_code

        rule_desc = error_report[error_report["Code"] == rule_code]
        # assumption. error_description has one entry per rule.
        rule_issue_df = rule_table.merge(rule_desc, on="Code")

        rule_issue_df.rename(
            columns={
                "Table": "tables_affected",
                "RowID": "row_id",
                "Code": "rule_code",
                "Description": "rule_description",
                "Fields": "columns_affected",
                "CHILD": "child_id",
            },
            inplace=True,
        )
        # remove ERR_ columns
        rule_issue_df.drop(columns=[col_name], inplace=True)
        # explode column lists into one per row.
        rule_issue_df = rule_issue_df.explode(
            column=["columns_affected"], ignore_index=True
        )
        # reorder
        rule_issue_df = rule_issue_df[
            [
                "child_id",
                "tables_affected",
                "columns_affected",
                "row_id",
                "rule_code",
                "rule_description",
            ]
        ]

        issue_dfs_per_rule.append(rule_issue_df)

    full_issue_df = pd.concat(issue_dfs_per_rule)
    full_issue_df.reset_index(drop=True, inplace=True)
    return full_issue_df
