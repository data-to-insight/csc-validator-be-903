import pandas as pd
from lac_validator.rule_engine import rule_definition
from lac_validator.rules.rule_utils import decom_before_dob


@rule_definition(
    code="374",
    message="Child in residential employment should be at least 14 years old.",
    affected_fields=['DECOM', 'PLACE'],
)
def validate(dfs):
    if 'Episodes' not in dfs or 'Header' not in dfs:
        return {}
    else:
        return decom_before_dob(dfs, p_code='P3', y_gap=14)


def test_validate():
    import pandas as pd

    fake_epi = pd.DataFrame(
        {
            "CHILD": ["111", "222", "333", "444", "555", "666", "777"],
            "DECOM": [
                "01/01/2020",
                "01/02/2020",
                "02/03/2020",
                "15/03/2010",
                pd.NA,
                "15/03/2004",
                "14/03/2014",
            ],
            "PLACE": ["P3", "P3", "P3", "P3", "P3", "P3", "P3"],  # day before 14bd
            "DEC": [
                "13/02/2020",
                "14/03/2020",
                "14/04/2020",
                pd.NA,
                "27/04/2010",
                "26/04/2004",
                "25/04/2014",
            ],
        }
    )
    fake_hea = pd.DataFrame(
        {
            "CHILD": ["111", "222", "333", "444", "555", "666", "777"],
            "DOB": [
                "01/01/1998",
                "01/02/2000",
                "02/03/2015",
                "15/01/2010",
                "15/03/2000",
                "15/03/2000",
                "15/03/2000",
            ],
        }
    )

    fake_hea['DOB'] = pd.to_datetime(fake_hea['DOB'], format='%d/%m/%Y', errors='coerce')
    fake_epi['DECOM'] = pd.to_datetime(fake_epi['DECOM'], format='%d/%m/%Y', errors='coerce')
    fake_epi['DEC'] = pd.to_datetime(fake_epi['DEC'], format='%d/%m/%Y', errors='coerce')

    fake_dfs = {"Episodes": fake_epi, "Header": fake_hea}    

    assert validate(fake_dfs) == {"Episodes": [2, 5, 6]}
