import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="633",
    message="Local authority code where previous permanence option was arranged is not a valid value.",
    affected_fields=["LA_PERM"],
    tables=["PrevPerm"],
)
def validate(dfs):
    if "PrevPerm" not in dfs:
        return {}
    else:
        prevperm = dfs["PrevPerm"]
        la_codes = (
            "800,889,822,301,304,303,330,825,837,302,846,370,350,890,867,380,305,801,351,873,823,895,896,"
            "381,909,202,908,331,306,841,830,831,878,371,835,332,840,307,308,811,881,845,390,916,203,876,"
            "850,311,204,884,312,205,313,805,919,310,309,420,921,206,207,886,810,382,314,340,888,208,856,"
            "383,855,209,925,341,201,821,352,806,887,826,315,929,812,391,926,892,813,802,928,891,392,316,"
            "815,353,931,879,836,851,874,807,354,317,870,318,372,857,333,935,343,803,373,342,893,356,355,"
            "871,394,334,933,882,936,861,852,319,860,808,393,866,210,357,894,883,880,358,211,937,869,320,"
            "359,865,384,335,336,212,868,872,885,344,877,213,938,816,999"
        )
        out_of_uk_codes = ["WAL", "SCO", "NUK", "NIR"]
        valid_values = la_codes.split(",") + out_of_uk_codes

        # Where provided <LA_PERM> must be a valid value
        mask = prevperm["LA_PERM"].notna() & (
            ~prevperm["LA_PERM"].astype("str").isin(valid_values)
        )

        # error locations
        error_locs = prevperm.index[mask]
        return {"PrevPerm": error_locs.tolist()}


def test_validate():
    import pandas as pd

    fake_data_prevperm = pd.DataFrame(
        {
            "CHILD": ["101", "102", "103", "6", "7", "8"],
            "LA_PERM": [pd.NA, "SCO", "204", "458", "176", 212],
        }
    )
    fake_dfs = {"PrevPerm": fake_data_prevperm}

    result = validate(fake_dfs)
    assert result == {"PrevPerm": [3, 4]}
