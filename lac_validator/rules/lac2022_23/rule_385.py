import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="385",
    message="Date episode ceased must be on or before the end of the current collection year.",
    affected_fields=["DEC"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        epi = dfs["Episodes"]
        collection_end = pd.to_datetime(
            dfs["metadata"]["collection_end"], format="%d/%m/%Y", errors="coerce"
        )
        epi["DEC"] = pd.to_datetime(epi["DEC"], format="%d/%m/%Y", errors="coerce")
        error_mask = epi["DEC"] > collection_end
        error_list = epi.index[error_mask].to_list()
        return {"Episodes": error_list}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "DEC": [
                "14/03/2021",
                "08/09/2021",
                "03/10/2020",
                "04/04/2021",
                pd.NA,
                "Tuesday 33st",
            ],
        }
    )

    metadata = {"collection_end": "01/04/2021"}

    fake_dfs = {"Episodes": fake_data, "metadata": metadata}

    result = validate(fake_dfs)

    assert result == {"Episodes": [1, 3]}
