import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="576",
    message="There is an open missing/away from placement without authorisation period in "
    + "last year’s return and there is no corresponding period recorded at the start of "
    + "this year.",
    affected_fields=["CHILD"],
)
def validate(dfs):
    if "Missing" not in dfs or "Missinglast" not in dfs:
        return {}
    else:
        mis = dfs["Missing"]
        misl = dfs["Missinglast"]
        mis["MISSTART"] = pd.todatetime(
            mis["MISSTART"], format="%d/%m/%Y", errors="coerce"
        )
        misl["MISSTART"] = pd.todatetime(
            misl["MISSTART"], format="%d/%m/%Y", errors="coerce"
        )

        mis.resetindex(inplace=True)
        mis["MISSTART"].fillna(
            pd.todatetime("01/01/2099", format="%d/%m/%Y", errors="coerce"),
            inplace=True,
        )
        minmis = mis.groupby(["CHILD"])["MISSTART"].idxmin()
        mis = mis.loc[minmis, :]

        openmisl = misl.query("MISEND.isnull()")

        errcoh = mis.merge(openmisl, how="left", on="CHILD", suffixes=["", "LAST"])
        errcoh = errcoh.query("(MISSTART != MISSTARTLAST) & MISSTARTLAST.notnull()")

        errlist = errcoh["index"].unique().tolist()
        errlist.sort()
        return {"Missing": errlist}


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

    error_defn, error_func = validate()

    assert error_func(fake_dfs) == {"Missing": [1, 3]}
