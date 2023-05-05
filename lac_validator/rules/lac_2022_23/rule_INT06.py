from validator903.types import IntegrityCheckDefinition


import pandas as pd
from lac_validator.rule_engine import rule_definition


def validate(dfs):
    if "Header" not in dfs or "OC3" not in dfs:
        return {}
    else:
        header = dfs["Header"]
        file = dfs["OC3"]

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
        return {"OC3": eps_error_locations.unique().tolist()}


def test_validate():
    erro_defn, error_func = validate_INT06()

    fake_dfs = {"Header": fake_INT_header, "OC3": fake_INT_file}
    result = error_func(fake_dfs)
    assert result == {"OC3": [3]}
