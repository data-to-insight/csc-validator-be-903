import pandas as pd

from lac_validator.rule_engine import rule_definition


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
        mis["MIS_START"] = pd.to_datetime(
            mis["MIS_START"], format="%d/%m/%Y", errors="coerce"
        )
        mis["MIS_END"] = pd.to_datetime(
            mis["MIS_END"], format="%d/%m/%Y", errors="coerce"
        )

        mis["MIS_END_FILL"] = mis["MIS_END"].fillna(mis["MIS_START"])
        mis.sort_values(["CHILD", "MIS_END_FILL", "MIS_START"], inplace=True)

        mis.reset_index(inplace=True)
        mis.reset_index(inplace=True)  # Twice on purpose

        mis["LAG_INDEX"] = mis["level_0"].shift(-1)

        lag_mis = mis.merge(
            mis,
            how="inner",
            left_on="level_0",
            right_on="LAG_INDEX",
            suffixes=["", "_PREV"],
        )

        # We're only interested in cases where there is more than one row for a child.
        lag_mis = lag_mis[lag_mis["CHILD"] == lag_mis["CHILD_PREV"]]

        # A previous MIS_END date is null
        mask1 = lag_mis["MIS_END_PREV"].isna()
        # MIS_START is before previous MIS_END (overlapping dates)
        mask2 = lag_mis["MIS_START"] < lag_mis["MIS_END_PREV"]

        mask = mask1 | mask2

        error_list = lag_mis["index"][mask].to_list()
        error_list.sort()
        return {"Missing": error_list}


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

    result = validate(fake_dfs)

    assert result == {"Missing": [0, 4, 6, 9]}
