from validator903.types import IntegrityCheckDefinition


import pandas as pd
from lac_validator.rule_engine import rule_definition


def validate(dfs):
    if "PrevPerm" not in dfs:
        return {}
    else:
        file = dfs["PrevPerm"]

        file["index_file"] = file.index

        file["CHILD_COUNT"] = file.groupby("CHILD")["CHILD"].transform("count")

        mask = file["CHILD_COUNT"] > 1
        eps_error_locations = file.loc[mask, "index_file"]
        return {"PrevPerm": eps_error_locations.unique().tolist()}


def test_validate():
    erro_defn, error_func = validate_INT35()

    fake_dfs = {"PrevPerm": fake_INT_header}
    result = validate(fake_dfs)
    assert result == {"PrevPerm": [0, 1, 2, 3, 4, 5, 6, 7]}
