from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="134",
    message="Data on adoption should not be entered for the OC3 cohort.",
    affected_fields=[
        "IN_TOUCH",
        "ACTIV",
        "ACCOM",
        "DATE_INT",
        "DATE_MATCH",
        "FOSTER_CARE",
        "NB_ADOPTR",
        "SEX_ADOPTR",
        "LS_ADOPTR",
    ],
)
def validate(dfs):
    if "OC3" not in dfs or "AD1" not in dfs:
        return {}
    else:
        oc3 = dfs["OC3"]
        ad1 = dfs["AD1"]
        ad1["ad1_index"] = ad1.index

        all_data = ad1.merge(oc3, how="left", on="CHILD")

        na_oc3_data = (
            all_data["IN_TOUCH"].isna()
            & all_data["ACTIV"].isna()
            & all_data["ACCOM"].isna()
        )

        na_ad1_data = (
            all_data["DATE_INT"].isna()
            & all_data["DATE_MATCH"].isna()
            & all_data["FOSTER_CARE"].isna()
            & all_data["NB_ADOPTR"].isna()
            & all_data["SEX_ADOPTR"].isna()
            & all_data["LS_ADOPTR"].isna()
        )

        validation_error = ~na_oc3_data & ~na_ad1_data
        validation_error_locations = all_data.loc[
            validation_error, "ad1_index"
        ].unique()

        return {"AD1": validation_error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_data_oc3 = pd.DataFrame(
        {
            "CHILD": ["A", "B", "C", "D", "E"],
            "IN_TOUCH": [pd.NA, "XXX", pd.NA, pd.NA, pd.NA],
            "ACTIV": [pd.NA, pd.NA, "XXX", pd.NA, pd.NA],
            "ACCOM": [pd.NA, pd.NA, pd.NA, "XXX", pd.NA],
        }
    )
    fake_data_ad1 = pd.DataFrame(
        {
            "CHILD": ["A", "B", "C", "D", "E"],
            "DATE_INT": [pd.NA, pd.NA, "XXX", pd.NA, "XXX"],
            "DATE_MATCH": [pd.NA, "XXX", "XXX", pd.NA, "XXX"],
            "FOSTER_CARE": [pd.NA, pd.NA, "XXX", pd.NA, "XXX"],
            "NB_ADOPTR": [pd.NA, pd.NA, "XXX", pd.NA, "XXX"],
            "SEX_ADOPTR": [pd.NA, pd.NA, "XXX", pd.NA, "XXX"],
            "LS_ADOPTR": [pd.NA, pd.NA, "XXX", "XXX", "XXX"],
        }
    )

    fake_dfs = {"OC3": fake_data_oc3, "AD1": fake_data_ad1}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"AD1": [1, 2, 3]}
