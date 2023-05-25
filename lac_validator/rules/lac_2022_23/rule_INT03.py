from validator903.types import IntegrityCheckDefinition


import pandas as pd
from lac_validator.rule_engine import rule_definition


def validate(dfs):
    if "Header" not in dfs or "Episodes" not in dfs:
        return {}
    else:
        header = dfs["Header"]
        file = dfs["Episodes"]

        file["index_file"] = file.index

        merged = header.merge(
            file[["CHILD", "index_file"]],
            on="CHILD",
            indicator=True,
            how="right",
            suffixes=["_header", "_file"],
        )

        mask = merged["_merge"] == "right_only"
        eps_error_locations = merged.loc[mask, "index_file"]
        return {"Episodes": eps_error_locations.unique().tolist()}


def test_validate():
    erro_defn, error_func = validate_INT03()

    fake_dfs = {"Header": fake_INT_header, "Episodes": fake_INT_file}
    result = validate(fake_dfs)
    assert result == {"Episodes": [3]}
