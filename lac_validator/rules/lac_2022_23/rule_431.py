import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="431",
    message="The reason for new episode is started to be looked after, but the previous episode ended on the same day.",
    affected_fields=["RNE", "DECOM"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        epi = dfs["Episodes"]
        epi["DECOM"] = pd.todatetime(epi["DECOM"], format="%d/%m/%Y", errors="coerce")
        epi["DEC"] = pd.todatetime(epi["DEC"], format="%d/%m/%Y", errors="coerce")
        epi.sortvalues(["CHILD", "DECOM"], inplace=True)

        epi.resetindex(inplace=True)
        epi.resetindex(inplace=True)
        epi["LAGINDEX"] = epi["level0"].shift(-1)

        mepi = epi.merge(
            epi,
            how="inner",
            lefton="level0",
            righton="LAGINDEX",
            suffixes=["", "PREV"],
        )

        mepi = mepi[(mepi["CHILD"] == mepi["CHILDPREV"]) & (mepi["RNE"] == "S")]
        errormask = mepi["DECOM"] <= mepi["DECPREV"]
        errorlist = mepi["index"][errormask].tolist()
        errorlist.sort()
        return {"Episodes": errorlist}


def validate503Generic(subval):
    Gen503dict = {
        "A": {
            "Desc": "The reason for new episode in the first episode does not match open episode at end of last year.",
            "Fields": "RNE",
        },
        "B": {
            "Desc": "The legal status in the first episode does not match open episode at end of last year.",
            "Fields": "LS",
        },
        "C": {
            "Desc": "The category of need in the first episode does not match open episode at end of last year.",
            "Fields": "CIN",
        },
        "D": {
            "Desc": "The placement type in the first episode does not match open episode at end of last year",
            "Fields": "PLACE",
        },
        "E": {
            "Desc": "The placement provider in the first episode does not match open episode at end of last year.",
            "Fields": "PLACEPROVIDER",
        },
        "F": {
            "Desc": "The Ofsted URN in the  first episode does not match open episode at end of last year.",
            "Fields": "URN",
        },
        "G": {
            "Desc": "The distance in first episode does not match open episode at end of last year.",
            "Fields": "PLDISTANCE",
        },
        "H": {
            "Desc": "The placement LA in first episode does not match open episode at end of last year.",
            "Fields": "PLLA",
        },
        "J": {
            "Desc": "The placement location in first episode does not match open episode at end of last year.",
            "Fields": "PLLOCATION",
        },
    }
    error = ErrorDefinition(
        code="503" + subval,
        description=Gen503dict[subval]["Desc"],
        affectedfields=[Gen503dict[subval]["Fields"]],
    )

    def validate(dfs):
        if "Episodes" not in dfs or "Episodeslast" not in dfs:
            return {}
        else:
            epi = dfs["Episodes"]
            epilast = dfs["Episodeslast"]
            epi["DECOM"] = pd.todatetime(
                epi["DECOM"], format="%d/%m/%Y", errors="coerce"
            )
            epilast["DECOM"] = pd.todatetime(
                epilast["DECOM"], format="%d/%m/%Y", errors="coerce"
            )
            epilast["DEC"] = pd.todatetime(
                epilast["DEC"], format="%d/%m/%Y", errors="coerce"
            )

            epi.resetindex(inplace=True)

            firstepinds = epi.groupby(["CHILD"])["DECOM"].idxmin(skipna=True)
            mindecom = epi.loc[firstepinds, :]

            lastepinds = epilast.groupby(["CHILD"])["DECOM"].idxmax(skipna=True)
            maxlastdecom = epilast.loc[lastepinds, :]

            mergedco = mindecom.merge(
                maxlastdecom, how="inner", on=["CHILD"], suffixes=["", "PRE"]
            )

            thisone = Gen503dict[subval]["Fields"]
            preone = thisone + "PRE"

            if subval == "G":
                errmask = (
                    abs(
                        mergedco[thisone].astype(float) - mergedco[preone].astype(float)
                    )
                    >= 0.2
                )
            else:
                errmask = mergedco[thisone].astype(str) != mergedco[preone].astype(str)
            errmask = errmask & mergedco["DECPRE"].isna()

            errlist = mergedco["index"][errmask].unique().tolist()
            errlist.sort()
            return {"Episodes": errlist}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {
                "CHILD": "111",
                "RNE": "S",
                "DECOM": "01/06/2020",
                "DEC": "04/06/2020",
            },  # 0
            {
                "CHILD": "111",
                "RNE": "S",
                "DECOM": "05/06/2020",
                "DEC": "06/06/2020",
            },  # 1
            {
                "CHILD": "111",
                "RNE": "T",
                "DECOM": "06/06/2020",
                "DEC": "08/06/2020",
            },  # 2
            {
                "CHILD": "111",
                "RNE": "S",
                "DECOM": "08/06/2020",
                "DEC": "05/06/2020",
            },  # 3  Fails
            {
                "CHILD": "222",
                "RNE": "S",
                "DECOM": "05/06/2020",
                "DEC": "06/06/2020",
            },  # 4
            {
                "CHILD": "333",
                "RNE": "S",
                "DECOM": "06/06/2020",
                "DEC": "07/06/2020",
            },  # 5
            {"CHILD": "333", "RNE": "S", "DECOM": "10/06/2020", "DEC": pd.NA},  # 6
            {
                "CHILD": "444",
                "RNE": "S",
                "DECOM": "08/06/2020",
                "DEC": "09/06/2020",
            },  # 7
            {
                "CHILD": "444",
                "RNE": "S",
                "DECOM": "09/06/2020",
                "DEC": "10/06/2020",
            },  # 8  Fails
            {"CHILD": "444", "RNE": "S", "DECOM": "15/06/2020", "DEC": pd.NA},  # 9
            {
                "CHILD": "555",
                "RNE": "S",
                "DECOM": "11/06/2020",
                "DEC": "12/06/2020",
            },  # 10
            {
                "CHILD": "6666",
                "RNE": "S",
                "DECOM": "12/06/2020",
                "DEC": "13/06/2020",
            },  # 11
            {
                "CHILD": "6666",
                "RNE": "S",
                "DECOM": "13/06/2020",
                "DEC": "14/06/2020",
            },  # 12 Fails
            {
                "CHILD": "6666",
                "RNE": "S",
                "DECOM": "14/06/2020",
                "DEC": "15/06/2020",
            },  # 13 Fails
        ]
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [3, 8, 12, 13]}
