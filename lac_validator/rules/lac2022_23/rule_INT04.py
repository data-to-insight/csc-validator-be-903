from lac_validator.fixtures import fake_INT_file, fake_INT_header
from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="INT04",
    message="Internal Check: Child in Missing does not exist in Header.",
    affected_fields=["CHILD"],
)
def validate(dfs):
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


def test_validate():
    fake_dfs = {"Header": fake_INT_header.copy(), "Missing": fake_INT_file.copy()}
    result = validate(fake_dfs)
    assert result == {"Missing": [3]}
