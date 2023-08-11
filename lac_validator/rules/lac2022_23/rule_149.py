import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="149",
    message="Reason episode ceased code is not valid. ",
    affected_fields=["REC"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}

    episodes = dfs["Episodes"]
    code_list = [
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

    mask = episodes["REC"].isin(code_list) | episodes["REC"].isna()

    validation_error_mask = ~mask
    validation_error_locations = episodes.index[validation_error_mask]

    return {"Episodes": validation_error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "REC": ["E4A", "E4b", "X", "", pd.NA],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    result = validate(fake_dfs)

    assert result == {"Episodes": [1, 2, 3]}
