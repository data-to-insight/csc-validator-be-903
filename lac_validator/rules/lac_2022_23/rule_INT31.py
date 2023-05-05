from validator903.types import IntegrityCheckDefinition


def validate(dfs):
    if "AD1" not in dfs:
        return {}
    else:
        file = dfs["AD1"]

        file["indexfile"] = file.index

        file["CHILDCOUNT"] = file.groupby("CHILD")["CHILD"].transform("count")

        mask = file["CHILDCOUNT"] > 1
        epserrorlocations = file.loc[mask, "indexfile"]
        return {"AD1": epserrorlocations.unique().tolist()}


def test_validate():
    erro_defn, error_func = validate_INT31()

    fake_dfs = {"AD1": fake_INT_header}
    result = error_func(fake_dfs)
    assert result == {"AD1": [0, 1, 2, 3, 4, 5, 6, 7]}
