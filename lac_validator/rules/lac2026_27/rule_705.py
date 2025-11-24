import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="705",
    message="A DoLO cannot start when the previous DoLO is still open.",
    affected_fields=["DOLO_START", "DOLO_END"],
    tables=["DoLo"],
)
def validate(dfs):
    # If provided <DOLO_START> from current 
    # DoLO occurrence must be >= previous DoLO occurrence <DOLO_START> 
    # and previous DoLO occurrence <DOLO_END> cannot be Null

    if "DoLo" not in dfs:
        return {}

    dolo = dfs["DoLo"]
    dolo.reset_index(inplace=True) 
    dolo = dolo[dolo['DOLO_START'].notna()]

    dolo['DOLO_START_dt'] = pd.to_datetime(
        dolo['DOLO_START'], format="%d/%m/%Y", errors="coerce"
        )

    dolo["DOLO_END_dt"] = pd.to_datetime(
        dolo["DOLO_END"], format="%d/%m/%Y", errors="coerce"
    )

    # sorting by DOLO_END
    dolo.sort_values(['CHILD', 'DOLO_END'], ascending=False, inplace=True) 
    dolo['LEAD_INDEX'] = dolo['index'].shift(1)  

    m_dolo = dolo.merge(dolo[['CHILD', 'LEAD_INDEX', 'DOLO_START', "DOLO_END"]], how='inner', left_on='index', right_on="LEAD_INDEX", suffixes=("", "_prev"))

    same_child = m_dolo['CHILD'] == m_dolo['CHILD_prev']
    empty_end_prev = m_dolo['DOLO_END_prev'].isna()
    dolo_overlap = m_dolo['DOLO_START'] < m_dolo['DOLO_START_prev']

    error_rows = m_dolo[same_child & (empty_end_prev | dolo_overlap)].sort_values('index')

    return {"DoLo": error_rows['index'].to_list()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "CHILD": [1,1,1,2,2,3

            ],
            "DOLO_START": ["01/01/2000","04/01/2000","03/01/2000","01/01/2000","02/01/2000","01/01/2000"

            ],
            "DOLO_END": ["02/01/2000","04/01/2000","06/01/2000", pd.NA,"02/01/2000","02/01/2000"
            ],
        }
    )


    fake_dfs = {"DoLo": fake_data}

    result = validate(fake_dfs)

    assert result == {"DoLo": [2, 4]}
