import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="218",
    message="Ofsted Unique reference number (URN) is required.",
    affected_fields=["URN"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        collection_start = dfs["metadata"]["collection_start"]
        pl_list = [
            "P1",
            "P3",
            "R1",
            "R2",
            "R5",
            "T0",
            "T1",
            "T2",
            "T3",
            "T4",
            "Z1",
        ]

        # convert string date values to datetime format to enable comparison.
        collection_start = pd.to_datetime(
            collection_start, format="%d/%m/%Y", errors="coerce"
        )
        episodes["DEC_dt"] = pd.to_datetime(
            episodes["DEC"], format="%d/%m/%Y", errors="coerce"
        )

        out_of_england = (
            episodes["PL_LA"]
            .astype("str")
            .str.upper()
            .str.startswith(("N", "W", "S", "C"))
        )
        place_exempt = episodes["PLACE"].isin(pl_list)
        ends_after_collection_start = (
            episodes["DEC_dt"] >= collection_start
        ) | episodes["DEC"].isna()

        mask = (
            ends_after_collection_start
            & episodes["URN"].isna()
            & ~place_exempt
            & ~out_of_england
        )

        error_locations = episodes.index[mask]
        return {"Episodes": error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_data_eps = pd.DataFrame(
        [
            {
                "CHILD": "0000",
                "PLACE": "H5",
                "DEC": pd.NA,
                "PL_LA": "o",
                "URN": pd.NA,
            },  # 4 fail
            {
                "CHILD": "1111",
                "PLACE": "C2",
                "DEC": "01/06/2015",
                "PL_LA": "W06000008",
                "URN": "xx",
            },  # 1 ignore: PL_LA is Wales
            {
                "CHILD": "1111",
                "PLACE": "C2",
                "DEC": "01/02/2016",
                "PL_LA": "o",
                "URN": "xx",
            },  # 2 pass
            {
                "CHILD": "2222",
                "PLACE": "C2",
                "DEC": "01/02/2014",
                "PL_LA": "o",
                "URN": "xx",
            },  # 3 ignore: DEC < coll. end
            {
                "CHILD": "2222",
                "PLACE": "xx",
                "DEC": pd.NA,
                "PL_LA": "o",
                "URN": pd.NA,
            },  # 4 fail
            {
                "CHILD": "2222",
                "PLACE": "R5",
                "DEC": "01/02/2016",
                "PL_LA": "o",
                "URN": "xx",
            },  # 5 ignore: of PLACE value
            {
                "CHILD": "3333",
                "PLACE": "C2",
                "DEC": "01/03/2014",
                "PL_LA": "o",
                "URN": pd.NA,
            },  # 6 ignore: DEC
            {
                "CHILD": "3333",
                "PLACE": "C2",
                "DEC": "04/01/2016",
                "PL_LA": "o",
                "URN": pd.NA,
            },  # 7 fail
            {
                "CHILD": "4444",
                "PLACE": "C2",
                "DEC": "01/02/2016",
                "PL_LA": "o",
                "URN": pd.NA,
            },  # 8 fail
            {
                "CHILD": "4444",
                "PLACE": "C2",
                "DEC": "01/04/2017",
                "PL_LA": "o",
                "URN": pd.NA,
            },  # 9 fail
            {
                "CHILD": "5555",
                "PLACE": "C2",
                "DEC": "31/03/2015",
                "PL_LA": "o",
                "URN": pd.NA,
            },  # 10 ignore: DEC
            {
                "CHILD": "5555",
                "PLACE": "C2",
                "DEC": "04/01/2016",
                "PL_LA": "SCO",
                "URN": pd.NA,
            },  # 11 ignore: in Scotland
        ]
    )

    metadata = {"collection_start": "01/04/2015"}

    fake_dfs = {"Episodes": fake_data_eps, "metadata": metadata}

    result = validate(fake_dfs)
    assert result == {"Episodes": [0, 4, 7, 8, 9]}
