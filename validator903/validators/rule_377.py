import pandas as pd

from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="377",
        description="Only two temporary placements coded as being due to holiday of usual foster carer(s) are "
        + "allowed in any 12- month period.",
        affected_fields=["PLACE"],
    )

    def _validate(dfs):
        if "Episodes" not in dfs:
            return {}
        else:
            epi = dfs["Episodes"]
            epi["DECOM"] = pd.to_datetime(
                epi["DECOM"], format="%d/%m/%Y", errors="coerce"
            )
            epi.reset_index(inplace=True)

            potent_cohort = epi[epi["PLACE"] == "T3"]

            # Here I'm after the CHILD ids where there are more than 2 T3 placements.
            count_them = (
                potent_cohort.groupby("CHILD")["CHILD"].count().to_frame(name="cc")
            )
            count_them.reset_index(inplace=True)
            count_them = count_them[count_them["cc"] > 2]

            err_coh = epi[epi["CHILD"].isin(count_them["CHILD"])]
            err_coh = err_coh[err_coh["PLACE"] == "T3"]

            err_list = err_coh["index"].unique().tolist()
            err_list.sort()
            return {"Episodes": err_list}

    return error, _validate


# !# Potential false negatives - if child has no missing periods in current year's Missing table nothing is flagged!


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {"CHILD": "111", "RNE": "P", "DECOM": "01/06/2020", "PLACE": "T3"},  # 0 ^
            {"CHILD": "111", "RNE": "P", "DECOM": "05/06/2020", "PLACE": "P3"},  # 1
            {"CHILD": "111", "RNE": "T", "DECOM": "06/06/2020", "PLACE": "T3"},  # 2
            {"CHILD": "111", "RNE": "B", "DECOM": "08/06/2020", "PLACE": "T3"},  # 3 v
            {"CHILD": "222", "RNE": "B", "DECOM": "05/06/2020", "PLACE": "T3"},  # 4 -
            {"CHILD": "333", "RNE": "B", "DECOM": "06/06/2020", "PLACE": "T3"},  # 5 ^
            {"CHILD": "333", "RNE": "U", "DECOM": "10/06/2020", "PLACE": "T3"},  # 6 v
            {"CHILD": "444", "RNE": "B", "DECOM": "07/06/2020", "PLACE": "T3"},  # 7 ^
            {"CHILD": "444", "RNE": "B", "DECOM": "08/06/2020", "PLACE": "oo"},  # 8
            {"CHILD": "444", "RNE": "T", "DECOM": "09/06/2020", "PLACE": "T3"},  # 9
            {"CHILD": "444", "RNE": "B", "DECOM": "15/06/2020", "PLACE": "T3"},  # 10 v
            {"CHILD": "6666", "RNE": "P", "DECOM": "11/06/2020", "PLACE": "oo"},  # 11 ^
            {"CHILD": "6666", "RNE": "P", "DECOM": "12/06/2020", "PLACE": "T3"},  # 12
            {"CHILD": "6666", "RNE": "P", "DECOM": "13/06/2020", "PLACE": "T3"},  # 13
            {"CHILD": "6666", "RNE": "P", "DECOM": "14/06/2020", "PLACE": "T3"},  # 14 v
        ]
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [0, 2, 3, 7, 9, 10, 12, 13, 14]}
