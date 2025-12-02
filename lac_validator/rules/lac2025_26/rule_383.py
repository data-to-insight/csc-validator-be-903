import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="383",
    message="A child in a temporary placement must subsequently return to his/her normal placement.",
    affected_fields=["PLACE", "RNE", "PL_POST"],
    tables=["Episodes"],
)
def validate(dfs):
    #  If previous episode <PL> = ‘T0’ or ‘T1’ or ‘T2’ or ‘T3’ or ‘T4’ then
    # current episode <RNE> must = ‘P’
    # AND
    # <PL> must = previous episode -1 <PL>
    # AND
    # <PL_POST> must = previous episode -1 <PL_POST>
    if "Episodes" not in dfs:
        return {}

    epi = dfs["Episodes"]

    epi["index"] = epi.index

    epi["DECOM_dt"] = pd.to_datetime(epi["DECOM"], dayfirst=True, errors="coerce")

    epi.sort_values(["CHILD", "DECOM_dt"], inplace=True)

    epi["prev_index"] = epi["index"].shift(-1)
    epi["prev-1_index"] = epi["index"].shift(-2)

    epi_1_prev = epi.merge(
        epi, left_on="index", right_on="prev_index", suffixes=("", "_prev")
    )
    epi_2_prev = epi_1_prev.merge(
        epi, left_on="index", right_on="prev-1_index", suffixes=("", "_prev-1")
    )

    same_child = (epi_2_prev["CHILD"] == epi_2_prev["CHILD_prev"]) & (
        epi_2_prev["CHILD"] == epi_2_prev["CHILD_prev-1"]
    )
    prev_pl = epi_2_prev["PLACE_prev"].isin(["T0", "T1", "T2", "T3", "T4"])
    rne = epi_2_prev["RNE"] != "P"
    pl_not_equal = epi_2_prev["PLACE"] != epi_2_prev["PLACE_prev-1"]
    post_not_equal = epi_2_prev["PL_POST"] != epi_2_prev["PL_POST_prev-1"]

    error_rows = epi_2_prev[
        (same_child & prev_pl) & (rne | pl_not_equal | post_not_equal)
    ]["index"]

    return {"Episodes": error_rows.to_list()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {
                "CHILD": "111",
                "RNE": "S",
                "DECOM": "01/06/2020",
                "PLACE": "S1",
                "PL_POST": 1,
            },  # 0
            {
                "CHILD": "111",
                "RNE": "S",
                "DECOM": "05/06/2020",
                "PLACE": "T1",
                "PL_POST": 1,
            },  # 1
            {
                "CHILD": "111",
                "RNE": "T",
                "DECOM": "06/06/2020",
                "PLACE": "S1",
                "PL_POST": 1,
            },  # 2
            {
                "CHILD": "222",
                "RNE": "S",
                "DECOM": "05/06/2020",
                "PLACE": "T1",
                "PL_POST": 1,
            },  # 3
            {
                "CHILD": "333",
                "RNE": "S",
                "DECOM": "06/06/2020",
                "PLACE": "S1",
                "PL_POST": 1,
            },  # 4
            {
                "CHILD": "333",
                "RNE": "S",
                "DECOM": "10/06/2020",
                "PLACE": "T1",
                "PL_POST": 1,
            },  # 5
            {
                "CHILD": "333",
                "RNE": "P",
                "DECOM": "12/06/2020",
                "PLACE": "S2",
                "PL_POST": 1,
            },  # 6
            {
                "CHILD": "444",
                "RNE": "S",
                "DECOM": "08/06/2020",
                "PLACE": "T1",
                "PL_POST": 1,
            },  # 7
            {
                "CHILD": "444",
                "RNE": "S",
                "DECOM": "09/06/2020",
                "PLACE": "P4",
                "PL_POST": 1,
            },  # 8
            {
                "CHILD": "444",
                "RNE": "S",
                "DECOM": "15/06/2020",
                "PLACE": "T1",
                "PL_POST": 1,
            },  # 9
            {
                "CHILD": "6666",
                "RNE": "S",
                "DECOM": "12/06/2020",
                "PLACE": "T1",
                "PL_POST": 1,
            },  # 10
            {
                "CHILD": "6666",
                "RNE": "S",
                "DECOM": "13/06/2020",
                "PLACE": "T1",
                "PL_POST": 1,
            },  # 11
            {
                "CHILD": "6666",
                "RNE": "P",
                "DECOM": "14/06/2020",
                "PLACE": "T1",
                "PL_POST": 1,
            },  # 12
            {
                "CHILD": "777",
                "RNE": "P",
                "DECOM": "01/06/2020",
                "PLACE": "S1",
                "PL_POST": 1,
            },  # 13
            {
                "CHILD": "777",
                "RNE": "S",
                "DECOM": "05/06/2020",
                "PLACE": "T1",
                "PL_POST": 2,
            },  # 14
            {
                "CHILD": "777",
                "RNE": "P",
                "DECOM": "06/06/2020",
                "PLACE": "S1",
                "PL_POST": 3,
            },  # 15
        ]
    )

    fake_dfs = {"Episodes": fake_data}

    result = validate(fake_dfs)

    assert result == {"Episodes": [2, 6, 15]}
