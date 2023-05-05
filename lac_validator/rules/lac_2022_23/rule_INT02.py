from validator903.types import IntegrityCheckDefinition


def validate(dfs):
    if "Header" not in dfs or "PlacedAdoption" not in dfs:
        return {}
    else:
        header = dfs["Header"]
        file = dfs["PlacedAdoption"]

        file["indexfile"] = file.index

        merged = header.merge(
            file[["CHILD", "indexfile"]],
            on="CHILD",
            indicator=True,
            how="right",
            suffixes=["header", "file"],
        )

        mask = merged["merge"] == "rightonly"
        epserrorlocations = merged.loc[mask, "indexfile"]
        return {"PlacedAdoption": epserrorlocations.unique().tolist()}


def test_validate():
    erro_defn, error_func = validate_INT02()

    fake_dfs = {"Header": fake_INT_header, "PlacedAdoption": fake_INT_file}
    result = error_func(fake_dfs)
    assert result == {"PlacedAdoption": [3]}
