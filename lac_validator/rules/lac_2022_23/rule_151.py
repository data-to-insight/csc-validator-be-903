from validator903.types import ErrorDefinition


@rule_definition(
    code="151",
    message="All data items relating to a childs adoption must be coded or left blank.",
    affected_fields=[
        "DATE_INT",
        "DATE_MATCH",
        "FOSTER_CARE",
        "NB_ADOPTER",
        "SEX_ADOPTR",
        "LS_ADOPTR",
    ],
)
def validate(dfs):
    if "AD1" not in dfs:
        return {}
    else:
        ad1 = dfs["AD1"]
        nadateint = ad1["DATEINT"].isna()
        nadatematch = ad1["DATEMATCH"].isna()
        nafostercare = ad1["FOSTERCARE"].isna()
        nanbadoptr = ad1["NBADOPTR"].isna()
        nasexadoptr = ad1["SEXADOPTR"].isna()
        nalsadoptr = ad1["LSADOPTR"].isna()

        ad1notnull = (
            ~nadateint
            & ~nadatematch
            & ~nafostercare
            & ~nanbadoptr
            & ~nasexadoptr
            & ~nalsadoptr
        )

        validationerror = (
            ~nadateint
            | ~nadatematch
            | ~nafostercare
            | ~nanbadoptr
            | ~nasexadoptr
            | ~nalsadoptr
        ) & ~ad1notnull
        validationerrorlocations = ad1.index[validationerror]

        return {"AD1": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "DATE_INT": [
                pd.NA,
                "01/01/2021",
                "01/01/2021",
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                "01/01/2021",
            ],
            "DATE_MATCH": [
                pd.NA,
                "01/01/2021",
                pd.NA,
                "01/01/2021",
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
            ],
            "FOSTER_CARE": [
                pd.NA,
                "01/01/2021",
                pd.NA,
                pd.NA,
                "01/01/2021",
                pd.NA,
                pd.NA,
                pd.NA,
                "01/01/2021",
            ],
            "NB_ADOPTR": [
                pd.NA,
                "01/01/2021",
                pd.NA,
                pd.NA,
                pd.NA,
                "01/01/2021",
                pd.NA,
                pd.NA,
                pd.NA,
            ],
            "SEX_ADOPTR": [
                pd.NA,
                "01/01/2021",
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                "01/01/2021",
                pd.NA,
                "01/01/2021",
            ],
            "LS_ADOPTR": [
                pd.NA,
                "01/01/2021",
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                "01/01/2021",
                pd.NA,
            ],
        }
    )

    fake_dfs = {"AD1": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)
    assert result == {"AD1": [2, 3, 4, 5, 6, 7, 8]}
