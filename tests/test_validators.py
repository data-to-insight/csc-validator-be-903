from validator903.validators import *
import pandas as pd

def test_validate_143():
    fake_data = pd.DataFrame({
        'RNE': ['S', 'p', 'SP', 'a', '', pd.NA],
    })

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_143()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [1, 2, 3, 4]}

def test_validate_145():
    fake_data = pd.DataFrame({
        'CIN': ['N0', 'N1', 'N9', 'n8', '', pd.NA],
    })

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_145()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [0, 2, 3, 4]}

def test_validate_144():
    fake_data = pd.DataFrame({
        'LS': ['C1', 'c1', 'section 20', '', pd.NA],
    })

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_144()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [1, 2, 3]}
    
def test_validate_146():
    fake_data = pd.DataFrame({
        'PLACE': ['A2', 'R4', 'Z', 'P1', '', 't3', pd.NA],
    })

    fake_dfs = {'Episodes': fake_data}
    
    error_defn, error_func = validate_146()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [0, 1, 2, 4, 5]}
  
def test_validate_149():
    fake_data = pd.DataFrame({
        'REC': ['E4A', 'E4b', 'X', '', pd.NA],
    })

    fake_dfs = {'Episodes': fake_data}
    
    error_defn, error_func = validate_149()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [1, 2, 3]}
     
def test_validate_167():
    fake_data = pd.DataFrame({
        'REVIEW': ['01/02/2020', '31/03/2020', '12/12/2019', '05/07/2020', pd.NA],
        'REVIEW_CODE': ['p0', 'child too young', 'PN3', '', pd.NA],
    })

    fake_dfs = {'Reviews': fake_data}
    
    error_defn, error_func = validate_167()

    result = error_func(fake_dfs)

    assert result == {'Reviews': [0, 1, 3]}

def test_validate_103():
    fake_data = pd.DataFrame({
        'ETHNIC': ['WBRI', 'WIRI', 'WOTH', 'wbri', 'White British', '', pd.NA],
    })

    fake_dfs = {'Header': fake_data}

    error_defn, error_func = validate_103()

    result = error_func(fake_dfs)

    assert result == {'Header': [3, 4, 5, 6]}

def test_validate_101():
    fake_data = pd.DataFrame({
        'SEX': [1, 2, 3, pd.NA],
    })

    fake_dfs = {'Header': fake_data}

    error_defn, error_func = validate_101()

    result = error_func(fake_dfs)

    assert result == {'Header': [2, 3]}

def test_validate_141():
    fake_data = pd.DataFrame({
        'DECOM': ['01/01/2021', '19/02/2010', '38/04/2019', '01/01/19', pd.NA],
    })

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_141()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [2, 3]}

def test_validate_102():
    fake_data = pd.DataFrame({
        'DOB': ['01/01/2021', '19/02/2010', '38/04/2019', '01/01/19', pd.NA],
    })

    fake_dfs = {'Header': fake_data}

    error_defn, error_func = validate_102()

    result = error_func(fake_dfs)

    assert result == {'Header': [2, 3, 4]}

def test_validate_392c(dummy_postcodes):
    fake_data = pd.DataFrame({
        'HOME_POST': [
            'AB1 0JD',
            'invalid',
            'AB1 0JD',
            'invalid',
            'AB10JD',
        ],
        'PL_POST': [
            'AB1 0JD',
            'AB1 0JD',
            'invalid',
            'invalid',
            'AB1 0JD',
        ],
    })

    fake_dfs = {'Episodes': fake_data, 'metadata': {'postcodes': dummy_postcodes}}

    error_defn, error_func = validate_392c()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [1, 2, 3]}

def test_validate_213():
    fake_data = pd.DataFrame({
        'PLACE': ['T0','U6','U1','U4','P1','T2','T3', pd.NA],
        'PLACE_PROVIDER': [pd.NA , pd.NA,'PR3','PR4','PR0','PR2','PR1', pd.NA],
    })

    fake_dfs = {'Episode': fake_data}

    error_defn, error_func = validate_213()

    result = error_func(fake_dfs)

    assert result == {'Episode': [5,6]}

