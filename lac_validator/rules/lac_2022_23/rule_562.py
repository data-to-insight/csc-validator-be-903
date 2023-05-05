import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="562",
    message="Episode commenced before the start of the current collection year but there is a missing continuous episode in the previous year.",
    affected_fields=["DECOM"],
)
def validate(dfs):
    if "Episodes" not in dfs or "Episodeslast" not in dfs:
        return {}
    else:
        epi = dfs["Episodes"]
        epilast = dfs["Episodeslast"]
        epi["DECOM"] = pd.todatetime(epi["DECOM"], format="%d/%m/%Y", errors="coerce")
        epilast["DECOM"] = pd.todatetime(
            epilast["DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        collectionstart = pd.todatetime(
            dfs["metadata"]["collectionstart"], format="%d/%m/%Y", errors="coerce"
        )

        epi.resetindex(inplace=True)
        epi = epi[epi["DECOM"] < collectionstart]

        grpdecombychild = epi.groupby(["CHILD"])["DECOM"].idxmin(skipna=True)
        mindecom = epi.loc[epi.index.isin(grpdecombychild), :]

        grplastdecombychild = epilast.groupby(["CHILD"])["DECOM"].idxmax(skipna=True)
        maxlastdecom = epilast.loc[epilast.index.isin(grplastdecombychild), :]

        mergedco = mindecom.merge(
            maxlastdecom,
            how="left",
            on=["CHILD", "DECOM"],
            suffixes=["", "PRE"],
            indicator=True,
        )
        errorcohort = mergedco[mergedco["merge"] == "leftonly"]

        errorlist = errorcohort["index"].tolist()
        errorlist = list(set(errorlist))
        errorlist.sort()
        return {"Episodes": errorlist}


def test_validate():
    import pandas as pd

    fake_epi = pd.DataFrame(
        [
            {"CHILD": "111", "DECOM": "15/03/2021"},  # 0 Min pre year start
            {"CHILD": "111", "DECOM": "05/06/2021"},  # 1
            {"CHILD": "222", "DECOM": "13/03/2021"},  # 2 Min pre year start
            {"CHILD": "222", "DECOM": "08/06/2021"},  # 3
            {"CHILD": "222", "DECOM": "05/06/2021"},  # 4
            {"CHILD": "333", "DECOM": "01/01/2021"},  # 5 Min pre year start
            {"CHILD": "444", "DECOM": "01/05/2021"},  # 6
        ]
    )
    fake_last = pd.DataFrame(
        [
            {"CHILD": "111", "DECOM": "01/06/2020"},  # 0
            {"CHILD": "111", "DECOM": "05/06/2020"},  # 1
            {"CHILD": "111", "DECOM": "15/03/2021"},  # 2 Max matches next year
            {"CHILD": "222", "DECOM": "01/02/2021"},  # 3
            {"CHILD": "222", "DECOM": "11/03/2021"},  # 4 Max doesn't match - fail
            {"CHILD": "333", "DECOM": "06/06/2020"},  # 5 Max doesn't match - fail
        ]
    )
    metadata = {"collection_start": "01/04/2021"}

    fake_dfs = {"Episodes": fake_epi, "Episodes_last": fake_last, "metadata": metadata}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [2, 5]}
