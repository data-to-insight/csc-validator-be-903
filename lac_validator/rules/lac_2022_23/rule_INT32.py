from validator903.types import IntegrityCheckDefinition


def validate(dfs):
    if "Header" not in dfs:
        return {}
    else:
        file = dfs["Header"]

        file["indexfile"] = file.index

        file["CHILDCOUNT"] = file.groupby("CHILD")["CHILD"].transform("count")

        mask = file["CHILDCOUNT"] > 1
        epserrorlocations = file.loc[mask, "indexfile"]
        return {"Header": epserrorlocations.unique().tolist()}


def test_validate():
    erro_defn, error_func = validate_INT32()

    fake_dfs = {"Header": fake_INT_header}
    result = error_func(fake_dfs)
    assert result == {"Header": [0, 1, 2, 3, 4, 5, 6, 7]}
