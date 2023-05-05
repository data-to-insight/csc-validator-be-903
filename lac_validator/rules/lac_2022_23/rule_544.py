from validator903.types import ErrorDefinition


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
        teethck = oc2["TEETHCHECK"].isna()
        healthass = oc2["HEALTHASSESSMENT"].isna()
        submisuse = oc2["SUBSTANCEMISUSE"].isna()

        errormask = convict & (immunisations | teethck | healthass | submisuse)
        validationerrorlocations = oc2.index[errormask]

        return {"OC2": validationerrorlocations.tolist()}


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

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"OC2": [1, 2, 3, 4, 5, 6, 7, 8]}
