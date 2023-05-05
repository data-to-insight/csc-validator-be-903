import pandas as pd

from validator903.types import IntegrityCheckDefinition


def validate(dfs):
    if "Header" not in dfs or "Reviews" not in dfs:
        return {}
    else:
        header = dfs["Header"]
        file = dfs["Reviews"]

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
        return {"Reviews": epserrorlocations.unique().tolist()}


def test_validate():
    erro_defn, error_func = validate_INT17()

    fake_dfs = {"Header": fake_INT_header, "Reviews": fake_INT_file}
    result = error_func(fake_dfs)
    assert result == {"Reviews": [2]}
