import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="234",
    message="A child aged under 10 can not change placement due to being admitted to custody",
    affected_fields=["REASON_PLACE_CHANGE"],
    tables=["Episodes", "Header"],
)
def validate(dfs):
    # If <DECOM> < <DOB> + 10 years then previous episode <REASON_PLACE_CHANGE> can not be 'CUSTOD'
    if "Episodes" not in dfs:
        return {}
    if "Header" not in dfs:
        return {}

    episodes = dfs["Episodes"].reset_index()
    header = dfs["Header"].reset_index()

    episodes = episodes.merge(
        header[["CHILD", "DOB", "index"]],
        on="CHILD",
        how="left",
        suffixes=("_eps", "_hdr"),
    )

    episodes["DOB_dt"] = pd.to_datetime(episodes["DOB"], dayfirst=True, errors="coerce")
    episodes["DECOM_dt"] = pd.to_datetime(
        episodes["DECOM"], dayfirst=True, errors="coerce"
    )

    under_10_at_DECOM = (episodes["DOB_dt"] + pd.DateOffset(years=10)) > episodes[
        "DECOM_dt"
    ]
    custod_place_change = episodes["REASON_PLACE_CHANGE"] == "CUSTOD"

    failure_rows = under_10_at_DECOM & custod_place_change

    eps_errors = episodes.loc[failure_rows, "index_eps"].to_list()
    hdr_errors = episodes.loc[failure_rows, "index_hdr"].to_list()
    return {"Episodes": eps_errors, "Header": hdr_errors}


def test_validate():
    import pandas as pd

    fake_header = pd.DataFrame(
        {
            "CHILD": [1, 2, 3, 4],
            "DOB": ["01/01/2000", "01/01/2000", "01/01/2000", "01/01/2000"],
        }
    )

    fake_epi = pd.DataFrame(
        {
            "CHILD": [1, 2, 3, 4],
            "DECOM": ["01/01/2009", "01/01/2009", "01/01/2010", "02/01/2010"],
            "REASON_PLACE_CHANGE": ["CUSTOD", "SILLY", "CUSTOD", "CUSTOD"],  # 0 fail
        }
    )

    fake_dfs = {"Episodes": fake_epi, "Header": fake_header}

    result = validate(fake_dfs)

    assert result == {"Episodes": [0], "Header": [0]}
