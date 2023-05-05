import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="446",
    message="E1 is not a valid code for episodes starting before December 2005.",
    affected_fields=["LS", "DECOM"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        episodes["DECOM"] = pd.todatetime(
            episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        mindecomallowed = pd.todatetime(
            "01/12/2005", format="%d/%m/%Y", errors="coerce"
        )

        mask = episodes["LS"].eq("E1") & (episodes["DECOM"] < mindecomallowed)
        validationerrormask = mask
        validationerrorlocations = episodes.index[validationerrormask]

        return {"Episodes": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "LS": ["E1", "E1", "E1", "E1", "E1", "C1"],
            "DECOM": [
                "01/12/2005",
                "15/05/2012",
                pd.NA,
                "20/09/2004",
                "01/10/2005",
                "20/02/2005",
            ],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [3, 4]}
