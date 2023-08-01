import pandas as pd

from lac_validator.rule_engine import rule_definition


import pandas as pd


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
        epi["DECOM"] = pd.to_datetime(epi["DECOM"], format="%d/%m/%Y", errors="coerce")
        epi.sort_values(["CHILD", "DECOM"], inplace=True)
        epi["idx_orig"] = epi.index
        epi.reset_index(inplace=True)
        epi["idx_ordered"] = epi.index
        epi["idx_previous"] = epi.index + 1

        err_co = (
            epi.merge(
                epi,
                how="inner",
                left_on="idx_ordered",
                right_on="idx_previous",
                suffixes=["", "_PRE"],
            )
            .query("RNE.isin(['P', 'T']) & CHILD == CHILD_PRE")
            .query(
                "(LS != LS_PRE) | ((PLACE == PLACE_PRE) & (PL_POST == PL_POST_PRE) & (URN == URN_PRE) & "
                + "(PLACE_PROVIDER == PLACE_PROVIDER_PRE))"
            )
        )

        err_list = err_co["idx_orig"].unique().tolist()
        err_list.sort()

        return {"Episodes": err_list}


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

    

    result = validate(fake_dfs)

    assert result == {"Episodes": [2, 6]}
