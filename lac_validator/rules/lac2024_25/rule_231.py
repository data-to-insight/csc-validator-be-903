import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="231",
    message="We expect that unaccompanied asylum seeking children are generally older young people. Please check the date of birth is correct. If the date of birth is correct then please provide details in a bypass request.",
    affected_fields=["DOB", "UASC_STATUS"],
    tables=["Header"],
)
def validate(dfs):
    # If <UASC_STATUS> = 1 then <DOB> should be > 11 years prior to <COLLECTION_END_DATE>
    if "Header" not in dfs:
        return {}
    else:
        df = dfs["Header"]

        collection_end = pd.to_datetime(
            dfs["metadata"]["collection_end"], format="%d/%m/%Y", errors="coerce"
        )

        df['DOB'] = pd.to_datetime(df["DOB"], format="%d/%m/%Y", errors="coerce")
        
        under_11_uasc = df[((df["DOB"] > collection_end - pd.DateOffset(years=11)  )) & (df['UASC_STATUS'].astype(str) == "1")].index
        
        return {"Header": under_11_uasc.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame([{"DOB": "01/04/2014", "UASC_STATUS": "1"}, # under 11 uasc, fails  
                            {"DOB": "31/03/2014", "UASC_STATUS": "1"}, # 11 day of collection end, uasc, according to stric rule logic, passes
                            {"DOB": "01/04/2014", "UASC_STATUS": "0"},
                            {"DOB": "30/03/2014", "UASC_STATUS": "1"}]) # over 11, uasc, passes
    

    fake_metadata = {"collection_end":"31/03/2025"}

    fake_dfs = {"Header":fake_data,
                "metadata":fake_metadata}

    result = validate(fake_dfs)

    assert result == {"Header": [0]}
