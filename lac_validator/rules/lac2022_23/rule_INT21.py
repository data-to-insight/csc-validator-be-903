from lac_validator.fixtures import fake_INT_file, fake_INT_header
from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="INT21",
    message="Internal Check: SEX in UASC is different to SEX in Header.",
    affected_fields=["SEX"],
)
def validate(dfs):
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


def test_validate():
    fake_dfs = {"Header": fake_INT_header.copy(), "UASC": fake_INT_file.copy()}
    result = validate(fake_dfs)
    assert result == {"UASC": [2]}
