from validator903.types import IntegrityCheckDefinition


def validate(dfs):
    if "UASC" not in dfs:
        return {}
    else:
        file = dfs["UASC"]

        file["indexfile"] = file.index

        file["CHILDCOUNT"] = file.groupby("CHILD")["CHILD"].transform("count")

        mask = file["CHILDCOUNT"] > 1
        epserrorlocations = file.loc[mask, "indexfile"]
        return {"UASC": epserrorlocations.unique().tolist()}


def test_validate():
    erro_defn, error_func = validate_INT36()

    fake_dfs = {"UASC": fake_INT_header}
    result = error_func(fake_dfs)
    assert result == {"UASC": [0, 1, 2, 3, 4, 5, 6, 7]}
