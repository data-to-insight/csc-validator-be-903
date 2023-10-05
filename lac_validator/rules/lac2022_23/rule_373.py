import pandas as pd

from lac_validator.rule_engine import rule_definition
from lac_validator.rules.rule_utils import decom_before_dob


@rule_definition(
    code="373",
    message="Child placed in a school should be at least 4 years old.",
    affected_fields=["DECOM", "PLACE"],
)
def validate(dfs):
    if "Episodes" not in dfs or "Header" not in dfs:
        return {}
    else:
        return decom_before_dob(dfs, p_code="S1", y_gap=4)


def test_validate():
    fake_epi = pd.DataFrame(
        {
            "CHILD": ["111", "222", "333", "444", "555", "666"],
            "DECOM": [
                "01/01/2020",
                "01/02/2020",
                "02/03/2020",
                "15/03/2010",
                "15/03/2004",
                "14/03/2004",
            ],
            "PLACE": ["S1", "S1", "P2", "S1", "S1", "S1"],  # day before 4bd
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

    fake_hea["DOB"] = pd.to_datetime(
        fake_hea["DOB"], format="%d/%m/%Y", errors="coerce"
    )
    fake_epi["DECOM"] = pd.to_datetime(
        fake_epi["DECOM"], format="%d/%m/%Y", errors="coerce"
    )
    fake_epi["DEC"] = pd.to_datetime(
        fake_epi["DEC"], format="%d/%m/%Y", errors="coerce"
    )

    fake_dfs = {"Episodes": fake_epi, "Header": fake_hea}

    assert validate(fake_dfs) == {"Episodes": [3, 5]}
