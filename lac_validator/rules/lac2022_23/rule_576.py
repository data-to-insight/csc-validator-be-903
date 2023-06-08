import pandas as pd

from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="576",
    message="There is an open missing/away from placement without authorisation period in "
    + "last year’s return and there is no corresponding period recorded at the start of "
    + "this year.",
    affected_fields=["CHILD"],
)
def validate(dfs):
    if "Missing" not in dfs or "Missing_last" not in dfs:
        return {}
    else:
        mis = dfs["Missing"]
        mis_l = dfs["Missing_last"]
        mis["MIS_START"] = pd.to_datetime(
            mis["MIS_START"], format="%d/%m/%Y", errors="coerce"
        )
        mis_l["MIS_START"] = pd.to_datetime(
            mis_l["MIS_START"], format="%d/%m/%Y", errors="coerce"
        )

        mis.reset_index(inplace=True)
        mis["MIS_START"].fillna(
            pd.to_datetime("01/01/2099", format="%d/%m/%Y", errors="coerce"),
            inplace=True,
        )
        min_mis = mis.groupby(["CHILD"])["MIS_START"].idxmin()
        mis = mis.loc[min_mis, :]

        open_mis_l = mis_l.query("MIS_END.isnull()")

        err_coh = mis.merge(open_mis_l, how="left", on="CHILD", suffixes=["", "_LAST"])
        err_coh = err_coh.query(
            "(MIS_START != MIS_START_LAST) & MIS_START_LAST.notnull()"
        )

        err_list = err_coh["index"].unique().tolist()
        err_list.sort()
        return {"Missing": err_list}


def test_validate():
    import pandas as pd

    fake_mis_l = pd.DataFrame(
        [
            {"CHILD": "111", "MIS_START": "07/02/2020", "MIS_END": "07/02/2020"},  # 0
            {"CHILD": "222", "MIS_START": "07/02/2020", "MIS_END": pd.NA},  # 1
            {"CHILD": "333", "MIS_START": "03/02/2020", "MIS_END": "07/02/2020"},  # 2
            {"CHILD": "444", "MIS_START": "07/02/2020", "MIS_END": pd.NA},  # 3
            {"CHILD": "555", "MIS_START": "01/02/2020", "MIS_END": pd.NA},  # 4
            {"CHILD": "666", "MIS_START": "13/02/2020", "MIS_END": "07/02/2020"},  # 5
        ]
    )
    fake_mis = pd.DataFrame(
        [
            {"CHILD": "111", "MIS_START": "07/02/2020"},  # 0
            {"CHILD": "222", "MIS_START": "08/02/2020"},  # 1 Fails
            {"CHILD": "333", "MIS_START": "03/02/2020"},  # 2
            {"CHILD": "444", "MIS_START": pd.NA},  # 3 Fails
            {"CHILD": "555", "MIS_START": "01/02/2020"},  # 4
            {"CHILD": "666", "MIS_START": "13/02/2020"},  # 5
        ]
    )
    fake_dfs = {"Missing_last": fake_mis_l, "Missing": fake_mis}

    

    assert validate(fake_dfs) == {"Missing": [1, 3]}
