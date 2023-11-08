import pandas as pd
import numpy as np

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="347",
    message="Only care leavers aged 18 years or over can be accommodated in a Foyer or similar accommodation. Check if the accommodation should be reported instead as ‘D’ (registered supported accommodation) or ‘Y’ (other accommodation).",
    affected_fields=["PLACE", "DEC", "URN"],
)
def validate(dfs):
    # If <ACCOM> = ‘T’ then <DOB> must be >= 18 years prior to <COLLECTION_START_DATE>
    if "OC3" not in dfs:
        return {}
    else:
        df = dfs["OC3"]
        collection_end = dfs["metadata"]["collection_start"]
        df = df.reset_index()
        df["AGE_AT_CE"] = collection_end - df["DOB"]
        df_T = df[df["ACCOM"] == "T"]

        df_errors = df_T[~(df_T["AGE_AT_CE"] >= np.timedelta64(18, "Y"))]

        return {"OC3": df_errors["index"].tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {
                "CHILD": "child1",
                "DOB": "01/01/1999",
                "IN_TOUCH": "Y",
                "ACTIV": "Y",
                "ACCOM": "T",
            },  # 0 Pass over 18
            {
                "CHILD": "child2",
                "DOB": "01/01/2010",
                "IN_TOUCH": pd.NA,
                "ACTIV": pd.NA,
                "ACCOM": pd.NA,
            },  # 1 Pass under 18 but not accom = T
            {
                "CHILD": "child3",
                "DOB": "01/01/2000",
                "IN_TOUCH": "Y",
                "ACTIV": "Y",
                "ACCOM": "T",
            },  # 2 Pass over 18
            {
                "CHILD": "child4",
                "DOB": "01/01/2002",
                "IN_TOUCH": "Y",
                "ACTIV": "Y",
                "ACCOM": "T",
            },  # Fail, under 18, accom = T
        ]
    )

    fake_data["DOB"] = pd.to_datetime(fake_data["DOB"], format="%d/%m/%Y")
    metadata = {"collection_start": pd.to_datetime("01/01/2020", format="%d/%m/%Y")}

    fake_dfs = {
        "OC3": fake_data,
        "metadata": metadata,
    }

    result = validate(fake_dfs)

    assert result == {"OC3": [3]}
