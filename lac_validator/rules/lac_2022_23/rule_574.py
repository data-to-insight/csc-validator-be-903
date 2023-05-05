import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="574",
    message="A new missing/away from placement without authorisation period cannot start when the previous missing/away from placement without authorisation period is still open. Missing/away from placement without authorisation periods should also not overlap.",
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

        mis["MISENDFILL"] = mis["MISEND"].fillna(mis["MISSTART"])
        mis.sortvalues(["CHILD", "MISENDFILL", "MISSTART"], inplace=True)

        mis.resetindex(inplace=True)
        mis.resetindex(inplace=True)  # Twice on purpose

        mis["LAGINDEX"] = mis["level0"].shift(-1)

        lagmis = mis.merge(
            mis,
            how="inner",
            lefton="level0",
            righton="LAGINDEX",
            suffixes=["", "PREV"],
        )

        # We're only interested in cases where there is more than one row for a child.
        lagmis = lagmis[lagmis["CHILD"] == lagmis["CHILDPREV"]]

        # A previous MISEND date is null
        mask1 = lagmis["MISENDPREV"].isna()
        # MISSTART is before previous MISEND (overlapping dates)
        mask2 = lagmis["MISSTART"] < lagmis["MISENDPREV"]

        mask = mask1 | mask2

        errorlist = lagmis["index"][mask].tolist()
        errorlist.sort()
        return {"Missing": errorlist}


def test_validate():
    import pandas as pd

    fake_mis = pd.DataFrame(
        [
            {
                "CHILD": "111",
                "MIS_START": "01/06/2020",
                "MIS_END": "05/06/2020",
            },  # 0 Fails, previous end is null
            {"CHILD": "111", "MIS_START": "04/06/2020", "MIS_END": pd.NA},  # 1
            {"CHILD": "222", "MIS_START": "03/06/2020", "MIS_END": "04/06/2020"},  # 2
            {"CHILD": "222", "MIS_START": "04/06/2020", "MIS_END": pd.NA},  # 3
            {
                "CHILD": "222",
                "MIS_START": "07/06/2020",
                "MIS_END": "09/06/2020",
            },  # 4 Fails, previous end is null
            {"CHILD": "333", "MIS_START": "02/06/2020", "MIS_END": "04/06/2020"},  # 5
            {
                "CHILD": "333",
                "MIS_START": "03/06/2020",
                "MIS_END": "09/06/2020",
            },  # 6 Fails, overlaps previous
            {"CHILD": "444", "MIS_START": "06/06/2020", "MIS_END": "08/06/2020"},  # 7
            {"CHILD": "444", "MIS_START": "10/06/2020", "MIS_END": "10/06/2020"},  # 8
            {
                "CHILD": "444",
                "MIS_START": "08/06/2020",
                "MIS_END": "10/08/2020",
            },  # 9 Fails, overlaps previous
            {"CHILD": "555", "MIS_START": pd.NA, "MIS_END": "05/06/2020"},  # 10
            {"CHILD": "555", "MIS_START": pd.NA, "MIS_END": "05/06/2020"},  # 11
        ]
    )

    fake_dfs = {"Missing": fake_mis}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Missing": [0, 4, 6, 9]}
