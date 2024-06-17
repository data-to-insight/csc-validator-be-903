import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="579",
    message="A new decision that the child should be placed for adoption this year cannot start when the previous decision is still open. Decisions to place the child for adoption should also not overlap. The date of any new decision to place the child for adoption must not be before the date placed ceased of previous decisions.",
    affected_fields=["DATE_PLACED", "DATE_PLACED_CEASED"],
    tables=["PlacedAdoption"],
)
def validate(dfs):
    if "PlacedAdoption" not in dfs:
        return {}
    else:
        adopt_placed = dfs["PlacedAdoption"]
        adopt_placed["DATE_PLACED"] = pd.to_datetime(
            adopt_placed["DATE_PLACED"], format="%d/%m/%Y", errors="coerce"
        )
        adopt_placed["DATE_PLACED_CEASED"] = pd.to_datetime(
            adopt_placed["DATE_PLACED_CEASED"], format="%d/%m/%Y", errors="coerce"
        )

        adopt_placed.sort_values(["CHILD", "DATE_PLACED"], inplace=True)

        adopt_placed.reset_index(inplace=True)
        adopt_placed.reset_index(inplace=True)  # Twice on purpose

        adopt_placed["LAG_INDEX"] = adopt_placed["level_0"].shift(-1)

        lag_adopt_placed = adopt_placed.merge(
            adopt_placed,
            how="inner",
            left_on="level_0",
            right_on="LAG_INDEX",
            suffixes=["", "_PREV"],
        )

        # We're only interested in cases where there is more than one row for a child.
        lag_adopt_placed = lag_adopt_placed[
            lag_adopt_placed["CHILD"] == lag_adopt_placed["CHILD_PREV"]
        ]

        # A previous ADOPT_PLACED_CEASED date is null
        mask1 = lag_adopt_placed["DATE_PLACED_CEASED_PREV"].isna()
        # ADOPT_PLACED is before previous ADOPT_PLACED (overlapping dates)
        mask2 = (
            lag_adopt_placed["DATE_PLACED"]
            < lag_adopt_placed["DATE_PLACED_CEASED_PREV"]
        )

        mask = mask1 | mask2

        error_list = lag_adopt_placed["index"][mask].to_list()
        error_list.sort()
        return {"PlacedAdoption": error_list}


def test_validate():
    import pandas as pd

    fake_adopt_place = pd.DataFrame(
        [
            {
                "CHILD": "111",
                "DATE_PLACED": "01/06/2020",
                "DATE_PLACED_CEASED": "05/06/2020",
            },  # 0
            {
                "CHILD": "111",
                "DATE_PLACED": "04/06/2020",
                "DATE_PLACED_CEASED": pd.NA,
            },  # 1 Fails overlaps
            {
                "CHILD": "222",
                "DATE_PLACED": "03/06/2020",
                "DATE_PLACED_CEASED": "04/06/2020",
            },  # 2
            {
                "CHILD": "222",
                "DATE_PLACED": "04/06/2020",
                "DATE_PLACED_CEASED": pd.NA,
            },  # 3
            {
                "CHILD": "222",
                "DATE_PLACED": "07/06/2020",
                "DATE_PLACED_CEASED": "09/06/2020",
            },
            # 4 Fails, previous end is null
            {
                "CHILD": "333",
                "DATE_PLACED": "02/06/2020",
                "DATE_PLACED_CEASED": "04/06/2020",
            },  # 5
            {
                "CHILD": "333",
                "DATE_PLACED": "03/06/2020",
                "DATE_PLACED_CEASED": "09/06/2020",
            },  # 6 Fails overlaps
            {
                "CHILD": "555",
                "DATE_PLACED": pd.NA,
                "DATE_PLACED_CEASED": "05/06/2020",
            },  # 7
            {
                "CHILD": "555",
                "DATE_PLACED": pd.NA,
                "DATE_PLACED_CEASED": "05/06/2020",
            },  # 8
        ]
    )

    fake_dfs = {"PlacedAdoption": fake_adopt_place}

    result = validate(fake_dfs)

    assert result == {"PlacedAdoption": [1, 4, 6]}
