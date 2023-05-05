import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="141",
    message="Date episode began is not a valid date.",
    affected_fields=["DECOM"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        mask = pd.todatetime(
            episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
        ).notna()

        nalocation = episodes["DECOM"].isna()

        validationerrormask = ~mask & ~nalocation
        validationerrorlocations = episodes.index[validationerrormask]

        return {"Episodes": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "DECOM": ["01/01/2021", "19/02/2010", "38/04/2019", "01/01/19", pd.NA],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [2, 3]}
