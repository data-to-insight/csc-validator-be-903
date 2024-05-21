import pandas as pd

from lac_validator.datastore import merge_postcodes
from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="392d",
    message="Home and placement postcodes should not be same unless the placement type is P1.",
    affected_fields=["HOME_POST", "PL_POST", "PLACE"],
    tables=["Episodes"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]

        not_p1 = episodes[(episodes["PLACE"] != "P1")]

        same_postcode = not_p1[not_p1["HOME_POST"] == not_p1["PL_POST"]]

        error_mask = episodes.index.isin(same_postcode.index)

        return {"Episodes": episodes.index[error_mask].tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "PLACE": [
                "P2",
                "P1",
                "P2",
            ],
            "PL_POST": [
                "BN20",
                "BN20",
                "BN21",
            ],
            "HOME_POST": [
                "BN20",
                "BN20",
                "BN20",
            ],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    result = validate(fake_dfs)

    assert result == {
        "Episodes": [
            0,
        ]
    }
