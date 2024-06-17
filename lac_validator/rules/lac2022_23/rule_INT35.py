from lac_validator.fixtures import fake_INT_file, fake_INT_header
from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="INT35",
    message="Internal Check: Child should only exist once in PrevPerm.",
    affected_fields=["CHILD"],
    tables=["PrevPerm"],
)
def validate(dfs):
    if "PrevPerm" not in dfs:
        return {}
    else:
        file = dfs["PrevPerm"]

        file["index_file"] = file.index

        file["CHILD_COUNT"] = file.groupby("CHILD")["CHILD"].transform("count")

        mask = file["CHILD_COUNT"] > 1
        eps_error_locations = file.loc[mask, "index_file"]
        return {"PrevPerm": eps_error_locations.unique().tolist()}


def test_validate():
    fake_dfs = {"PrevPerm": fake_INT_header.copy()}
    result = validate(fake_dfs)
    assert result == {"PrevPerm": [0, 1, 2, 3, 4, 5, 6, 7]}
