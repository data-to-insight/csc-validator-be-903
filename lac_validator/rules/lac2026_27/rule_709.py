import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="709",
    message="Child with a DoLO is in an unexpected placement type.",
    affected_fields=["DOLO_START"],
    tables=["DoLo"],
)
def validate(dfs):
    # If <DOLO_START> and <DOLO_END> are present then <PLACEMENT> for any episode
    # where <DECOM> and <DEC> overlap the DOLO should be 'K2', 'Z12', or 'Z13'.
    if "DoLo" not in dfs:
        return {}
    if "Episodes" not in dfs:
        return {}

    dolo = dfs["DoLo"]
    epi = dfs["Episodes"]

    dolo["index"] = dolo.index

    # The rule asks for dolo start and end to be present but if it
    # didn't we could find overlaps by popping collection end as DOLO_END
    dolo = dolo[dolo["DOLO_START"].notna() & dolo["DOLO_END"].notna()].copy()

    dolo["DOLO_START_dt"] = pd.to_datetime(
        dolo["DOLO_START"], dayfirst=True, errors="coerce"
    )
    dolo["DOLO_END_dt"] = pd.to_datetime(
        dolo["DOLO_END"], dayfirst=True, errors="coerce"
    )

    epi["DEC_dt"] = pd.to_datetime(epi["DEC"], dayfirst=True, errors="coerce")
    epi["DECOM_dt"] = pd.to_datetime(epi["DECOM"], dayfirst=True, errors="coerce")

    merged = epi.merge(dolo, on="CHILD", how="inner")

    # We can find overlaps by finding a DOLO_START before a DEC and a DOLO_END after a  after a DECOM
    overlaps = merged[
        (merged["DOLO_START_dt"] <= merged["DEC_dt"])
        & (merged["DOLO_END_dt"] >= merged["DECOM_dt"])
    ]

    wrong_placement_overlaps = overlaps[
        ~overlaps["PLACEMENT"].isin(["K2", "Z12", "Z13"])
    ]

    error_rows = wrong_placement_overlaps["index"]

    return {"DoLo": error_rows.tolist()}


def test_validate():
    import pandas as pd

    fake_dolo = pd.DataFrame(
        [
            {
                "CHILD": 1,
                "DOLO_START": "02/01/2000",
                "DOLO_END": "03/01/2000",
            },  # dolo inside ep1, fail on placement
            {
                "CHILD": 1,
                "DOLO_START": "02/01/2000",
                "DOLO_END": "05/01/2000",
            },  # dolo starts inside ep1, ends after, fail on placement
            {
                "CHILD": 1,
                "DOLO_START": "31/01/1999",
                "DOLO_END": "03/01/2000",
            },  # dolo startes before ep1, fail on placement
            {
                "CHILD": 1,
                "DOLO_START": "31/01/1999",
                "DOLO_END": "05/01/2000",
            },  # dolo starts before ends after ep1, fail on placement
            {
                "CHILD": 1,
                "DOLO_START": "25/12/1999",
                "DOLO_END": "31/12/1999",
            },  # dolo starts and ends before ep1, pass
            {
                "CHILD": 1,
                "DOLO_START": "06/01/2000",
                "DOLO_END": "07/01/2000",
            },  # dolo starts and ends after ep1, pass
            {
                "CHILD": 1,
                "DOLO_START": "02/01/2000",
                "DOLO_END": pd.NA,
            },  # pass no DOLO_END
            {
                "CHILD": 1,
                "DOLO_START": pd.NA,
                "DOLO_END": "07/01/2000",
            },  # pass no DOLO_START
        ]
    )

    fake_eps = pd.DataFrame(
        [
            {
                "CHILD": 1,
                "DECOM": "01/01/2000",
                "DEC": "04/01/2000",
                "PLACEMENT": "P",
            },  # episode 1
            {
                "CHILD": 1,
                "DECOM": "01/01/2000",
                "DEC": "04/01/2000",
                "PLACEMENT": "K2",
            },  # same dates as ep but pass due to placement
            {"CHILD": 2, "DECOM": "01/01/2000", "DEC": "03/01/2000", "PLACEMENT": "P"},
        ]
    )

    fake_dfs = {"DoLo": fake_dolo, "Episodes": fake_eps}

    result = validate(fake_dfs)

    assert result == {"DoLo": [0, 1, 2, 3]}
