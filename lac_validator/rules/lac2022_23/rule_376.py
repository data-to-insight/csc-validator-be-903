import pandas as pd

from lac_validator.rule_engine import rule_definition
from lac_validator.rules.rule_utils import dec_after_decom


@rule_definition(
    code="376",
    message="Temporary placements coded as being due to holiday of usual foster carer(s) cannot exceed three weeks.",
    affected_fields=["DECOM", "PLACE"],
)
def validate(dfs):
    if "Episodes" not in dfs or "Header" not in dfs:
        return {}
    else:
        return dec_after_decom(dfs, p_code="T3", y_gap=21)


def test_validate():
    fake_epi = pd.DataFrame(
        {
            "CHILD": ["111", "222", "333", "444", "555", "666", "777"],
            "DECOM": [
                "01/01/2020",
                "01/02/2020",
                "02/03/2020",
                "15/03/2010",
                "15/03/2004",
                "14/03/2014",
                pd.NA,
            ],
            "DEC": [
                "22/01/2020",
                "23/02/2020",
                "24/03/2020",
                "06/04/2010",
                "05/04/2004",
                "04/04/2014",
                pd.NA,
            ],
            "PLACE": ["T3", "T3", "T3", "T3", "T3", "P2", "T3"],
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

    assert validate(fake_dfs) == {"Episodes": [1, 2, 3]}
