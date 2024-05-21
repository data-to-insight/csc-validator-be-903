import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="511",
    message="If reporting that the number of person(s) adopting the looked after child is two adopters then the code should only be MM, FF or MF. MM = the adopting couple are both males; FF = the adopting couple are both females; MF = The adopting couple are male and female.",
    affected_fields=["NB_ADOPTR", "SEX_ADOPTR"],
    tables=["AD1"],
)
def validate(dfs):
    if "AD1" not in dfs:
        return {}

    else:
        AD1 = dfs["AD1"]

        mask = AD1["NB_ADOPTR"].astype(str).eq("2") & AD1["SEX_ADOPTR"].isin(
            ["M1", "F1"]
        )

        validation_error_mask = mask
        validation_error_locations = AD1.index[validation_error_mask]

        return {"AD1": validation_error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "NB_ADOPTR": ["2", "2", pd.NA, 2, "2", "1", 2, 1, 2],
            "SEX_ADOPTR": ["MM", "FF", "MM", "M1", "F1", "F1", "F1", "F1", pd.NA],
        }
    )

    fake_dfs = {"AD1": fake_data}

    result = validate(fake_dfs)

    assert result == {"AD1": [3, 4, 6]}