def test_validate_168():
    fake_data = pd.DataFrame({
        'UPN' : ['UN3','E07295962325C1556','UN5','UN7','UPN3sDSG','X06805040829A','5035247309594',pd.NA,'L086819786126','K06014812931','J000947841350156','M0940709','I072272729588',
                 'N075491517151','Z041674136429','E043016488226','S074885779408'],
    })

    fake_dfs = {'Header': fake_data}

    error_defn, error_func = validate_168()

    result = error_func(fake_dfs)

    assert result == {'Header': [1,3,4,6,7,9,10,11,12,16]}

def test_validate_388():
    fake_data = pd.DataFrame([
    { 'CHILD' : '111', 'DECOM' : '01/06/2020', 'DEC' : '04/06/2020', 'REC': 'X1' },  #0  Fails Case 1
    { 'CHILD' : '111', 'DECOM' : '05/06/2020', 'DEC' : '06/06/2020', 'REC': 'X1' },  #1
    { 'CHILD' : '111', 'DECOM' : '06/06/2020', 'DEC' : '08/06/2020', 'REC': 'X1' },  #2
    { 'CHILD' : '111', 'DECOM' : '08/06/2020', 'DEC' : '05/06/2020', 'REC': 'X1' },  #3  Fails Case 3
    { 'CHILD' : '222', 'DECOM' : '05/06/2020', 'DEC' : '06/06/2020', 'REC': pd.NA }, #4
    { 'CHILD' : '333', 'DECOM' : '06/06/2020', 'DEC' : '07/06/2020', 'REC': 'E11' }, #5  Fails Case 2
    { 'CHILD' : '333', 'DECOM' : '07/06/2020', 'DEC' : pd.NA, 'REC': pd.NA },        #6
    { 'CHILD' : '444', 'DECOM' : '08/06/2020', 'DEC' : '09/06/2020', 'REC': 'X1' },  #7
    { 'CHILD' : '444', 'DECOM' : '09/06/2020', 'DEC' : '10/06/2020', 'REC': 'E11' }, #8
    { 'CHILD' : '444', 'DECOM' : '15/06/2020', 'DEC' : pd.NA, 'REC': pd.NA },        #9
    { 'CHILD' : '555', 'DECOM' : '11/06/2020', 'DEC' : '12/06/2020', 'REC': 'X1' },   #10  Fails Case 3
    { 'CHILD' : '6666', 'DECOM' : '12/06/2020', 'DEC' : '13/06/2020', 'REC': 'X1' },  #11
    { 'CHILD' : '6666', 'DECOM' : '13/06/2020', 'DEC' : '14/06/2020', 'REC': 'X1' },  #12
    { 'CHILD' : '6666', 'DECOM' : '14/06/2020', 'DEC' : '15/06/2020', 'REC': 'X1' },  #13
    { 'CHILD' : '6666', 'DECOM' : '15/06/2020', 'DEC' : '16/06/2020', 'REC': 'X1' },  #14  Fails Case 3
    { 'CHILD' : '77777', 'DECOM' : '16/06/2020', 'DEC' : '17/06/2020', 'REC': 'X1' }, #15
    { 'CHILD' : '77777', 'DECOM' : '17/06/2020', 'DEC' : '18/06/2020', 'REC': 'X1' }, #16
    { 'CHILD' : '77777', 'DECOM' : '18/06/2020', 'DEC' : pd.NA, 'REC': pd.NA },       #17
    { 'CHILD' : '999', 'DECOM' : '31/06/2020', 'DEC' : pd.NA, 'REC': pd.NA },  #18   Nonsense date, but should pass
    { 'CHILD' : '123', 'DECOM' : pd.NA, 'DEC' : pd.NA, 'REC': pd.NA },  #19   Nonsense dates, but should pass
    { 'CHILD' : pd.NA, 'DECOM' : pd.NA, 'DEC' : pd.NA, 'REC': pd.NA },  #20   Nonsense, but should pass
    ])

    fake_dfs = {'Episode': fake_data}

    error_defn, error_func = validate_388()

    result = error_func(fake_dfs)

    assert result == {'Episode': [0,3,5,10,14]}
