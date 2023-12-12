import pandas as pd

from lac_validator.rule_engine import rule_definition
from lac_validator.rules.rule_utils import decom_before_dob


@rule_definition(
    code="371",
    message="Child in supported accomodation not subject to children’s homes regulations should be at least 16.",
    affected_fields=["DECOM", "PLACE"],
)
def validate(dfs):
    if "Episodes" not in dfs or "Header" not in dfs:
        return {}
    else:
        return decom_before_dob(dfs, p_code="K3", y_gap=16)


def test_validate():
    fake_epi = pd.DataFrame(
        {
            "CHILD": ["111", "222", "333", "444", "555", "666"],
            "DECOM": [
                "01/01/2022",
                "01/02/2022",
                "02/03/2022",
                "15/01/1982",
                "15/03/2016",
                "14/03/2016",
            ],
            "PLACE": ["K3", "P2", "P2", "K3", "K3", "K3"],  # 14bd    #day before 14bd
            "DEC": [
                "13/02/2022",
                "14/03/2022",
                "14/04/2022",
                "27/04/2012",
                "26/04/2006",
                "25/04/2012",
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
