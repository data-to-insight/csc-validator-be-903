import pandas as pd
import numpy as np

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="1016",
    message="If the child ceases to be looked after in the year, but is still looked after on or after their 17th or on their 18th birthday, then information on their activity and accommodation is not required.Please delete the OC3 information.",
    affected_fields=["IN_TOUCH", "ACTIV", "ACCOM"],
)
def validate(dfs):
    # If <DOB> < 19 and >= to 17 years prior to <COLLECTION_END_DATE>
    # and
    # current episode <DEC> is present and after the birthdate then
    # <IN_TOUCH>, <ACTIV> and <ACCOM> should not be provided
    if "OC3" not in dfs:
        return {}
    else:
        df = dfs["OC3"]
        collection_end = dfs["metadata"]["collection_end"]

        df["DOB"] = pd.to_datetime(df["DOB"], format="%d/%m/%Y")
        collection_end = pd.to_datetime(
            collection_end, format="%d/%m/%Y", errors="coerce"
        )

        df = df.reset_index()

        df["AGE_AT_CE"] = collection_end - df["DOB"]
        df_errors = df[
            (df["AGE_AT_CE"] < np.timedelta64(19, "Y"))
            & (df["AGE_AT_CE"] >= np.timedelta64(17, "Y"))
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
                "DOB": "01/01/2001",
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
        ]
    )

    metadata = {"collection_end": pd.to_datetime("01/01/2020", format="%d/%m/%Y")}

    fake_dfs = {
        "OC3": fake_data,
        "metadata": metadata,
    }

    result = validate(fake_dfs)

    assert result == {"OC3": [0, 3]}
