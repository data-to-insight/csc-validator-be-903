from lac_validator.fixtures import fake_INT_file, fake_INT_header
from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="INT31",
    message="Internal Check: Child should only exist once in AD1.",
    affected_fields=["CHILD"],
)
def validate(dfs):
    if "AD1" not in dfs:
        return {}
    else:
        file = dfs["AD1"]

        file["index_file"] = file.index

        file["CHILD_COUNT"] = file.groupby("CHILD")["CHILD"].transform("count")

        mask = file["CHILD_COUNT"] > 1
        eps_error_locations = file.loc[mask, "index_file"]
        return {"AD1": eps_error_locations.unique().tolist()}


def test_validate():
    fake_dfs = {"AD1": fake_INT_header.copy()}
    result = validate(fake_dfs)
    assert result == {"AD1": [0, 1, 2, 3, 4, 5, 6, 7]}
