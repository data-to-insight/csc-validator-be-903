from validator903.types import ErrorDefinition


@rule_definition(
    code="451",
    message="Child is still freed for adoption, but freeing orders could not be applied for since 30 December 2005.",
    affected_fields=["DEC", "REC", "LS"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        mask = (
            episodes["DEC"].isna() & episodes["REC"].isna() & (episodes["LS"] == "D1")
        )
        errorlocations = episodes.index[mask]
        return {"Episodes": errorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "CHILD": ["101", "102", "101", "102", "103", "104"],
            "REC": ["E11", "E12", "X1", pd.NA, "E11", "E11"],
            "DEC": [
                "15/03/2021",
                "17/06/2020",
                "20/03/2020",
                pd.NA,
                "23/08/2020",
                pd.NA,
            ],
            "LS": ["J2", "X", "J2", "D1", "D", "D1"],
        }
    )
    fake_dfs = {"Episodes": fake_data}
    error_defn, error_func = validate()
    result = error_func(fake_dfs)
    assert result == {"Episodes": [3]}
