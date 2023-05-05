from validator903.types import ErrorDefinition


@rule_definition(
    code="178",
    message="Placement provider code is not a valid code.",
    affected_fields=["PLACE_PROVIDER"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}

    episodes = dfs["Episodes"]

    codelistplacementprovider = ["PR0", "PR1", "PR2", "PR3", "PR4", "PR5"]
    codelistplacementwithnoprovider = ["T0", "T1", "T2", "T3", "T4", "Z1"]

    placeproviderneededandcorrect = episodes["PLACEPROVIDER"].isin(
        codelistplacementprovider
    ) & ~episodes["PLACE"].isin(codelistplacementwithnoprovider)

    placeprovidernotprovided = episodes["PLACEPROVIDER"].isna()

    placeprovidernotneeded = episodes["PLACEPROVIDER"].isna() & episodes["PLACE"].isin(
        codelistplacementwithnoprovider
    )

    mask = (
        placeproviderneededandcorrect
        | placeprovidernotprovided
        | placeprovidernotneeded
    )

    validationerrormask = ~mask
    validationerrorlocations = episodes.index[validationerrormask]

    return {"Episodes": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "PLACE_PROVIDER": ["PR0", "PR1", "", pd.NA, "", pd.NA],
            "PLACE": ["U1", "T0", "U2", "Z1", "T1", pd.NA],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [1, 2, 4]}
