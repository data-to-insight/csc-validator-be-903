import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="145",
    message="Category of need code is not a valid code.",
    affected_fields=["CIN"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}

    episodes = dfs["Episodes"]
    code_list = [
        "N1",
        "N2",
        "N3",
        "N4",
        "N5",
        "N6",
        "N7",
        "N8",
    ]

    mask = episodes["CIN"].isin(code_list) | episodes["CIN"].isna()
    validation_error_mask = ~mask
    validation_error_locations = episodes.index[validation_error_mask]

    return {"Episodes": validation_error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "CIN": ["N0", "N1", "N9", "n8", "", pd.NA],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    result = validate(fake_dfs)

    assert result == {"Episodes": [0, 2, 3, 4]}
