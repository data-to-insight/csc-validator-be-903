from validator903.types import ErrorDefinition


@rule_definition(
    code="144",
    message="The legal status code is not a valid code.",
    affected_fields=["LS"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}

    episodes = dfs["Episodes"]
    codelist = [
        "C1",
        "C2",
        "D1",
        "E1",
        "V2",
        "V3",
        "V4",
        "J1",
        "J2",
        "J3",
        "L1",
        "L2",
        "L3",
    ]

    mask = episodes["LS"].isin(codelist) | episodes["LS"].isna()

    validationerrormask = ~mask
    validationerrorlocations = episodes.index[validationerrormask]

    return {"Episodes": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "LS": ["C1", "c1", "section 20", "", pd.NA],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [1, 2, 3]}
