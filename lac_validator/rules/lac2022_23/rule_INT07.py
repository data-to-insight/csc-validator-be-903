from lac_validator.rule_engine import rule_definition
from lac_validator.fixtures import fake_INT_header, fake_INT_file


@rule_definition(
code="INT07",
message="Internal Check: Child in PrevPerm does not exist in Header.",
affected_fields=["CHILD"],
)
def validate(dfs):
    
        if "Header" not in dfs or "PrevPerm" not in dfs:
            return {}
        else:
            header = dfs["Header"]
            file = dfs["PrevPerm"]

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
            return {"PrevPerm": eps_error_locations.unique().tolist()}

    


def test_validate():
    
    fake_dfs = {"Header": fake_INT_header.copy(), "PrevPerm": fake_INT_file.copy()}
    result = validate(fake_dfs)
    assert result == {"PrevPerm": [3]}
