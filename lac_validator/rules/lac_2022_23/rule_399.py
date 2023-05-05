from validator903.types import ErrorDefinition


@rule_definition(
    code="399",
    message="Mother field, review field or participation field are completed but "
    + "child is looked after under legal status V3 or V4.",
    affected_fields=["MOTHER", "LS", "REVIEW", "REVIEW_CODE"],
)
def validate(dfs):
    if "Episodes" not in dfs or "Header" not in dfs or "Reviews" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        header = dfs["Header"]
        reviews = dfs["Reviews"]

        codelist = ["V3", "V4"]
        # Rule adjustment: if child has any other episodes where LS is not V3 or V4, rule should not be triggered. Trigger error 399 only if all child episodes

        # Column that will contain True if LS of the episode is either V3 or V4
        episodes["LSCHECKS"] = episodes["LS"].isin(codelist)

        # Column that will contain True only if all LSs, for a child, are either V3 or V4
        episodes["LSCHECK"] = episodes.groupby("CHILD")["LSCHECKS"].transform("min")

        eps = episodes.loc[episodes["LSCHECK"] == True].copy()

        # prepare to merge
        eps["indexeps"] = eps.index
        header["indexhdr"] = header.index
        reviews["indexrevs"] = reviews.index

        # merge
        merged = eps.merge(header, on="CHILD", how="left").merge(
            reviews, on="CHILD", how="left"
        )

        # If <LS> = 'V3' or 'V4' then <MOTHER>, <REVIEW> and <REVIEWCODE> should not be provided
        mask = merged["LSCHECK"] & (
            merged["MOTHER"].notna()
            | merged["REVIEW"].notna()
            | merged["REVIEWCODE"].notna()
        )

        # Error locations
        epserrors = merged.loc[mask, "indexeps"].dropna().unique()
        headererrors = merged.loc[mask, "indexhdr"].dropna().unique()
        revserrors = merged.loc[mask, "indexrevs"].dropna().unique()

        return {
            "Episodes": epserrors.tolist(),
            "Header": headererrors.tolist(),
            "Reviews": revserrors.tolist(),
        }


def test_validate():
    import pandas as pd

    # change log

    # index 6 and 7 are changed to the same child such that though both have the review information, index 6 would no longer trigger the error because the child has another episode (index 7) where LS is not V3/V4.
    # Index 0 and 1 have been same to the same child such that all its episodes have LS V3/V4 and the error is trigged though index zero does not have the review information and would not have triggered the error on its own.
    # index 6 truly reflects the change. It would have failed earlier but it passes now since the child's other LS is not V3

    # test data assumes that child IDs cannot repeat in the header and reviews tables.

    fake_data_episodes = pd.DataFrame(
        {
            "CHILD": ["101", "101", "103", "104", "105", "106", "108", "108"],
            "LS": ["V4", "V4", "V3", "L4", pd.NA, "V4", "V3", "XO"],
        }
    )
    fake_data_header = pd.DataFrame(
        {
            "CHILD": ["101", "102", "103", "104", "105", "106", "108", "109"],
            "MOTHER": ["0", "0", pd.NA, pd.NA, 1, 0, 1, pd.NA],
        }
    )
    fake_data_reviews = pd.DataFrame(
        {
            "CHILD": ["101", "102", "103", "104", "105", "106", "108", "109"],
            "REVIEW": [
                "31/12/2008",
                "01/01/2012",
                pd.NA,
                "01/01/2009",
                "01/01/2012",
                "01/01/2017",
                "01/01/2021",
                "01/01/2015",
            ],
            "REVIEW_CODE": ["PN1", "PN2", pd.NA, "PN4", "PN5", "PN6", "PN7", "PN0"],
        }
    )
    fake_dfs = {
        "Header": fake_data_header,
        "Reviews": fake_data_reviews,
        "Episodes": fake_data_episodes,
    }
    error_defn, error_func = validate()
    result = error_func(fake_dfs)
    assert result == {
        "Header": [0, 5],
        "Reviews": [0, 5],
        "Episodes": [
            0,
            1,
            5,
        ],
    }
