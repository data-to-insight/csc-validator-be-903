import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="547",
    message="Any child who has health promotion information completed must also have immunisation, teeth check, health assessment and substance misuse problem identified fields completed.",
    affected_fields=[
        "HEALTH_CHECK",
        "IMMUNISATIONS",
        "TEETH_CHECK",
        "HEALTH_ASSESSMENT",
        "SUBSTANCE_MISUSE",
    ],
    tables=["OC2"],
)
def validate(dfs):
    if "OC2" not in dfs:
        return {}
    else:
        oc2 = dfs["OC2"]

        healthck = oc2["HEALTH_CHECK"].astype(str) == "1"
        immunisations = oc2["IMMUNISATIONS"].isna()
        teeth_ck = oc2["TEETH_CHECK"].isna()
        health_ass = oc2["HEALTH_ASSESSMENT"].isna()
        sub_misuse = oc2["SUBSTANCE_MISUSE"].isna()

        error_mask = healthck & (immunisations | teeth_ck | health_ass | sub_misuse)
        validation_error_locations = oc2.index[error_mask]

        return {"OC2": validation_error_locations.to_list()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "HEALTH_CHECK": [pd.NA, 1, "1", 1, "1", 0, 1, pd.NA],
            "IMMUNISATIONS": [pd.NA, pd.NA, pd.NA, 1, pd.NA, pd.NA, 1, pd.NA],
            "TEETH_CHECK": [pd.NA, pd.NA, pd.NA, "1", "1", pd.NA, 1, "1"],
            "HEALTH_ASSESSMENT": [pd.NA, pd.NA, pd.NA, 0, "1", pd.NA, 1, 0],
            "SUBSTANCE_MISUSE": [pd.NA, pd.NA, pd.NA, 0, pd.NA, pd.NA, 1, "1"],
        }
    )

    fake_dfs = {"OC2": fake_data}

    result = validate(fake_dfs)

    assert result == {"OC2": [1, 2, 4]}
