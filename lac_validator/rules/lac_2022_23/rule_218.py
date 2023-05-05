import pandas as pd

from validator903.types import ErrorDefinition


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
        collectionstart = dfs["metadata"]["collectionstart"]
        pllist = [
            "H5",
            "P1",
            "P2",
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
        collectionstart = pd.todatetime(
            collectionstart, format="%d/%m/%Y", errors="coerce"
        )
        episodes["DECdt"] = pd.todatetime(
            episodes["DEC"], format="%d/%m/%Y", errors="coerce"
        )

        outofengland = (
            episodes["PLLA"]
            .astype("str")
            .str.upper()
            .str.startswith(("N", "W", "S", "C"))
        )
        placeexempt = episodes["PLACE"].isin(pllist)
        endsaftercollectionstart = (episodes["DECdt"] >= collectionstart) | episodes[
            "DEC"
        ].isna()

        mask = (
            endsaftercollectionstart
            & episodes["URN"].isna()
            & ~placeexempt
            & ~outofengland
        )

        errorlocations = episodes.index[mask]
        return {"Episodes": errorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data_eps = pd.DataFrame(
        [
            {
                "CHILD": "1111",
                "PLACE": "H5",
                "DEC": "01/02/2014",
                "PL_LA": "o",
                "URN": "xx",
            },  # 0 ignore: of PLACE value
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
    error_defn, error_func = validate()

    result = error_func(fake_dfs)
    assert result == {"Episodes": [4, 7, 8, 9]}
