from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="557",
    message="Child for whom the decision was made that they should be placed for adoption has left care "
    + "but was not adopted and information on the decision that they should no longer be placed for "
    + "adoption items has not been completed.",
    affected_fields=[
        "DATE_PLACED_CEASED",
        "REASON_PLACED_CEASED",  # PlacedAdoption
        "PLACE",
        "LS",
        "REC",
    ],  # Episodes
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    if "PlacedAdoption" not in dfs:
        return {}
    else:
        eps = dfs["Episodes"]
        placed = dfs["PlacedAdoption"]

        eps = eps.reset_index()
        placed = placed.reset_index()

        child_placed = eps["PLACE"].isin(["A3", "A4", "A5", "A6"])
        order_granted = eps["LS"].isin(["D1", "E1"])
        not_adopted = (
            ~eps["REC"].isin(["E11", "E12"]) & eps["REC"].notna() & (eps["REC"] != "X1")
        )

        placed["ceased_incomplete"] = (
            placed["DATE_PLACED_CEASED"].isna() | placed["REASON_PLACED_CEASED"].isna()
        )

        eps = eps[(child_placed | order_granted) & not_adopted]

        eps = eps.merge(
            placed, on="CHILD", how="left", suffixes=["_EP", "_PA"], indicator=True
        )

        eps = eps[(eps["_merge"] == "left_only") | eps["ceased_incomplete"]]

        EP_errors = eps["index_EP"]
        PA_errors = eps["index_PA"].dropna()

        return {
            "Episodes": EP_errors.to_list(),
            "PlacedAdoption": PA_errors.to_list(),
        }


def test_validate():
    import pandas as pd

    test_episodes = pd.DataFrame(
        [
            {
                "CHILD": "11",
                "PLACE": "A3",
                "LS": "x",
                "REC": "x",
            },  # 0: Fail! (missing vals in PA)
            {
                "CHILD": "202",
                "PLACE": "x",
                "LS": "D1",
                "REC": "x",
            },  # 1: PA filled in --ok
            {"CHILD": "3003", "PLACE": "A4", "LS": "D1", "REC": "E12"},  # 2: E12 --ok
            {"CHILD": "40004", "PLACE": "x", "LS": "E1", "REC": "E12"},  # 3: E12 --ok
            {
                "CHILD": "5005",
                "PLACE": "A5",
                "LS": "x",
                "REC": "x",
            },  # 4: Fail! (not in PA)
            {
                "CHILD": "606",
                "PLACE": "A6",
                "LS": "x",
                "REC": "x",
            },  # 5: Fail! (missing vals in PA)
            {"CHILD": "77", "PLACE": "x", "LS": "x", "REC": "x"},  # 6 --ok
            {
                "CHILD": "8",
                "PLACE": "A6",
                "LS": "x",
                "REC": "X1",
            },  # 5: --ok (REC is X1)
        ]
    )

    test_placed = pd.DataFrame(
        [
            {
                "CHILD": "11",
                "DATE_PLACED_CEASED": pd.NA,
                "REASON_PLACED_CEASED": pd.NA,
            },  # 0: Fail!
            {
                "CHILD": "202",
                "DATE_PLACED_CEASED": "01/02/2003",
                "REASON_PLACED_CEASED": "invalid dont matter",
            },  # 1
            {
                "CHILD": "3003",
                "DATE_PLACED_CEASED": pd.NA,
                "REASON_PLACED_CEASED": pd.NA,
            },  # 2: E12 in EP --ok
            {
                "CHILD": "40004",
                "DATE_PLACED_CEASED": pd.NA,
                "REASON_PLACED_CEASED": pd.NA,
            },  # 3: E12 in EP  --ok
            {
                "CHILD": "606",
                "DATE_PLACED_CEASED": pd.NA,
                "REASON_PLACED_CEASED": pd.NA,
            },  # 4: Fail! (missing vals in PA)
        ]
    )

    fake_dfs = {
        "Episodes": test_episodes,
        "PlacedAdoption": test_placed,
    }

    

    result = validate(fake_dfs)

    assert result == {
        "PlacedAdoption": [0, 4],
        "Episodes": [0, 4, 5],
    }
