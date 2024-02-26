import pandas as pd
import numpy as np

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="1016",
    message="Care leaver information is not required for 17- or 18-year olds who cease to be looked after, after their birthday.",
    affected_fields=["IN_TOUCH", "ACTIV", "ACCOM"],
)
def validate(dfs):
    # If <DOB> < 19 and >= to 17 years prior to <COLLECTION_END_DATE>
    # and
    # current episode <DEC> is present and after the birthdate then
    # <IN_TOUCH>, <ACTIV> and <ACCOM> should not be provided
    if ("OC3" not in dfs) | ("Episodes" not in dfs):
        return {}
    else:
        OC3 = dfs["OC3"]
        episodes = dfs["Episodes"]
        collection_end = dfs["metadata"]["collection_end"]

        OC3["DOB"] = pd.to_datetime(OC3["DOB"], format="%d/%m/%Y")
        collection_end = pd.to_datetime(
            collection_end, format="%d/%m/%Y", errors="coerce"
        )

        episodes["DEC"] = pd.to_datetime(
            episodes["DEC"], format="%d/%m/%Y", errors="coerce"
        )

        OC3 = OC3.reset_index()

        OC3["AGE_AT_CE"] = collection_end - OC3["DOB"]

        df_merged = OC3.merge(episodes, on="CHILD", how="inner")

        # Fails rows where the child is between 19 and 17 at the end of a return,
        # and their DEC is after their 17th birthday
        condition_17 = df_merged["DEC"] >= (df_merged["DOB"] + np.timedelta64(17, "Y"))
        condition_18 = df_merged["DEC"] >= (df_merged["DOB"] + np.timedelta64(18, "Y"))

        df_errors = df_merged[
            (df_merged["AGE_AT_CE"] < np.timedelta64(19, "Y"))
            & (df_merged["AGE_AT_CE"] >= np.timedelta64(17, "Y"))
            & (condition_17 | condition_18)
        ]

        df_errors = df_errors[
            df_errors["IN_TOUCH"].notna()
            | df_errors["ACTIV"].notna()
            | df_errors["ACCOM"].notna()
        ]

        return {"OC3": df_errors["index"].tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {
                "CHILD": "child1",
                "DOB": "31/03/2002",
                "IN_TOUCH": "Y",
                "ACTIV": "Y",
                "ACCOM": "Y",
            },
            {
                "CHILD": "child2",
                "DOB": "01/01/2001",
                "IN_TOUCH": pd.NA,
                "ACTIV": pd.NA,
                "ACCOM": pd.NA,
            },
            {
                "CHILD": "child3",
                "DOB": "01/01/2000",
                "IN_TOUCH": "Y",
                "ACTIV": "Y",
                "ACCOM": "Y",
            },
            {
                "CHILD": "child4",
                "DOB": "01/01/2002",
                "IN_TOUCH": "Y",
                "ACTIV": "Y",
                "ACCOM": "Y",
            },
            {
                "CHILD": "child5",
                "DOB": "01/01/2002",
                "IN_TOUCH": "Y",
                "ACTIV": "Y",
                "ACCOM": "Y",
            },
            {
                "CHILD": "child6",
                "DOB": "01/01/2002",
                "IN_TOUCH": "Y",
                "ACTIV": "Y",
                "ACCOM": "Y",
            },
            {
                "CHILD": "child7",
                "DOB": "01/01/2002",
                "IN_TOUCH": pd.NA,
                "ACTIV": pd.NA,
                "ACCOM": pd.NA,
            },
            {
                "CHILD": "child8",
                "DOB": "01/09/2002",
                "IN_TOUCH": "Y",
                "ACTIV": "Y",
                "ACCOM": "Y",
            },
            {
                "CHILD": "child9",
                "DOB": "01/09/2002",
                "IN_TOUCH": "Y",
                "ACTIV": "Y",
                "ACCOM": "Y",
            },
            {
                "CHILD": "child10",
                "DOB": "01/09/2001",
                "IN_TOUCH": "Y",
                "ACTIV": "Y",
                "ACCOM": "Y",
            },
        ]
    )

    fake_epi = pd.DataFrame(
        [
            {"CHILD": "child1", "DEC": "31/03/2020"},
            {"CHILD": "child2", "DEC": pd.NA},
            {"CHILD": "child3", "DEC": pd.NA},
            {"CHILD": "child4", "DEC": "01/01/2020"},
            {"CHILD": "child6", "DEC": pd.NA},
            {"CHILD": "child4", "DEC": pd.NA},
            {"CHILD": "child8", "DEC": "31/08/20020"},
            {"CHILD": "child9", "DEC": "02/09/2020"},
            {"CHILD": "child10", "DEC": "02/09/2020"},
        ]
    )

    metadata = {"collection_end": pd.to_datetime("31/03/2020", format="%d/%m/%Y")}

    fake_dfs = {
        "Episodes": fake_epi,
        "OC3": fake_data,
        "metadata": metadata,
    }

    result = validate(fake_dfs)

    assert result == {"OC3": [0, 3, 8, 9]}
