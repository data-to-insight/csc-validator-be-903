import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="217",
    message="Children who are placed for adoption with current foster carers (placement types A3 or A5) must have a reason for new episode of S, T or U.",
    affected_fields=["PLACE", "DECOM", "RNE"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        episodes["DECOM"] = pd.todatetime(
            episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        maxdecomallowed = pd.todatetime(
            "01/04/2015", format="%d/%m/%Y", errors="coerce"
        )
        reasonnewep = ["S", "T", "U"]
        placecodes = ["A3", "A5"]

        mask = (
            episodes["PLACE"].isin(placecodes) & (episodes["DECOM"] >= maxdecomallowed)
        ) & ~episodes["RNE"].isin(reasonnewep)

        validationerrormask = mask
        validationerrorlocations = episodes.index[validationerrormask]

        return {"Episodes": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "PLACE": ["A3", "A5", "A3", pd.NA, "U1", "A3", "A5", "A5"],
            "DECOM": [
                "01/04/2015",
                "31/12/2015",
                "20/01/2016",
                pd.NA,
                "01/10/2017",
                "20/02/2016",
                "01/01/2017",
                "01/04/2013",
            ],
            "RNE": ["S", "T", "U", pd.NA, "X", "X", "X", "X"],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [5, 6]}
