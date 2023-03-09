from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="151",
        description="All data items relating to a childs adoption must be coded or left blank.",
        affected_fields=[
            "DATE_INT",
            "DATE_MATCH",
            "FOSTER_CARE",
            "NB_ADOPTER",
            "SEX_ADOPTR",
            "LS_ADOPTR",
        ],
    )

    def _validate(dfs):
        if "AD1" not in dfs:
            return {}
        else:
            ad1 = dfs["AD1"]
            na_date_int = ad1["DATE_INT"].isna()
            na_date_match = ad1["DATE_MATCH"].isna()
            na_foster_care = ad1["FOSTER_CARE"].isna()
            na_nb_adoptr = ad1["NB_ADOPTR"].isna()
            na_sex_adoptr = ad1["SEX_ADOPTR"].isna()
            na_lsadoptr = ad1["LS_ADOPTR"].isna()

            ad1_not_null = (
                ~na_date_int
                & ~na_date_match
                & ~na_foster_care
                & ~na_nb_adoptr
                & ~na_sex_adoptr
                & ~na_lsadoptr
            )

            validation_error = (
                ~na_date_int
                | ~na_date_match
                | ~na_foster_care
                | ~na_nb_adoptr
                | ~na_sex_adoptr
                | ~na_lsadoptr
            ) & ~ad1_not_null
            validation_error_locations = ad1.index[validation_error]

            return {"AD1": validation_error_locations.tolist()}

    return error, _validate


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
