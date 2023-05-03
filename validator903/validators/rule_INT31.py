from validator903.types import IntegrityCheckDefinition


def validate():
    error = IntegrityCheckDefinition(
        code="INT31",
        description="Internal Check: Child should only exist once in AD1.",
        affected_fields=["CHILD"],
    )

    def _validate(dfs):
        if "AD1" not in dfs:
            return {}
        else:
            file = dfs["AD1"]

            file["index_file"] = file.index

            file["CHILD_COUNT"] = file.groupby("CHILD")["CHILD"].transform("count")

            mask = file["CHILD_COUNT"] > 1
            eps_error_locations = file.loc[mask, "index_file"]
            return {"AD1": eps_error_locations.unique().tolist()}

    return error, _validate


def test_validate():
    erro_defn, error_func = validate_INT31()

    fake_dfs = {"AD1": fake_INT_header}
    result = error_func(fake_dfs)
    assert result == {"AD1": [0, 1, 2, 3, 4, 5, 6, 7]}
