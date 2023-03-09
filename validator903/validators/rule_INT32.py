from validator903.types import IntegrityCheckDefinition


def validate():
    error = IntegrityCheckDefinition(
        code="INT32",
        description="Internal Check: Child should only exist once in Header.",
        affected_fields=["CHILD"],
    )

    def _validate(dfs):
        if "Header" not in dfs:
            return {}
        else:
            file = dfs["Header"]

            file["index_file"] = file.index

            file["CHILD_COUNT"] = file.groupby("CHILD")["CHILD"].transform("count")

            mask = file["CHILD_COUNT"] > 1
            eps_error_locations = file.loc[mask, "index_file"]
            return {"Header": eps_error_locations.unique().tolist()}

    return error, _validate


def test_validate():
    erro_defn, error_func = validate_INT32()

    fake_dfs = {"Header": fake_INT_header}
    result = error_func(fake_dfs)
    assert result == {"Header": [0, 1, 2, 3, 4, 5, 6, 7]}
