from lac_validator.fixtures import fake_INT_file, fake_INT_header
from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="INT05",
    message="Internal Check: Child in OC2 does not exist in Header.",
    affected_fields=["CHILD"],
    tables=["Header", "OC2"],
)
def validate(dfs):
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


def test_validate():
    fake_dfs = {"Header": fake_INT_header.copy(), "OC2": fake_INT_file.copy()}
    result = validate(fake_dfs)
    assert result == {"OC2": [3]}
