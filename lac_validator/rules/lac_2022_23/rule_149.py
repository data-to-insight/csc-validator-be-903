from validator903.types import ErrorDefinition


@rule_definition(
    code="149",
    message="Reason episode ceased code is not valid. ",
    affected_fields=["REC"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}

    episodes = dfs["Episodes"]
    codelist = [
        "E11",
        "E12",
        "E2",
        "E3",
        "E4A",
        "E4B",
        "E13",
        "E41",
        "E45",
        "E46",
        "E47",
        "E48",
        "E5",
        "E6",
        "E7",
        "E8",
        "E9",
        "E14",
        "E15",
        "E16",
        "E17",
        "X1",
    ]

    mask = episodes["REC"].isin(codelist) | episodes["REC"].isna()

    validationerrormask = ~mask
    validationerrorlocations = episodes.index[validationerrormask]

    return {"Episodes": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "REC": ["E4A", "E4b", "X", "", pd.NA],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [1, 2, 3]}
