import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="567",
    message="The date that the missing episode or episode that the child was away from placement without authorisation ended is before the date that it started.",
    affected_fields=["MIS_START", "MIS_END"],
)
def validate(dfs):
    if "Missing" not in dfs:
        return {}
    else:
        mis = dfs["Missing"]
        mis["MISSTART"] = pd.todatetime(
            mis["MISSTART"], format="%d/%m/%Y", errors="coerce"
        )
        mis["MISEND"] = pd.todatetime(mis["MISEND"], format="%d/%m/%Y", errors="coerce")

        miserror = mis[mis["MISSTART"] > mis["MISEND"]]

        return {"Missing": miserror.index.tolist()}


def test_validate():
    import pandas as pd

    fake_mis = pd.DataFrame(
        [
            {"MIS_START": "01/06/2020", "MIS_END": "05/06/2020"},  # 0
            {"MIS_START": "02/06/2020", "MIS_END": pd.NA},  # 1
            {"MIS_START": "03/06/2020", "MIS_END": "01/06/2020"},  # 2 Fails
            {"MIS_START": "04/06/2020", "MIS_END": "02/06/2020"},  # 3 Fails
            {"MIS_START": pd.NA, "MIS_END": "05/06/2020"},  # 4
        ]
    )

    fake_dfs = {"Missing": fake_mis}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Missing": [2, 3]}
