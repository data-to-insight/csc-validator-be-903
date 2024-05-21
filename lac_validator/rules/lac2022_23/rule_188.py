import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="188",
    message="Child is aged under 4 years at the end of the year, "
    "but a Strengths and Difficulties (SDQ) score or a reason "
    "for no SDQ score has been completed. ",
    affected_fields=["SDQ_SCORE", "SDQ_REASON"],
    tables=["OC2"],
)
def validate(dfs):
    if "OC2" not in dfs:
        return {}

    oc2 = dfs["OC2"]

    collection_end_str = dfs["metadata"]["collection_end"]

    collection_end = pd.to_datetime(
        collection_end_str, format="%d/%m/%Y", errors="coerce"
    )
    oc2["DOB_dt"] = pd.to_datetime(oc2["DOB"], format="%d/%m/%Y", errors="coerce")

    oc2["4th_bday"] = oc2["DOB_dt"] + pd.DateOffset(years=4)
    error_mask = (oc2["4th_bday"] > collection_end) & oc2[
        ["SDQ_SCORE", "SDQ_REASON"]
    ].notna().any(axis=1)

    oc2_errors = oc2.loc[error_mask].index.to_list()

    return {"OC2": oc2_errors}


def test_validate():
    import pandas as pd

    metadata = {"collection_end": "31/03/1981"}

    oc2 = pd.DataFrame(
        {
            "CHILD": ["0", "1", "2", "3", "4"],
            "DOB": [
                "01/01/1970",
                "01/01/1980",
                "01/01/1970",
                "31/03/1977",
                "01/04/1977",
            ],
            "SDQ_SCORE": ["OK", "!!!", pd.NA, "OK", "!!!"],
        }
    )

    oc2["SDQ_REASON"] = pd.NA

    fake_dfs = {"OC2": oc2, "metadata": metadata}

    result = validate(fake_dfs)

    assert result == {"OC2": [1, 4]}
