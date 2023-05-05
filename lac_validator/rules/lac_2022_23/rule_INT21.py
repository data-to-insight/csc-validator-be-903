from validator903.types import IntegrityCheckDefinition


import pandas as pd
from lac_validator.rule_engine import rule_definition


def validate(dfs):
    if "Header" not in dfs or "UASC" not in dfs:
        return {}
    else:
        header = dfs["Header"]
        file = dfs["UASC"]

        file["index_file"] = file.index

        merged = header.merge(
            file[["CHILD", "SEX", "index_file"]],
            on="CHILD",
            indicator=True,
            how="right",
            suffixes=["_header", "_file"],
        )

        mask = (
            (merged["SEX_header"] != merged["SEX_file"])
            & (merged["SEX_header"].notna() & merged["SEX_file"].notna())
            & (merged["_merge"] != "right_only")
        )
        eps_error_locations = merged.loc[mask, "index_file"]
        return {"UASC": eps_error_locations.unique().tolist()}


def test_validate():
    erro_defn, error_func = validate_INT21()

    fake_dfs = {"Header": fake_INT_header, "UASC": fake_INT_file}
    result = error_func(fake_dfs)
    assert result == {"UASC": [2]}
