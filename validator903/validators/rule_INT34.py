from validator903.types import IntegrityCheckDefinition


def validate():
    error = IntegrityCheckDefinition(
        code="INT34",
        description="Internal Check: Child should only exist once in OC3.",
        affected_fields=["CHILD"],
    )

    def _validate(dfs):
        if "OC3" not in dfs:
            return {}
        else:
            file = dfs["OC3"]

            file["index_file"] = file.index

            file["CHILD_COUNT"] = file.groupby("CHILD")["CHILD"].transform("count")

            mask = file["CHILD_COUNT"] > 1
            eps_error_locations = file.loc[mask, "index_file"]
            return {"OC3": eps_error_locations.unique().tolist()}

    return error, _validate


def test_validate():
    erro_defn, error_func = validate_INT34()

    fake_dfs = {"OC3": fake_INT_header}
    result = error_func(fake_dfs)
    assert result == {"OC3": [0, 1, 2, 3, 4, 5, 6, 7]}
