from lac_validator.fixtures import fake_INT_file, fake_INT_header
from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="INT36",
    message="Internal Check: Child should only exist once in UASC.",
    affected_fields=["CHILD"],
)
def validate(dfs):
    if "UASC" not in dfs:
        return {}
    else:
        file = dfs["UASC"]

        file["index_file"] = file.index

        file["CHILD_COUNT"] = file.groupby("CHILD")["CHILD"].transform("count")

        mask = file["CHILD_COUNT"] > 1
        eps_error_locations = file.loc[mask, "index_file"]
        return {"UASC": eps_error_locations.unique().tolist()}


def test_validate():
    fake_dfs = {"UASC": fake_INT_header.copy()}
    result = validate(fake_dfs)
    assert result == {"UASC": [0, 1, 2, 3, 4, 5, 6, 7]}
