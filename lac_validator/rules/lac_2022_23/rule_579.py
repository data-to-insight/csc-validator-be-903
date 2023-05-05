import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="579",
    message="A new decision that the child should be placed for adoption this year cannot start when the previous decision is still open. Decisions to place the child for adoption should also not overlap. The date of any new decision to place the child for adoption must not be before the date placed ceased of previous decisions.",
    affected_fields=["DATE_PLACED", "DATE_PLACED_CEASED"],
)
def validate(dfs):
    if "PlacedAdoption" not in dfs:
        return {}
    else:
        adoptplaced = dfs["PlacedAdoption"]
        adoptplaced["DATEPLACED"] = pd.todatetime(
            adoptplaced["DATEPLACED"], format="%d/%m/%Y", errors="coerce"
        )
        adoptplaced["DATEPLACEDCEASED"] = pd.todatetime(
            adoptplaced["DATEPLACEDCEASED"], format="%d/%m/%Y", errors="coerce"
        )

        adoptplaced.sortvalues(["CHILD", "DATEPLACED"], inplace=True)

        adoptplaced.resetindex(inplace=True)
        adoptplaced.resetindex(inplace=True)  # Twice on purpose

        adoptplaced["LAGINDEX"] = adoptplaced["level0"].shift(-1)

        lagadoptplaced = adoptplaced.merge(
            adoptplaced,
            how="inner",
            lefton="level0",
            righton="LAGINDEX",
            suffixes=["", "PREV"],
        )

        # We're only interested in cases where there is more than one row for a child.
        lagadoptplaced = lagadoptplaced[
            lagadoptplaced["CHILD"] == lagadoptplaced["CHILDPREV"]
        ]

        # A previous ADOPTPLACEDCEASED date is null
        mask1 = lagadoptplaced["DATEPLACEDCEASEDPREV"].isna()
        # ADOPTPLACED is before previous ADOPTPLACED (overlapping dates)
        mask2 = lagadoptplaced["DATEPLACED"] < lagadoptplaced["DATEPLACEDCEASEDPREV"]

        mask = mask1 | mask2

        errorlist = lagadoptplaced["index"][mask].tolist()
        errorlist.sort()
        return {"PlacedAdoption": errorlist}


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

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"PlacedAdoption": [1, 4, 6]}
