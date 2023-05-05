import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="435",
    message="Reason for new episode is that child’s placement has changed but not the legal status, "
    + "but this is not reflected in the episode data recorded.",
    affected_fields=["LS", "PLACE", "PL_POST", "URN", "PLACE_PROVIDER"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        epi = dfs["Episodes"]
        epi["DECOM"] = pd.todatetime(epi["DECOM"], format="%d/%m/%Y", errors="coerce")
        epi.sortvalues(["CHILD", "DECOM"], inplace=True)
        epi["idxorig"] = epi.index
        epi.resetindex(inplace=True)
        epi["idxordered"] = epi.index
        epi["idxprevious"] = epi.index + 1

        errco = (
            epi.merge(
                epi,
                how="inner",
                lefton="idxordered",
                righton="idxprevious",
                suffixes=["", "PRE"],
            )
            .query("RNE.isin(['P', 'T']) & CHILD == CHILDPRE")
            .query(
                "(LS != LSPRE) | ((PLACE == PLACEPRE) & (PLPOST == PLPOSTPRE) & (URN == URNPRE) & "
                + "(PLACEPROVIDER == PLACEPROVIDERPRE))"
            )
        )

        errlist = errco["idxorig"].unique().tolist()
        errlist.sort()

        return {"Episodes": errlist}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {
                "CHILD": "111",
                "DECOM": "01/06/2020",
                "RNE": "P",
                "LS": "L1",
                "PL_POST": "XX1",
                "URN": "SC112",
                "PLACE": "R1",
                "PLACE_PROVIDER": "PR1",
            },  # 0
            {
                "CHILD": "111",
                "DECOM": "03/06/2020",
                "RNE": "P",
                "LS": "L1",
                "PL_POST": "XX3",
                "URN": "SC112",
                "PLACE": "R1",
                "PLACE_PROVIDER": "PR1",
            },  # 1
            {
                "CHILD": "111",
                "DECOM": "04/06/2020",
                "RNE": "P",
                "LS": "L1",
                "PL_POST": "XX3",
                "URN": "SC112",
                "PLACE": "R1",
                "PLACE_PROVIDER": "PR1",
            },  # 2 Fail all the same
            {
                "CHILD": "111",
                "DECOM": "05/06/2020",
                "RNE": "P",
                "LS": "L1",
                "PL_POST": "XX1",
                "URN": "SC112",
                "PLACE": "R1",
                "PLACE_PROVIDER": "PR1",
            },  # 3
            {
                "CHILD": "222",
                "DECOM": "07/06/2020",
                "RNE": "P",
                "LS": "L1",
                "PL_POST": "XX1",
                "URN": "SC112",
                "PLACE": "R1",
                "PLACE_PROVIDER": "PR4",
            },  # 4
            {
                "CHILD": "222",
                "DECOM": "08/06/2020",
                "RNE": "P",
                "LS": "L1",
                "PL_POST": "XX1",
                "URN": "SC112",
                "PLACE": "R1",
                "PLACE_PROVIDER": "PR1",
            },  # 5
            {
                "CHILD": "222",
                "DECOM": "09/06/2020",
                "RNE": "P",
                "LS": "L3",
                "PL_POST": "XX1",
                "URN": "SC112",
                "PLACE": "R1",
                "PLACE_PROVIDER": "PR1",
            },  # 6 Fail dif LS
        ]
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [2, 6]}
