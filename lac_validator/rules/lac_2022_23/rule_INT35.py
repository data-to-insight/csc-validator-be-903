from validator903.types import IntegrityCheckDefinition


def validate(dfs):
    if "PrevPerm" not in dfs:
        return {}
    else:
        file = dfs["PrevPerm"]

        file["indexfile"] = file.index

        file["CHILDCOUNT"] = file.groupby("CHILD")["CHILD"].transform("count")

        mask = file["CHILDCOUNT"] > 1
        epserrorlocations = file.loc[mask, "indexfile"]
        return {"PrevPerm": epserrorlocations.unique().tolist()}


def test_validate():
    erro_defn, error_func = validate_INT35()

    fake_dfs = {"PrevPerm": fake_INT_header}
    result = error_func(fake_dfs)
    assert result == {"PrevPerm": [0, 1, 2, 3, 4, 5, 6, 7]}
