import pandas as pd

from validator903.types import IntegrityCheckDefinition


import pandas as pd
from lac_validator.rule_engine import rule_definition


def validate(dfs):
    if "Header" not in dfs or "OC3" not in dfs:
        return {}
    else:
        header = dfs["Header"]
        file = dfs["OC3"]

        header["DOB"] = pd.to_datetime(
            header["DOB"], format="%d/%m/%Y", errors="coerce"
        )
        file["DOB"] = pd.to_datetime(file["DOB"], format="%d/%m/%Y", errors="coerce")

        file["index_file"] = file.index

        merged = header.merge(
            file[["CHILD", "DOB", "index_file"]],
            on="CHILD",
            indicator=True,
            how="right",
            suffixes=["_header", "_file"],
        )

        mask = (
            (merged["DOB_header"] != merged["DOB_file"])
            & (merged["DOB_header"].notna() & merged["DOB_file"].notna())
            & (merged["_merge"] != "right_only")
        )
        eps_error_locations = merged.loc[mask, "index_file"]
        return {"OC3": eps_error_locations.unique().tolist()}


def test_validate():
    erro_defn, error_func = validate_INT15()

    fake_dfs = {"Header": fake_INT_header, "OC3": fake_INT_file}
    result = validate(fake_dfs)
    assert result == {"OC3": [2]}
