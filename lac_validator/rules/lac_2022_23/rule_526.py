import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="526",
    message="Child is missing a placement provider code for at least one episode.",
    affected_fields=["PLACE", "PLACE_PROVIDER"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        epi = dfs["Episodes"]
        errormask = (
            ~epi["PLACE"].isin(["T0", "T1", "T2", "T3", "T4", "Z1"])
            & epi["PLACEPROVIDER"].isna()
        )
        return {"Episodes": epi.index[errormask].tolist()}


def validate370to376and379(subval):
    Gen370dict = {
        "370": {
            "Desc": "Child in independent living should be at least 15.",
            "PCode": "P2",
            "Ygap": 15,
        },
        "371": {
            "Desc": "Child in semi-independent living accommodation not subject to children’s homes regulations "
            + "should be at least 14.",
            "PCode": "H5",
            "Ygap": 14,
        },
        "372": {
            "Desc": "Child in youth custody or prison should be at least 10.",
            "PCode": "R5",
            "Ygap": 10,
        },
        "373": {
            "Desc": "Child placed in a school should be at least 4 years old.",
            "PCode": "S1",
            "Ygap": 4,
        },
        "374": {
            "Desc": "Child in residential employment should be at least 14 years old.",
            "PCode": "P3",
            "Ygap": 14,
        },
        "375": {
            "Desc": "Hospitalisation coded as a temporary placement exceeds six weeks.",
            "PCode": "T1",
            "Ygap": 42,
        },
        "376": {
            "Desc": "Temporary placements coded as being due to holiday of usual foster carer(s) cannot exceed "
            + "three weeks.",
            "PCode": "T3",
            "Ygap": 21,
        },
        "379": {
            "Desc": "Temporary placements for unspecified reason (placement code T4) cannot exceed seven days.",
            "PCode": "T4",
            "Ygap": 7,
        },
    }
    error = ErrorDefinition(
        code=str(subval),
        description=Gen370dict[subval]["Desc"],
        affectedfields=["DECOM", "PLACE"],
    )

    def validate(dfs):
        if "Episodes" not in dfs or "Header" not in dfs:
            return {}
        else:
            epi = dfs["Episodes"]
            hea = dfs["Header"]
            hea["DOB"] = pd.todatetime(hea["DOB"], format="%d/%m/%Y", errors="coerce")
            epi["DECOM"] = pd.todatetime(
                epi["DECOM"], format="%d/%m/%Y", errors="coerce"
            )
            epi["DEC"] = pd.todatetime(epi["DEC"], format="%d/%m/%Y", errors="coerce")
            epi.resetindex(inplace=True)
            epip2 = epi[epi["PLACE"] == Gen370dict[subval]["PCode"]]
            mergede = epip2.merge(hea, how="inner", on="CHILD")
            mergede = mergede.dropna(subset=["DECOM", "DEC", "DOB"])
            if subval in ["370", "371", "372", "373", "374"]:
                errormask = mergede["DECOM"] < (
                    mergede["DOB"]
                    + pd.offsets.DateOffset(years=Gen370dict[subval]["Ygap"])
                )
            else:
                errormask = mergede["DEC"] > (
                    mergede["DECOM"]
                    + pd.offsets.DateOffset(days=Gen370dict[subval]["Ygap"])
                )
            return {"Episodes": mergede["index"][errormask].unique().tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "PLACE": ["E1", "P0", "T1", "T3", "P1", "Z1", "P0"],
            "PLACE_PROVIDER": ["PR1", "PR2", pd.NA, "PR0", pd.NA, pd.NA, pd.NA],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    assert error_func(fake_dfs) == {"Episodes": [4, 6]}
