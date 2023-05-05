from validator903.types import ErrorDefinition


@rule_definition(
    code="145",
    message="Category of need code is not a valid code.",
    affected_fields=["CIN"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}

    episodes = dfs["Episodes"]
    codelist = [
        "N1",
        "N2",
        "N3",
        "N4",
        "N5",
        "N6",
        "N7",
        "N8",
    ]

    mask = episodes["CIN"].isin(codelist) | episodes["CIN"].isna()
    validationerrormask = ~mask
    validationerrorlocations = episodes.index[validationerrormask]

    return {"Episodes": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "CIN": ["N0", "N1", "N9", "n8", "", pd.NA],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [0, 2, 3, 4]}
