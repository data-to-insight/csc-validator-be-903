import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="361",
    message="Police protection legal status lasted longer than maximum 72 hours allowed "
    + "in the Children Act 1989.",
    affected_fields=["DECOM", "LS", "DEC"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        epi = dfs["Episodes"]

        epi["DECOM"] = pd.todatetime(epi["DECOM"], format="%d/%m/%Y", errors="coerce")
        epi["DEC"] = pd.todatetime(epi["DEC"], format="%d/%m/%Y", errors="coerce")
        collectionend = pd.todatetime(
            dfs["metadata"]["collectionend"], format="%d/%m/%Y", errors="coerce"
        )

        epi.sortvalues(["CHILD", "DECOM"], inplace=True)
        epi.resetindex(inplace=True)
        epi.resetindex(inplace=True)

        epi["LAG"] = epi["level0"] - 1

        epi["DEC"].fillna(collectionend, inplace=True)

        errco = epi.merge(
            epi,
            how="left",
            lefton="level0",
            righton="LAG",
            suffixes=["", "NEXT"],
        ).query("LS == 'L1'")

        # Create a partition "FLOWS" for two or more separate flow sequences of L2 code dates within the same child.
        # when the dec / decomnext dates stop flowing or the child id changes
        # the cumsum is incremented this can then be used as the partition.
        errco["FLOWS"] = (errco["DEC"] == errco["DECOMNEXT"]) & (
            errco["CHILD"] == errco["CHILDNEXT"]
        )
        errco["FLOWS"] = errco["FLOWS"].shift(1)
        errco["FLOWS"].fillna(False, inplace=True)
        errco["FLOWS"] = ~errco["FLOWS"]
        errco["FLOWS"] = errco["FLOWS"].astype(int).cumsum()

        # Calc the min decom and max dec in each group so the days between them can be calculated.
        grpdecom = (
            errco.groupby(["CHILD", "FLOWS"])["DECOM"]
            .min()
            .toframe(name="MINDECOM")
            .resetindex()
        )
        grpdec = (
            errco.groupby(["CHILD", "FLOWS"])["DEC"]
            .max()
            .toframe(name="MAXDEC")
            .resetindex()
        )
        grplenl2 = grpdecom.merge(grpdec, how="inner", on=["CHILD", "FLOWS"])

        # Throw out anything <= 3 days.
        grplenl2["DAYDIF"] = (grplenl2["MAXDEC"] - grplenl2["MINDECOM"]).dt.days
        grplenl2 = grplenl2.query("DAYDIF > 3").copy()

        # Inner join back to the errco and get the original index out.
        errco["MERGEKEY"] = errco["CHILD"].astype(str) + errco["FLOWS"].astype(str)
        grplenl2["MERGEKEY"] = grplenl2["CHILD"].astype(str) + grplenl2["FLOWS"].astype(
            str
        )
        errfinal = errco.merge(
            grplenl2, how="inner", on=["MERGEKEY"], suffixes=["", "IG"]
        )

        errlist = errfinal["index"].unique().tolist()
        errlist.sort()

        return {"Episodes": errlist}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {
                "CHILD": "111",
                "DECOM": "01/06/2020",
                "DEC": "04/06/2020",
                "LS": "L1",
            },  # 0  CHANGE |a
            {
                "CHILD": "111",
                "DECOM": "04/06/2020",
                "DEC": "05/06/2020",
                "LS": "L1",
            },  # 1         |a
            {
                "CHILD": "111",
                "DECOM": "06/07/2020",
                "DEC": "07/07/2020",
                "LS": "E2",
            },  # 2
            {
                "CHILD": "111",
                "DECOM": "08/09/2020",
                "DEC": "10/09/2020",
                "LS": "L1",
            },  # 3  CHANGE |b Passes as <=3
            {
                "CHILD": "111",
                "DECOM": "09/10/2020",
                "DEC": "12/11/2020",
                "LS": "E3",
            },  # 4
            {
                "CHILD": "333",
                "DECOM": "06/06/2020",
                "DEC": "10/06/2020",
                "LS": "L1",
            },  # 5  CHANGE |c  Fail
            {
                "CHILD": "333",
                "DECOM": "10/06/2020",
                "DEC": "12/10/2020",
                "LS": "L1",
            },  # 6         |c  Fail
            {
                "CHILD": "444",
                "DECOM": "07/06/2020",
                "DEC": "08/07/2020",
                "LS": "L1",
            },  # 7  CHANGE |d  Fail
            {
                "CHILD": "444",
                "DECOM": "08/08/2020",
                "DEC": "09/08/2020",
                "LS": "E4",
            },  # 8
            {
                "CHILD": "444",
                "DECOM": "09/08/2020",
                "DEC": "15/08/2020",
                "LS": "L1",
            },  # 9  CHANGE |e  Fail
            {
                "CHILD": "444",
                "DECOM": "15/08/2020",
                "DEC": pd.NA,
                "LS": "L1",
            },  # 10        |e  Fail
            {
                "CHILD": "555",
                "DECOM": "15/03/2021",
                "DEC": pd.NA,
                "LS": "L1",
            },  # 11 CHANGE |f  Fail
        ]
    )
    metadata = {"collection_end": "31/03/2021"}

    fake_dfs = {"Episodes": fake_data, "metadata": metadata}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [0, 1, 5, 6, 7, 9, 10, 11]}
