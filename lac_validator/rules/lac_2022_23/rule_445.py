import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="445",
    message="D1 is not a valid code for episodes starting after December 2005.",
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
        maxdecomallowed = pd.todatetime(
            "31/12/2005", format="%d/%m/%Y", errors="coerce"
        )

        mask = episodes["LS"].eq("D1") & (episodes["DECOM"] > maxdecomallowed)
        validationerrormask = mask
        validationerrorlocations = episodes.index[validationerrormask]

        return {"Episodes": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "LS": ["D1", "D1", "D1", "D1", "D1", "C1"],
            "DECOM": [
                "01/11/2005",
                "31/12/2005",
                pd.NA,
                "20/01/2006",
                "01/10/2012",
                "20/02/2005",
            ],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [3, 4]}
