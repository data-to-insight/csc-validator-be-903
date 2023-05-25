import pandas as pd

from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="431",
    message="The reason for new episode is started to be looked after, but the previous episode ended on the same day.",
    affected_fields=["RNE", "DECOM"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        epi = dfs["Episodes"]
        epi["DECOM"] = pd.to_datetime(epi["DECOM"], format="%d/%m/%Y", errors="coerce")
        epi["DEC"] = pd.to_datetime(epi["DEC"], format="%d/%m/%Y", errors="coerce")
        epi.sort_values(["CHILD", "DECOM"], inplace=True)

        epi.reset_index(inplace=True)
        epi.reset_index(inplace=True)
        epi["LAG_INDEX"] = epi["level_0"].shift(-1)

        m_epi = epi.merge(
            epi,
            how="inner",
            left_on="level_0",
            right_on="LAG_INDEX",
            suffixes=["", "_PREV"],
        )

        m_epi = m_epi[(m_epi["CHILD"] == m_epi["CHILD_PREV"]) & (m_epi["RNE"] == "S")]
        error_mask = m_epi["DECOM"] <= m_epi["DEC_PREV"]
        error_list = m_epi["index"][error_mask].to_list()
        error_list.sort()
        return {"Episodes": error_list}


def validate_503_Generic(subval):
    Gen_503_dict = {
        "A": {
            "Desc": "The reason for new episode in the first episode does not match open episode at end of last year.",
            "Fields": "RNE",
        },
        "B": {
            "Desc": "The legal status in the first episode does not match open episode at end of last year.",
            "Fields": "LS",
        },
        "C": {
            "Desc": "The category of need in the first episode does not match open episode at end of last year.",
            "Fields": "CIN",
        },
        "D": {
            "Desc": "The placement type in the first episode does not match open episode at end of last year",
            "Fields": "PLACE",
        },
        "E": {
            "Desc": "The placement provider in the first episode does not match open episode at end of last year.",
            "Fields": "PLACE_PROVIDER",
        },
        "F": {
            "Desc": "The Ofsted URN in the  first episode does not match open episode at end of last year.",
            "Fields": "URN",
        },
        "G": {
            "Desc": "The distance in first episode does not match open episode at end of last year.",
            "Fields": "PL_DISTANCE",
        },
        "H": {
            "Desc": "The placement LA in first episode does not match open episode at end of last year.",
            "Fields": "PL_LA",
        },
        "J": {
            "Desc": "The placement location in first episode does not match open episode at end of last year.",
            "Fields": "PL_LOCATION",
        },
    }
    error = ErrorDefinition(
        code="503" + subval,
        description=Gen_503_dict[subval]["Desc"],
        affected_fields=[Gen_503_dict[subval]["Fields"]],
    )

    def validate(dfs):
        if "Episodes" not in dfs or "Episodes_last" not in dfs:
            return {}
        else:
            epi = dfs["Episodes"]
            epi_last = dfs["Episodes_last"]
            epi["DECOM"] = pd.to_datetime(
                epi["DECOM"], format="%d/%m/%Y", errors="coerce"
            )
            epi_last["DECOM"] = pd.to_datetime(
                epi_last["DECOM"], format="%d/%m/%Y", errors="coerce"
            )
            epi_last["DEC"] = pd.to_datetime(
                epi_last["DEC"], format="%d/%m/%Y", errors="coerce"
            )

            epi.reset_index(inplace=True)

            first_ep_inds = epi.groupby(["CHILD"])["DECOM"].idxmin(skipna=True)
            min_decom = epi.loc[first_ep_inds, :]

            last_ep_inds = epi_last.groupby(["CHILD"])["DECOM"].idxmax(skipna=True)
            max_last_decom = epi_last.loc[last_ep_inds, :]

            merged_co = min_decom.merge(
                max_last_decom, how="inner", on=["CHILD"], suffixes=["", "_PRE"]
            )

            this_one = Gen_503_dict[subval]["Fields"]
            pre_one = this_one + "_PRE"

            if subval == "G":
                err_mask = (
                    abs(
                        merged_co[this_one].astype(float)
                        - merged_co[pre_one].astype(float)
                    )
                    >= 0.2
                )
            else:
                err_mask = merged_co[this_one].astype(str) != merged_co[pre_one].astype(
                    str
                )
            err_mask = err_mask & merged_co["DEC_PRE"].isna()

            err_list = merged_co["index"][err_mask].unique().tolist()
            err_list.sort()
            return {"Episodes": err_list}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {
                "CHILD": "111",
                "RNE": "S",
                "DECOM": "01/06/2020",
                "DEC": "04/06/2020",
            },  # 0
            {
                "CHILD": "111",
                "RNE": "S",
                "DECOM": "05/06/2020",
                "DEC": "06/06/2020",
            },  # 1
            {
                "CHILD": "111",
                "RNE": "T",
                "DECOM": "06/06/2020",
                "DEC": "08/06/2020",
            },  # 2
            {
                "CHILD": "111",
                "RNE": "S",
                "DECOM": "08/06/2020",
                "DEC": "05/06/2020",
            },  # 3  Fails
            {
                "CHILD": "222",
                "RNE": "S",
                "DECOM": "05/06/2020",
                "DEC": "06/06/2020",
            },  # 4
            {
                "CHILD": "333",
                "RNE": "S",
                "DECOM": "06/06/2020",
                "DEC": "07/06/2020",
            },  # 5
            {"CHILD": "333", "RNE": "S", "DECOM": "10/06/2020", "DEC": pd.NA},  # 6
            {
                "CHILD": "444",
                "RNE": "S",
                "DECOM": "08/06/2020",
                "DEC": "09/06/2020",
            },  # 7
            {
                "CHILD": "444",
                "RNE": "S",
                "DECOM": "09/06/2020",
                "DEC": "10/06/2020",
            },  # 8  Fails
            {"CHILD": "444", "RNE": "S", "DECOM": "15/06/2020", "DEC": pd.NA},  # 9
            {
                "CHILD": "555",
                "RNE": "S",
                "DECOM": "11/06/2020",
                "DEC": "12/06/2020",
            },  # 10
            {
                "CHILD": "6666",
                "RNE": "S",
                "DECOM": "12/06/2020",
                "DEC": "13/06/2020",
            },  # 11
            {
                "CHILD": "6666",
                "RNE": "S",
                "DECOM": "13/06/2020",
                "DEC": "14/06/2020",
            },  # 12 Fails
            {
                "CHILD": "6666",
                "RNE": "S",
                "DECOM": "14/06/2020",
                "DEC": "15/06/2020",
            },  # 13 Fails
        ]
    )

    fake_dfs = {"Episodes": fake_data}

    

    result = validate(fake_dfs)

    assert result == {"Episodes": [3, 8, 12, 13]}
