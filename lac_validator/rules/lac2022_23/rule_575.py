import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="575",
    message="If the placement from which the child goes missing/away from placement without "
    + "authorisation ends, the missing/away from placement without authorisation period in "
    + "the missing module must also have an end date.",
    affected_fields=["MIS_END"],
    tables=["Episodes", "Missing"],
)
def validate(dfs):
    if "Episodes" not in dfs or "Missing" not in dfs:
        return {}
    else:
        epi = dfs["Episodes"]
        mis = dfs["Missing"]

        mis.reset_index(inplace=True)

        epi["DECOM"] = pd.to_datetime(epi["DECOM"], format="%d/%m/%Y", errors="coerce")
        epi["DEC"] = pd.to_datetime(epi["DEC"], format="%d/%m/%Y", errors="coerce")
        mis["MIS_START"] = pd.to_datetime(
            mis["MIS_START"], format="%d/%m/%Y", errors="coerce"
        )

        m_coh = epi.merge(mis, how="inner", on="CHILD").query(
            "(MIS_START >= DECOM) & (MIS_START <= DEC) & MIS_END.isnull() & DEC.notnull()"
        )

        err_list = m_coh["index"].unique().tolist()
        err_list.sort()
        return {"Missing": err_list}

        return {"Episodes": Episodes_errs, "AD1": AD1_errs}


def test_validate():
    import pandas as pd

    fake_epi = pd.DataFrame(
        [
            {"CHILD": "111", "DECOM": "01/06/2020", "DEC": "10/06/2020"},  # 0
            {"CHILD": "123", "DECOM": "08/06/2020", "DEC": "10/06/2020"},  # 1
            {"CHILD": "222", "DECOM": "05/06/2020", "DEC": "10/06/2020"},  # 2
            {"CHILD": "333", "DECOM": "06/06/2020", "DEC": pd.NA},  # 3
            {"CHILD": "333", "DECOM": "07/06/2020", "DEC": "10/06/2020"},  # 4
            {"CHILD": "444", "DECOM": "08/06/2020", "DEC": "10/06/2020"},  # 5
            {"CHILD": "444", "DECOM": "08/06/2020", "DEC": pd.NA},  # 6
        ]
    )

    fake_mis = pd.DataFrame(
        [
            {"CHILD": "111", "MIS_START": "01/06/2020", "MIS_END": "05/06/2020"},  # 0
            {"CHILD": "123", "MIS_START": "08/06/2020", "MIS_END": pd.NA},  # 1 Fail
            {"CHILD": "222", "MIS_START": "05/06/2020", "MIS_END": "05/06/2020"},  # 2
            {"CHILD": "333", "MIS_START": "06/06/2020", "MIS_END": pd.NA},  # 3
            {"CHILD": "444", "MIS_START": "08/06/2020", "MIS_END": "05/06/2020"},  # 4
            {"CHILD": "444", "MIS_START": "09/06/2020", "MIS_END": pd.NA},  # 5 Fail
            {"CHILD": "444", "MIS_START": "19/06/2020", "MIS_END": "05/06/2020"},  # 6
        ]
    )

    fake_dfs = {"Episodes": fake_epi, "Missing": fake_mis}

    result = validate(fake_dfs)

    assert result == {"Missing": [1, 5]}
