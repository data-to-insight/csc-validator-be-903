from validator903.types import IntegrityCheckDefinition


def validate():
    error = IntegrityCheckDefinition(
        code="INT21",
        description="Internal Check: SEX in UASC is different to SEX in Header.",
        affected_fields=["SEX"],
    )

    def _validate(dfs):
        if "Header" not in dfs or "UASC" not in dfs:
            return {}
        else:
            header = dfs["Header"]
            file = dfs["UASC"]

            file["index_file"] = file.index

            merged = header.merge(
                file[["CHILD", "SEX", "index_file"]],
                on="CHILD",
                indicator=True,
                how="right",
                suffixes=["_header", "_file"],
            )

            mask = (
                (merged["SEX_header"] != merged["SEX_file"])
                & (merged["SEX_header"].notna() & merged["SEX_file"].notna())
                & (merged["_merge"] != "right_only")
            )
            eps_error_locations = merged.loc[mask, "index_file"]
            return {"UASC": eps_error_locations.unique().tolist()}

    return error, _validate


def test_validate():
    erro_defn, error_func = validate_INT21()

    fake_dfs = {"Header": fake_INT_header, "UASC": fake_INT_file}
    result = error_func(fake_dfs)
    assert result == {"UASC": [2]}
