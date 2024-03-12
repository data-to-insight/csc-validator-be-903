import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="SW05STG1",
    message="Date social worker episode began is not a valid date.",
    affected_fields=["SW_DEC"],
)
def validate(dfs):
    if "SWEpisodes" not in dfs:
        return {}
    else:
        df = dfs["SWEpisodes"]

        df = df[df["SW_DEC"].notna()].copy()

        # function to check that date is of the right format
        def valid_date(dte):
            try:
                lst = dte.split("/")
            except AttributeError:
                return pd.NaT
            # Preceding block checks for the scenario where the value passed in is nan/naT

            # date should have three elements
            if len(lst) != 3:
                return pd.NaT

            z_list = ["ZZ", "ZZ", "ZZZZ"]
            # We set the date to the latest possible value to avoid false positives
            offset_list = [
                pd.DateOffset(months=1, days=-1),
                pd.DateOffset(years=1, days=-1),
                None,
            ]
            # that is, go to the next month/year and take the day before that
            date_bits = []

            for i, zeds, offset in zip(lst, z_list, offset_list):
                if i == "ZZ":
                    i = "01"
                    offset_to_use = offset
                elif i == "ZZZZ":
                    i = "2000"
                date_bits.append(i)

            as_datetime = pd.to_datetime(
                "/".join(date_bits), format="%d/%m/%Y", errors="coerce"
            )
            try:
                as_datetime += offset_to_use
            except NameError:  # offset_to_use only defined if needed
                pass
            return as_datetime

        df["SW_DEC_dt"] = df["SW_DEC"].apply(valid_date)

        error_rows = df[df["SW_DEC_dt"].isna()].index

        return {"SWEpisodes": error_rows.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "SW_DEC": ["ZZ/ZZ/ZZZZ", "01/01/2001", "zz", "01/01/ZZZZ", pd.NA],
        }
    )

    fake_dfs = {"SWEpisodes": fake_data}

    result = validate(fake_dfs)

    assert result == {"SWEpisodes": [2]}
