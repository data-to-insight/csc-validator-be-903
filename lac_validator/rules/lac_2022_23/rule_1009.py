from validator903.types import ErrorDefinition


@rule_definition(
    code="1009",
    message="Reason for placement change is not a valid code.",
    affected_fields=["REASON_PLACE_CHANGE"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}

    episodes = dfs["Episodes"]
    codelist = [
        "CARPL",
        "CLOSE",
        "ALLEG",
        "STAND",
        "APPRR",
        "CREQB",
        "CREQO",
        "CHILD",
        "LAREQ",
        "PLACE",
        "CUSTOD",
        "OTHER",
    ]

    mask = (
        episodes["REASONPLACECHANGE"].isin(codelist)
        | episodes["REASONPLACECHANGE"].isna()
    )

    validationerrormask = ~mask
    validationerrorlocations = episodes.index[validationerrormask]

    return {"Episodes": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "REASON_PLACE_CHANGE": ["CARPL", "OTHER", "other", "NA", "", pd.NA],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [2, 3, 4]}
