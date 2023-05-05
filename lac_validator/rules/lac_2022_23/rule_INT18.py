import pandas as pd

from validator903.types import IntegrityCheckDefinition


def validate(dfs):
    if "Header" not in dfs or "UASC" not in dfs:
        return {}
    else:
        header = dfs["Header"]
        file = dfs["UASC"]

        header["DOB"] = pd.todatetime(header["DOB"], format="%d/%m/%Y", errors="coerce")
        file["DOB"] = pd.todatetime(file["DOB"], format="%d/%m/%Y", errors="coerce")

        file["indexfile"] = file.index

        merged = header.merge(
            file[["CHILD", "DOB", "indexfile"]],
            on="CHILD",
            indicator=True,
            how="right",
            suffixes=["header", "file"],
        )

        mask = (
            (merged["DOBheader"] != merged["DOBfile"])
            & (merged["DOBheader"].notna() & merged["DOBfile"].notna())
            & (merged["merge"] != "rightonly")
        )
        epserrorlocations = merged.loc[mask, "indexfile"]
        return {"UASC": epserrorlocations.unique().tolist()}


def test_validate():
    erro_defn, error_func = validate_INT18()

    fake_dfs = {"Header": fake_INT_header, "UASC": fake_INT_file}
    result = error_func(fake_dfs)
    assert result == {"UASC": [2]}
