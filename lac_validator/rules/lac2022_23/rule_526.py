import pandas as pd

from lac_validator.rule_engine import rule_definition


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
        error_mask = (
            ~epi["PLACE"].isin(["T0", "T1", "T2", "T3", "T4", "Z1"])
            & epi["PLACE_PROVIDER"].isna()
        )
        return {"Episodes": epi.index[error_mask].to_list()}


def validate_370to376and379(subval):
    Gen_370_dict = {
        "370": {
            "Desc": "Child in independent living should be at least 15.",
            "P_Code": "P2",
            "Y_gap": 15,
        },
        "371": {
            "Desc": "Child in semi-independent living accommodation not subject to children’s homes regulations "
            + "should be at least 14.",
            "P_Code": "H5",
            "Y_gap": 14,
        },
        "372": {
            "Desc": "Child in youth custody or prison should be at least 10.",
            "P_Code": "R5",
            "Y_gap": 10,
        },
        "373": {
            "Desc": "Child placed in a school should be at least 4 years old.",
            "P_Code": "S1",
            "Y_gap": 4,
        },
        "374": {
            "Desc": "Child in residential employment should be at least 14 years old.",
            "P_Code": "P3",
            "Y_gap": 14,
        },
        "375": {
            "Desc": "Hospitalisation coded as a temporary placement exceeds six weeks.",
            "P_Code": "T1",
            "Y_gap": 42,
        },
        "376": {
            "Desc": "Temporary placements coded as being due to holiday of usual foster carer(s) cannot exceed "
            + "three weeks.",
            "P_Code": "T3",
            "Y_gap": 21,
        },
        "379": {
            "Desc": "Temporary placements for unspecified reason (placement code T4) cannot exceed seven days.",
            "P_Code": "T4",
            "Y_gap": 7,
        },
    }
    error = ErrorDefinition(
        code=str(subval),
        description=Gen_370_dict[subval]["Desc"],
        affected_fields=["DECOM", "PLACE"],
    )

    def validate(dfs):
        if "Episodes" not in dfs or "Header" not in dfs:
            return {}
        else:
            epi = dfs["Episodes"]
            hea = dfs["Header"]
            hea["DOB"] = pd.to_datetime(hea["DOB"], format="%d/%m/%Y", errors="coerce")
            epi["DECOM"] = pd.to_datetime(
                epi["DECOM"], format="%d/%m/%Y", errors="coerce"
            )
            epi["DEC"] = pd.to_datetime(epi["DEC"], format="%d/%m/%Y", errors="coerce")
            epi.reset_index(inplace=True)
            epi_p2 = epi[epi["PLACE"] == Gen_370_dict[subval]["P_Code"]]
            merged_e = epi_p2.merge(hea, how="inner", on="CHILD")
            merged_e = merged_e.dropna(subset=["DECOM", "DEC", "DOB"])
            if subval in ["370", "371", "372", "373", "374"]:
                error_mask = merged_e["DECOM"] < (
                    merged_e["DOB"]
                    + pd.offsets.DateOffset(years=Gen_370_dict[subval]["Y_gap"])
                )
            else:
                error_mask = merged_e["DEC"] > (
                    merged_e["DECOM"]
                    + pd.offsets.DateOffset(days=Gen_370_dict[subval]["Y_gap"])
                )
            return {"Episodes": merged_e["index"][error_mask].unique().tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "PLACE": ["E1", "P0", "T1", "T3", "P1", "Z1", "P0"],
            "PLACE_PROVIDER": ["PR1", "PR2", pd.NA, "PR0", pd.NA, pd.NA, pd.NA],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    assert validate(fake_dfs) == {"Episodes": [4, 6]}
