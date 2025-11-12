import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="348",
    message="Care leaver has previously been reported as having died. ",
    affected_fields=["IN_TOUCH"],
    tables=["OC3"],
)
def validate(dfs):
    if "OC3" not in dfs or "OC3_last" not in dfs:
        return {}

    oc3_this = dfs["OC3"].reset_index()
    oc3_last = dfs["OC3_last"]

    all_oc3 = oc3_this.merge(
        oc3_last[["IN_TOUCH", "CHILD"]],
        on="CHILD",
        how="left",
        suffixes=["_this", "_last"],
    )

    mask = (all_oc3["IN_TOUCH_last"] == "DIED") & (all_oc3["IN_TOUCH_this"] != "DIED")

    failure_rows = all_oc3[mask]["index"].to_list()

    return {"OC3": failure_rows}


def test_validate():
    import pandas as pd

    fake_this = pd.DataFrame(
        {
            "CHILD": [1, 2, 3, 4],
            "IN_TOUCH": [
                "DIED",
                "DIED",
                "MORT",
                "SHUFFLED",
            ],
        }
    )

    fake_last = pd.DataFrame(
        {
            "CHILD": [1, 2, 3, 4],
            "IN_TOUCH": ["DIED", "PASSED", "DIED", "SHUFFLED"],  # FAIL
        }
    )

    fake_dfs = {"OC3": fake_this, "OC3_last": fake_last}

    result = validate(fake_dfs)

    assert result == {"OC3": [2]}
