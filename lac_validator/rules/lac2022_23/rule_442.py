import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="442",
    message="Unique Pupil Number (UPN) field is not completed.",
    affected_fields=["UPN"],
)
def validate(dfs):
    if ("Episodes" not in dfs) or ("Header" not in dfs):
        return {}
    else:
        episodes = dfs["Episodes"]
        header = dfs["Header"]

        episodes.reset_index(inplace=True)
        header.reset_index(inplace=True)

        code_list = ["V3", "V4"]

        # merge to get all children for which episodes have been recorded.
        merged = episodes.merge(
            header, on=["CHILD"], how="inner", suffixes=["_eps", "_er"]
        )
        # Where any episode present, with an <LS> not = 'V3' or 'V4' then <UPN> must be provided
        mask = (~merged["LS"].isin(code_list)) & merged["UPN"].isna()
        header_error_locs = merged.loc[mask, "index_er"]

        return {
            # Select unique values since many episodes are joined to one header
            # and multiple errors will be raised for the same index.
            "Header": header_error_locs.dropna()
            .unique()
            .tolist()
        }


def test_validate():
    import pandas as pd

    fake_data_episodes = pd.DataFrame(
        {
            "CHILD": ["101", "102", "103", "104", "105", "106", "108", "999"],
            "LS": [pd.NA, "L4", pd.NA, "L4", "L1", "V4", "V3", "XO"],
        }
    )
    fake_data_header = pd.DataFrame(
        {
            "CHILD": ["101", "102", "103", "104", "105", "106", "108"],
            "UPN": [pd.NA, "H801200001001", "UN1", "UN2", pd.NA, "UN3", pd.NA],
        }
    )
    fake_dfs = {"Episodes": fake_data_episodes, "Header": fake_data_header}

    result = validate(fake_dfs)

    assert result == {"Header": [0, 4]}
