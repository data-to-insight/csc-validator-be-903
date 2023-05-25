from validator903.types import IntegrityCheckDefinition


import pandas as pd
from lac_validator.rule_engine import rule_definition


def validate(dfs):
    if "OC3" not in dfs:
        return {}
    else:
        file = dfs["OC3"]

        file["index_file"] = file.index

        file["CHILD_COUNT"] = file.groupby("CHILD")["CHILD"].transform("count")

        mask = file["CHILD_COUNT"] > 1
        eps_error_locations = file.loc[mask, "index_file"]
        return {"OC3": eps_error_locations.unique().tolist()}


def test_validate():
    erro_defn, error_func = validate_INT34()

    fake_dfs = {"OC3": fake_INT_header}
    result = validate(fake_dfs)
    assert result == {"OC3": [0, 1, 2, 3, 4, 5, 6, 7]}
