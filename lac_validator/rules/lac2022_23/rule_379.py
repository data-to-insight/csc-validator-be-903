import pandas as pd

from lac_validator.rule_engine import rule_definition
from lac_validator.rules.rule_utils import dec_after_decom


@rule_definition(
    code="379",
    message="Temporary placements for unspecified reason (placement code T4) cannot exceed seven days.",
    affected_fields=["DECOM", "PLACE"],
    tables=["Episodes", "Header"],
)
def validate(dfs):
    if "Episodes" not in dfs or "Header" not in dfs:
        return {}
    else:
        return dec_after_decom(dfs, p_code="T4", y_gap=7)


def test_validate():
    import pandas as pd

    fake_epi = pd.DataFrame(
        {
            "CHILD": ["111", "222", "333", "444", "555", "666"],
            "DECOM": [
                "01/01/2020",
                "01/02/2020",
                "02/03/2020",
                "15/03/2010",
                "15/03/2004",
                "14/03/2014",
            ],
            "DEC": [
                "08/01/2020",
                "09/02/2020",
                "09/03/2020",
                "25/03/2010",
                "22/03/2004",
                "25/03/2014",
            ],
            "PLACE": ["T4", "T4", "T4", "T4", "T4", "P2"],
        }
    )
    fake_hea = pd.DataFrame(
        {
            "CHILD": ["111", "222", "333", "444", "555", "666"],
            "DOB": [
                "08/01/2020",
                "08/02/2020",
                "09/03/2020",
                "22/03/2010",
                "22/03/2004",
                "21/03/2014",
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

    assert validate(fake_dfs) == {"Episodes": [1, 3]}
