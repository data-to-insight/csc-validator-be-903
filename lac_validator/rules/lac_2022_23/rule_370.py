import pandas as pd
from lac_validator.rule_engine import rule_definition
#from lac_validator.rules.rule_utils import decom_less_dob


@rule_definition(
    code="370",
    message="Child in independent living should be at least 15.",
    affected_fields=['DECOM', 'PLACE'],
)
def validate(dfs):
    if 'Episodes' not in dfs or 'Header' not in dfs:
        return {}
    else:
        decom
        epi = dfs['Episodes']
        hea = dfs['Header']

        epi.reset_index(inplace=True)
        epi_p2 = epi[epi['PLACE'] == 'P2']
        merged_e = epi_p2.merge(hea, how='inner', on='CHILD').dropna(subset=['DECOM', 'DEC', 'DOB'])
        error_mask = merged_e['DECOM'] < (merged_e['DOB'] +
                                                pd.offsets.DateOffset(years=15))
        return {'Episodes': merged_e['index'][error_mask].unique().tolist()}

def test_validate():
    import pandas as pd

    fake_epi = pd.DataFrame(
        {
            "CHILD": ["111", "222", "333", "444", "555", "666"],
            "DECOM": [
                "01/01/2020",
                "01/02/2020",
                "02/03/2020",
                "15/01/1980",
                "15/03/2015",
                "14/03/2015",
            ],
            "PLACE": ["E1", "P2", "P2", "P2", "P2", "P2"],  # 15bd    #day before 15bd
            "DEC": [
                "13/02/2020",
                "14/03/2020",
                "14/04/2020",
                "27/04/2010",
                "26/04/2004",
                "25/04/2014",
            ],
        }
    )
    fake_hea = pd.DataFrame(
        {
            "CHILD": ["111", "222", "333", "444", "555", "666"],
            "DOB": [
                "01/01/1998",
                "01/02/2000",
                "02/03/2015",
                "15/01/2010",
                "15/03/2000",
                "15/03/2000",
            ],
        }
    )    
    fake_hea['DOB'] = pd.to_datetime(fake_hea['DOB'], format='%d/%m/%Y', errors='coerce')
    fake_epi['DECOM'] = pd.to_datetime(fake_epi['DECOM'], format='%d/%m/%Y', errors='coerce')
    fake_epi['DEC'] = pd.to_datetime(fake_epi['DEC'], format='%d/%m/%Y', errors='coerce')

    fake_dfs = {"Episodes": fake_epi, "Header": fake_hea}    

    assert validate(fake_dfs) == {"Episodes": [2, 3, 5]}
