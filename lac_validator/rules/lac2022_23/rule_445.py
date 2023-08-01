import pandas as pd

from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="445",
    message="D1 is not a valid code for episodes starting after December 2005.",
    affected_fields=["LS", "DECOM"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        episodes["DECOM"] = pd.to_datetime(
            episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        max_decom_allowed = pd.to_datetime(
            "31/12/2005", format="%d/%m/%Y", errors="coerce"
        )

        mask = episodes["LS"].eq("D1") & (episodes["DECOM"] > max_decom_allowed)
        validation_error_mask = mask
        validation_error_locations = episodes.index[validation_error_mask]

        return {"Episodes": validation_error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "LS": ["D1", "D1", "D1", "D1", "D1", "C1"],
            "DECOM": [
                "01/11/2005",
                "31/12/2005",
                pd.NA,
                "20/01/2006",
                "01/10/2012",
                "20/02/2005",
            ],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    

    result = validate(fake_dfs)

    assert result == {"Episodes": [3, 4]}
