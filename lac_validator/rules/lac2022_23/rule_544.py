import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="544",
    message="Any child who has conviction information completed must also have immunisation, teeth check, health assessment and substance misuse problem identified fields completed.",
    affected_fields=[
        "CONVICTED",
        "IMMUNISATIONS",
        "TEETH_CHECK",
        "HEALTH_ASSESSMENT",
        "SUBSTANCE_MISUSE",
    ],
)
def validate(dfs):
    if "OC2" not in dfs:
        return {}
    else:
        oc2 = dfs["OC2"]

        convict = oc2["CONVICTED"].astype(str) == "1"
        immunisations = oc2["IMMUNISATIONS"].isna()
        teeth_ck = oc2["TEETH_CHECK"].isna()
        health_ass = oc2["HEALTH_ASSESSMENT"].isna()
        sub_misuse = oc2["SUBSTANCE_MISUSE"].isna()

        error_mask = convict & (immunisations | teeth_ck | health_ass | sub_misuse)
        validation_error_locations = oc2.index[error_mask]

        return {"OC2": validation_error_locations.to_list()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "CONVICTED": [pd.NA, 1, "1", 1, "1", 1, "1", 1, "1", 1],
            "IMMUNISATIONS": [
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                1,
            ],
            "TEETH_CHECK": [
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                "1",
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                1,
            ],
            "HEALTH_ASSESSMENT": [
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                "1",
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                1,
            ],
            "SUBSTANCE_MISUSE": [
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                1,
            ],
        }
    )

    fake_dfs = {"OC2": fake_data}

    result = validate(fake_dfs)

    assert result == {"OC2": [1, 2, 3, 4, 5, 6, 7, 8]}
