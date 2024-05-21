import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="434",
    message="Reason for new episode is that child's legal status has changed but not the placement, but this is not reflected in the episode data.",
    affected_fields=["RNE", "LS", "PLACE", "PL_POST", "URN", "PLACE_PROVIDER"],
    tables=["Episodes"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        episodes["DECOM"] = pd.to_datetime(
            episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        # create columns of previous values

        cols = ["PLACE", "PL_POST", "URN", "PLACE_PROVIDER"]

        episodes = episodes.sort_values(["CHILD", "DECOM"])

        error_mask = (
            (episodes["CHILD"] == episodes["CHILD"].shift(1))
            & (episodes["RNE"] == "L")
            & (
                (episodes["LS"] == episodes["LS"].shift(1))
                | (episodes[cols].fillna("") != episodes[cols].shift(1).fillna("")).any(
                    axis=1
                )
            )
        )
        # error locations
        error_locs = episodes.index[error_mask].to_list()
        return {"Episodes": error_locs}


def test_validate():
    import pandas as pd

    fake_eps = pd.DataFrame(
        [
            {
                "CHILD": "111",
                "DECOM": "01/01/2020",
                "RNE": "L",
                "LS": "--",
                "PL_POST": "ooo",
                "URN": "---",
            },  # 0
            {
                "CHILD": "111",
                "DECOM": "01/02/2020",
                "RNE": "P",
                "LS": "--",
                "PL_POST": "ooo",
                "URN": "---",
            },  # 1
            {
                "CHILD": "111",
                "DECOM": "01/12/2020",
                "RNE": "L",
                "LS": "--",
                "PL_POST": "ooo",
                "URN": "---",
            },
            # 2 fail: LS same as [3]
            {
                "CHILD": "111",
                "DECOM": "01/03/2020",
                "RNE": "P",
                "LS": "--",
                "PL_POST": "ooo",
                "URN": "---",
            },  # 3
            {
                "CHILD": "222",
                "DECOM": "01/01/2020",
                "RNE": "L",
                "LS": "--",
                "PL_POST": "---",
                "URN": "---",
            },  # 4
            {
                "CHILD": "222",
                "DECOM": "01/02/2020",
                "RNE": "L",
                "LS": "xx",
                "PL_POST": "---",
                "URN": "---",
            },  # 5
            {
                "CHILD": "222",
                "DECOM": "01/03/2020",
                "RNE": "L",
                "LS": "oo",
                "PL_POST": "---",
                "URN": "xxx",
            },  # 6 fail: URN
            {
                "CHILD": "222",
                "DECOM": "01/04/2020",
                "RNE": "L",
                "LS": "oo",
                "PL_POST": "xxx",
                "URN": "xxx",
            },
            # 7 fail: PL_POST
            {
                "CHILD": "333",
                "DECOM": "01/03/2020",
                "RNE": "P",
                "LS": "C1",
                "PL_POST": "---",
                "URN": pd.NA,
            },  # 8
            {
                "CHILD": "333",
                "DECOM": "01/04/2020",
                "RNE": "L",
                "LS": "C2",
                "PL_POST": "---",
                "URN": pd.NA,
            },  # 9
        ]
    )
    fake_eps["PLACE"] = "---"
    fake_eps["PLACE_PROVIDER"] = "---"
    fake_dfs = {"Episodes": fake_eps}

    result = validate(fake_dfs)
    assert result == {"Episodes": [2, 6, 7]}
