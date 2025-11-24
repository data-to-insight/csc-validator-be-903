import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="706",
    message="There is an open DoLO in last year’s return and there is no corresponding DoLO recorded at the start of this year..",
    affected_fields=["DOLO_START"],
    tables=["DoLo", "DOLO_last"],
)
def validate(dfs):
    if "DoLo" not in dfs:
        return {}

    # If previous collection year last DoLO has <DOLO_START> and <DOLO_END> is null,
    # then a DoLO must be present in this years collection and the first DoLO <DOLO_START>
    # must be the same as that episode’s <DOLO_START>

    dolo_this = dfs["DoLo"].reset_index()
    dolo_last = dfs["DoLo_last"].reset_index()

    dolo_last_no_end = dolo_last[dolo_last["DOLO_END"].isna()]

    # Get last years DOLOs with no end end match them to DOLO starts from this year, if the merge has an empty RHS
    # then there's no match from this year.
    m_dolo = dolo_last_no_end.merge(
        dolo_this, on=["CHILD", "DOLO_START"], how="left", suffixes=("_last", "_this")
    )

    # Find rows from this year with no match to last year
    no_matching_start = m_dolo[m_dolo["index_this"].isna()]

    # We need to return rows from last year with no matching start this year, we can't return rows from this year that
    # don't match last years as they don't exist!
    error_rows = no_matching_start["index_last"]

    return {"DoLo": error_rows.to_list()}


def test_validate():
    import pandas as pd

    fake_data_this = pd.DataFrame(
        {
            "CHILD": [1, 1, 1, 2, 2, 3],
            "DOLO_START": [
                "01/01/2000",
                "04/01/2000",
                "06/01/2000",
                "01/01/2000",
                "02/01/2000",
                "01/01/2000",
            ],
        }
    )

    fake_data_last = pd.DataFrame(
        {
            "CHILD": [1, 1, 1, 2, 2, 3],
            "DOLO_START": [
                "01/01/1999",
                "04/01/1999",
                "03/01/1999",
                "01/01/2000",
                "02/01/2000",
                "01/01/2000",
            ],
            "DOLO_END": [
                "02/01/1999",
                "05/01/1999",
                pd.NA,
                "01/02/1999",
                "03/01/1999",
                "02/01/2000",
            ],
        }
    )

    fake_dfs = {"DoLo": fake_data_this, "DoLo_last": fake_data_last}

    result = validate(fake_dfs)

    assert result == {"DoLo": [2]}
