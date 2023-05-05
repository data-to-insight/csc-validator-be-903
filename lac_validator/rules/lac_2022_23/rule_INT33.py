from validator903.types import IntegrityCheckDefinition


def validate(dfs):
    if "OC2" not in dfs:
        return {}
    else:
        file = dfs["OC2"]

        file["indexfile"] = file.index

        file["CHILDCOUNT"] = file.groupby("CHILD")["CHILD"].transform("count")

        mask = file["CHILDCOUNT"] > 1
        epserrorlocations = file.loc[mask, "indexfile"]
        return {"OC2": epserrorlocations.unique().tolist()}


def test_validate():
    erro_defn, error_func = validate_INT33()

    fake_dfs = {"OC2": fake_INT_header}
    result = error_func(fake_dfs)
    assert result == {"OC2": [0, 1, 2, 3, 4, 5, 6, 7]}
