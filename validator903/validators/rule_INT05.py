from validator903.types import IntegrityCheckDefinition


def validate():
    error = IntegrityCheckDefinition(
        code="INT05",
        description="Internal Check: Child in OC2 does not exist in Header.",
        affected_fields=["CHILD"],
    )

    def _validate(dfs):
        if "Header" not in dfs or "OC2" not in dfs:
            return {}
        else:
            header = dfs["Header"]
            file = dfs["OC2"]

            file["index_file"] = file.index

            merged = header.merge(
                file[["CHILD", "index_file"]],
                on="CHILD",
                indicator=True,
                how="right",
                suffixes=["_header", "_file"],
            )

            mask = merged["_merge"] == "right_only"
            eps_error_locations = merged.loc[mask, "index_file"]
            return {"OC2": eps_error_locations.unique().tolist()}

    return error, _validate


def test_validate():
    erro_defn, error_func = validate_INT05()

    fake_dfs = {"Header": fake_INT_header, "OC2": fake_INT_file}
    result = error_func(fake_dfs)
    assert result == {"OC2": [3]}
