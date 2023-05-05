import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="580",
    message="Child is missing when cease being looked after but reason episode ceased not ‘E8’.",
    affected_fields=["REC"],
)
def validate(dfs):
    if "Episodes" not in dfs or "Missing" not in dfs:
        return {}
    else:
        epi = dfs["Episodes"]
        mis = dfs["Missing"]
        mis["MISEND"] = pd.todatetime(mis["MISEND"], format="%d/%m/%Y", errors="coerce")
        mis["DOB"] = pd.todatetime(mis["DOB"], format="%d/%m/%Y", errors="coerce")
        epi["DEC"] = pd.todatetime(epi["DEC"], format="%d/%m/%Y", errors="coerce")

        epi.resetindex(inplace=True)
        mis["BD18"] = mis["DOB"] + pd.DateOffset(years=18)

        mcoh = mis.merge(epi, how="inner", on="CHILD")
        mcoh = mcoh.query("(BD18 == MISEND) & (MISEND == DEC) & DEC.notnull()")
        errlist = mcoh.query("REC != 'E8'")["index"].unique().tolist()
        errlist.sort()
        return {"Episodes": errlist}


def test_validate():
    import pandas as pd

    fake_epi = pd.DataFrame(
        [
            {"CHILD": "111", "DEC": "01/06/2020", "REC": "E7"},  # 0 fails
            {"CHILD": "123", "DEC": "08/06/2020", "REC": "E7"},  # 1 fails
            {"CHILD": "222", "DEC": "05/06/2020", "REC": "E8"},  # 2
            {"CHILD": "333", "DEC": "06/06/2020", "REC": "E5"},  # 3 fails
            {"CHILD": "444", "DEC": "07/06/2020", "REC": "E8"},  # 4
            {"CHILD": "555", "DEC": "19/06/2020", "REC": "E4"},  # 5 fails
            {"CHILD": "777", "DEC": "19/06/2020", "REC": "E4"},  # 6 fails
        ]
    )

    fake_mis = pd.DataFrame(
        [
            {
                "CHILD": "111",
                "MISSING": "M",
                "MIS_END": "01/06/2020",
                "DOB": "01/06/2002",
            },  #
            {
                "CHILD": "123",
                "MISSING": "M",
                "MIS_END": "08/06/2020",
                "DOB": "08/06/2002",
            },  #
            {
                "CHILD": "222",
                "MISSING": "M",
                "MIS_END": "05/06/2020",
                "DOB": "05/06/2002",
            },  #
            {
                "CHILD": "333",
                "MISSING": "M",
                "MIS_END": "06/06/2020",
                "DOB": "06/06/2002",
            },  #
            {
                "CHILD": "444",
                "MISSING": "M",
                "MIS_END": "08/06/2020",
                "DOB": "08/06/2002",
            },  #
            {
                "CHILD": "444",
                "MISSING": "M",
                "MIS_END": "09/06/2020",
                "DOB": "09/06/2002",
            },  #
            {
                "CHILD": "555",
                "MISSING": "M",
                "MIS_END": "19/06/2020",
                "DOB": "19/06/2002",
            },  #
            {
                "CHILD": "777",
                "MISSING": "A",
                "MIS_END": "19/06/2020",
                "DOB": "19/06/2002",
            },  #
        ]
    )

    fake_dfs = {"Episodes": fake_epi, "Missing": fake_mis}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [0, 1, 3, 5, 6]}
