import pandas as pd

from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="210",
        description="Children looked after for more than a week at 31 March should not have an unknown Unique Pupil Number (UPN) code of UN4.",
        affected_fields=["UPN", "DECOM"],
    )

    def _validate(dfs):
        if "Header" not in dfs or "Episodes" not in dfs:
            return {}
        else:
            header = dfs["Header"]
            episodes = dfs["Episodes"]
            collection_end = dfs["metadata"]["collection_end"]
            # convert to datetime
            episodes["DECOM"] = pd.to_datetime(
                episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
            )
            collection_end = pd.to_datetime(
                collection_end, format="%d/%m/%Y", errors="coerce"
            )
            yr = collection_end.year
            reference_date = ref_date = pd.to_datetime(
                "24/03/" + str(yr), format="%d/%m/%Y", errors="coerce"
            )
            # prepare to merge
            episodes.reset_index(inplace=True)
            header.reset_index(inplace=True)
            # the logical way is to merge left on UPN but that will be a one to many merge and may not go as well as a many to one merge that we've been doing.
            merged = episodes.merge(
                header, on="CHILD", how="left", suffixes=["_eps", "_er"]
            )
            # If <UPN> = 'UN4' then no episode <DECOM> must be >` = 24/03/YYYY Note: YYYY refers to the current collection year.
            mask = (merged["UPN"] == "UN4") & (merged["DECOM"] >= reference_date)
            # error locations
            error_locs_header = merged.loc[mask, "index_er"]
            error_locs_eps = merged.loc[mask, "index_eps"]
            return {
                "Episodes": error_locs_eps.tolist(),
                "Header": error_locs_header.unique().tolist(),
            }

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data_header = pd.DataFrame(
        {
            "CHILD": ["111", "123", "333", "444", "667"],
            "UPN": [
                "UN4",
                pd.NA,
                "UN3",
                "UN4",
                "UN4",
            ],
        }
    )
    fake_data_epi = pd.DataFrame(
        [
            {
                "CHILD": "111",
                "DECOM": "01/01/2020",
            },  # 0
            {
                "CHILD": "111",
                "DECOM": "11/01/2020",
            },  # 1
            {
                "CHILD": "111",
                "DECOM": "30/03/2020",
            },  # 2 fail
            {
                "CHILD": "123",
                "DECOM": "01/01/2020",
            },  # 3
            {
                "CHILD": "123",
                "DECOM": "11/01/2020",
            },  # 4
            {
                "CHILD": "333",
                "DECOM": "01/01/2020",
            },  # 5
            {
                "CHILD": "333",
                "DECOM": "22/01/2020",
            },  # 6
            {
                "CHILD": "333",
                "DECOM": "11/01/2020",
            },  # 7
            {
                "CHILD": "444",
                "DECOM": "22/01/2020",
            },  # 8
            {
                "CHILD": "444",
                "DECOM": "25/03/2020",
            },  # 9 fail
            {
                "CHILD": "444",
                "DECOM": "01/01/2020",
            },  # 10
            {
                "CHILD": "667",
                "DECOM": "01/01/2020",
            },  # 11
        ]
    )
    metadata = {"collection_end": "31/03/2020"}

    fake_dfs = {
        "Episodes": fake_data_epi,
        "Header": fake_data_header,
        "metadata": metadata,
    }
    error_defn, error_func = validate()
    result = error_func(fake_dfs)
    assert result == {"Episodes": [2, 9], "Header": [0, 3]}
