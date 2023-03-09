from validator903.types import IntegrityCheckDefinition


def validate():
    error = IntegrityCheckDefinition(
        code="INT04",
        description="Internal Check: Child in Missing does not exist in Header.",
        affected_fields=["CHILD"],
    )

    def _validate(dfs):
        if "Header" not in dfs or "Missing" not in dfs:
            return {}
        else:
            header = dfs["Header"]
            file = dfs["Missing"]

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
            return {"Missing": eps_error_locations.unique().tolist()}

    return error, _validate


def test_validate():
    erro_defn, error_func = validate_INT04()

    fake_dfs = {"Header": fake_INT_header, "Missing": fake_INT_file}
    result = error_func(fake_dfs)
    assert result == {"Missing": [3]}
