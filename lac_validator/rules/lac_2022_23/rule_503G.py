def test_validate():
    error_defn, error_func = validate()

    result = error_func(fake_dfs__452_453_503G_503H)

    assert result == {"Episodes": [4]}


# -------------------------------
