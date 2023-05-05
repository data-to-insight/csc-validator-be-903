from validator903.types import ErrorDefinition


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

        episodes.resetindex(inplace=True)
        header.resetindex(inplace=True)

        codelist = ["V3", "V4"]

        # merge to get all children for which episodes have been recorded.
        merged = episodes.merge(
            header, on=["CHILD"], how="inner", suffixes=["eps", "er"]
        )
        # Where any episode present, with an <LS> not = 'V3' or 'V4' then <UPN> must be provided
        mask = (~merged["LS"].isin(codelist)) & merged["UPN"].isna()
        headererrorlocs = merged.loc[mask, "indexer"]

        return {
            # Select unique values since many episodes are joined to one header
            # and multiple errors will be raised for the same index.
            "Header": headererrorlocs.dropna()
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
    error_defn, error_func = validate()
    result = error_func(fake_dfs)

    assert result == {"Header": [0, 4]}
