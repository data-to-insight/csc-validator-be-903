import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="1004",
    message="The start date of the missing episode or episode that the child was away from placement without authorisation is not a valid date.",
    affected_fields=["MIS_START"],
)
def validate(dfs):
    if "Missing" not in dfs:
        return {}
    else:
        missing = dfs["Missing"]

        missing["fMISSTART"] = pd.todatetime(
            missing["MISSTART"], format="%d/%m/%Y", errors="coerce"
        )

        missingstartdate = missing["MISSTART"].isna()
        invalidstartdate = missing["fMISSTART"].isna()

        errormask = missingstartdate | invalidstartdate

        errorlocations = missing.index[errormask]

        return {"Missing": errorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "MIS_START": [
                "08/03/2020",
                "22/06/2020",
                pd.NA,
                "13/10/2021",
                "10/24/2021",
            ],
            "MIS_END": ["08/03/2020", pd.NA, "22/06/2020", "13/10/21", pd.NA],
        }
    )

    fake_dfs = {"Missing": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Missing": [2, 4]}
