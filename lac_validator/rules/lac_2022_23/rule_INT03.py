from validator903.types import IntegrityCheckDefinition


def validate(dfs):
    if "Header" not in dfs or "Episodes" not in dfs:
        return {}
    else:
        header = dfs["Header"]
        file = dfs["Episodes"]

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
        return {"Episodes": epserrorlocations.unique().tolist()}


def test_validate():
    erro_defn, error_func = validate_INT03()

    fake_dfs = {"Header": fake_INT_header, "Episodes": fake_INT_file}
    result = error_func(fake_dfs)
    assert result == {"Episodes": [3]}
