from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="624",
    message="Date of birth of the first child contradicts the date of birth of the first child previously "
    + "recorded.",
    affected_fields=["MC_DOB"],
)
def validate(dfs):
    if "Header" not in dfs or "Header_last" not in dfs:
        return {}
    else:
        hea = dfs["Header"]
        hea_pre = dfs["Header_last"]
        hea["orig_idx"] = hea.index

        err_co = hea.merge(
            hea_pre, how="inner", on="CHILD", suffixes=["", "_PRE"]
        ).query("MC_DOB_PRE.notna() & (MC_DOB != MC_DOB_PRE)")

        err_list = err_co["orig_idx"].unique().tolist()
        err_list.sort()
        return {"Header": err_list}


def test_validate():
    import pandas as pd

    hdr = pd.DataFrame(
        [
            {"CHILD": "111", "MC_DOB": "01/06/2020"},  # 0
            {"CHILD": "222", "MC_DOB": "04/06/2020"},  # 1
            {"CHILD": "333", "MC_DOB": pd.NA},  # 2
            {"CHILD": "444", "MC_DOB": "08/09/2020"},  # 3
            {"CHILD": "555", "MC_DOB": pd.NA},  # 4
            {"CHILD": "66", "MC_DOB": "01/02/2020"},  # 5
        ]
    )
    hdr_last = pd.DataFrame(
        [
            {"CHILD": "111", "MC_DOB": "01/06/2020"},  # 0
            {"CHILD": "222", "MC_DOB": "04/06/2020"},  # 1
            {"CHILD": "333", "MC_DOB": "01/06/2019"},  # 2
            {"CHILD": "444", "MC_DOB": "10/09/2020"},  # 3
            {"CHILD": "555", "MC_DOB": pd.NA},  # 4
            {"CHILD": "66", "MC_DOB": pd.NA},  # 5
        ]
    )
    fake_dfs = {"Header": hdr, "Header_last": hdr_last}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Header": [2, 3]}
