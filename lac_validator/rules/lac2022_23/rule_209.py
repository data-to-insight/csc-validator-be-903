import pandas as pd

from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="209",
    message="Child looked after is of school age and should not have an unknown Unique Pupil Number (UPN) code of UN1.",
    affected_fields=["UPN", "DOB"],
)
def validate(dfs):
    if "Header" not in dfs:
        return {}
    else:
        header = dfs["Header"]
        collection_start = dfs["metadata"]["collection_start"]
        # convert to datetime
        header["DOB"] = pd.to_datetime(
            header["DOB"], format="%d/%m/%Y", errors="coerce"
        )
        collection_start = pd.to_datetime(
            collection_start, format="%d/%m/%Y", errors="coerce"
        )
        yr = collection_start.year - 1
        reference_date = pd.to_datetime(
            "31/08/" + str(yr), format="%d/%m/%Y", errors="coerce"
        )
        # If <DOB> >= 4 years prior to 31/08/YYYY then <UPN> should not be 'UN1' Note: YYYY in this instance refers to the year prior to the collection start (for collection year 2019-2020, it would be looking at the 31/08/2018).
        mask = (reference_date >= (header["DOB"] + pd.offsets.DateOffset(years=4))) & (
            header["UPN"] == "UN1"
        )
        # error locations
        error_locs_header = header.index[mask]
        return {"Header": error_locs_header.tolist()}


def test_validate():
    import pandas as pd

    fake_data_header = pd.DataFrame(
        {
            "CHILD": ["101", "102", "103", "104", "105", "106", "107"],
            "UPN": [pd.NA, "H801200001001", "UN1", "UN2", pd.NA, "UN1", pd.NA],
            "DOB": [
                "01/01/2020",
                "11/11/2020",
                "03/10/2015",
                "11/11/2020",
                "01/01/2020",
                "11/11/2020",
                "01/02/2020",
            ],
        }
    )
    metadata = {
        "collection_start": "01/04/2025",
    }
    fake_dfs = {"Header": fake_data_header, "metadata": metadata}

    
    result = validate(fake_dfs)

    assert result == {"Header": [2]}
