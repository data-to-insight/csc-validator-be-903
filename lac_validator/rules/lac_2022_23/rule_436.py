import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="436",
    message="Reason for new episode is that both child’s placement and legal status have changed, but this is not reflected in the episode data.",
    affected_fields=["RNE", "LS", "PLACE", "PL_POST", "URN", "PLACE_PROVIDER"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        epi = dfs["Episodes"]
        epi["DECOM"] = pd.todatetime(epi["DECOM"], format="%d/%m/%Y", errors="coerce")

        epi.sortvalues(["CHILD", "DECOM"], inplace=True)
        epi.resetindex(inplace=True)
        epi.resetindex(inplace=True)
        epi["LAGINDEX"] = epi["level0"].shift(-1)
        epi.fillna(
            value={
                "LS": "*",
                "PLACE": "*",
                "PLPOST": "*",
                "URN": "*",
                "PLACEPROVIDER": "*",
            },
            inplace=True,
        )
        epimerge = epi.merge(
            epi,
            how="inner",
            lefton="level0",
            righton="LAGINDEX",
            suffixes=["", "PRE"],
        )

        epimultirow = epimerge[epimerge["CHILD"] == epimerge["CHILDPRE"]]
        epihasBU = epimultirow[epimultirow["RNE"].isin(["U", "B"])]

        maskls = epihasBU["LS"] == epihasBU["LSPRE"]

        mask1 = epihasBU["PLACE"] == epihasBU["PLACEPRE"]
        mask2 = epihasBU["PLPOST"] == epihasBU["PLPOSTPRE"]
        mask3 = epihasBU["URN"] == epihasBU["URNPRE"]
        mask4 = epihasBU["PLACEPROVIDER"] == epihasBU["PLACEPROVIDERPRE"]

        errormask = maskls | (mask1 & mask2 & mask3 & mask4)

        errorlist = epihasBU[errormask]["index"].tolist()
        errorlist.sort()
        return {"Episodes": errorlist}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {"MISSING": "M", "MIS_END": pd.NA},  # 0
            {"MISSING": pd.NA, "MIS_END": "07/02/2020"},  # 1  Fails
            {"MISSING": "A", "MIS_END": "03/02/2020"},  # 2
            {"MISSING": pd.NA, "MIS_END": pd.NA},  # 3
            {"MISSING": "M", "MIS_END": "01/02/2020"},  # 4
            {"MISSING": pd.NA, "MIS_END": "13/02/2020"},  # 5  Fails
        ]
    )

    fake_dfs = {"Missing": fake_data}

    error_defn, error_func = validate()

    assert error_func(fake_dfs) == {"Missing": [1, 5]}
