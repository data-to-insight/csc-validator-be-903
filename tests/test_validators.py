from validator903.validators import *
import pandas as pd

def test_validate_611():
    fake_data = pd.DataFrame({
        'MOTHER': [1, '1', pd.NA, pd.NA, 1 ], 
        'MC_DOB': ['01/01/2021', '19/02/2016', 'dd/mm/yyyy', '31/31/19', pd.NA],
    })

    fake_dfs = {'Header': fake_data}

    error_defn, error_func = validate_611()

    result = error_func(fake_dfs)

    assert result == {'Header': [4]}

def test_validate_1009():
    fake_data = pd.DataFrame({
        'REASON_PLACE_CHANGE': ['CARPL', 'OTHER', 'other', 'NA', '', pd.NA],
    })

    fake_dfs = {'Episodes': fake_data}
    
    error_defn, error_func = validate_1009()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [2, 3, 4]}

def test_validate_1006():
    fake_data = pd.DataFrame({
        'MISSING': ['M', 'A', 'AWAY', 'NA', '', pd.NA],
    })

    fake_dfs = {'Missing': fake_data}

    error_defn, error_func = validate_1006()

    result = error_func(fake_dfs)

    assert result == {'Missing': [2, 3, 4]}

def test_validate_631():
    fake_data = pd.DataFrame({
        'PREV_PERM': ['P0', 'P1', 'p1', '', pd.NA],
    })

    fake_dfs = {'PrevPerm': fake_data}

    error_defn, error_func = validate_631()

    result = error_func(fake_dfs)

    assert result == {'PrevPerm': [0, 2, 3]}

def test_validate_196():
    fake_data = pd.DataFrame({
        'SDQ_REASON': ['SDQ2', 'sdq2', '', pd.NA],
    })

    fake_dfs = {'OC2': fake_data}

    error_defn, error_func = validate_196()

    result = error_func(fake_dfs)

    assert result == {'OC2': [1, 2]}

def test_validate_177():
    fake_data = pd.DataFrame({
        'LS_ADOPTR': ['L0', 'L11', 'L1', 'l2', '', pd.NA],
    })

    fake_dfs = {'AD1': fake_data}

    error_defn, error_func = validate_177()

    result = error_func(fake_dfs)

    assert result == {'AD1': [2, 3, 4]}

def test_validate_176():
    fake_data = pd.DataFrame({
        'SEX_ADOPTR': ['m1', 'F1', 'MM', '1', '', pd.NA],
    })

    fake_dfs = {'AD1': fake_data}

    error_defn, error_func = validate_176()

    result = error_func(fake_dfs)

    assert result == {'AD1': [0, 3, 4]}

def test_validate_175():
    fake_data = pd.DataFrame({
        'NB_ADOPTR': [0, 1, 2, '1', '2', '0', '', pd.NA],
    })

    fake_dfs = {'AD1': fake_data}

    error_defn, error_func = validate_175()

    result = error_func(fake_dfs)

    assert result == {'AD1': [0, 5, 6]}

def test_validate_132():
    fake_data = pd.DataFrame({
        'ACTIV': ['f1', 'F1', 1, 0, '1', '0', '', pd.NA],
    })

    fake_dfs = {'OC3': fake_data}

    error_defn, error_func = validate_132()

    result = error_func(fake_dfs)

    assert result == {'OC3': [0, 2, 4, 6]}

def test_validate_131():
    fake_data = pd.DataFrame({
        'IN_TOUCH': ['yes', 'YES', 1, 'REFUSE', 'REFU', '', pd.NA],
    })

    fake_dfs = {'OC3': fake_data}

    error_defn, error_func = validate_131()

    result = error_func(fake_dfs)

    assert result == {'OC3': [0, 2, 3, 5]}

def test_validate_120():
    fake_data = pd.DataFrame({
        'REASON_PLACED_CEASED': ['rd1', 'RD0', 1, 'RD1', '', pd.NA],
    })

    fake_dfs = {'PlacedAdoption': fake_data}

    error_defn, error_func = validate_120()

    result = error_func(fake_dfs)

    assert result == {'PlacedAdoption': [0, 1, 2, 4]}

def test_validate_114():
    fake_data = pd.DataFrame({
        'FOSTER_CARE': [0, 1, '0', '1', 2, 'former foster carer', '', pd.NA],
    })

    fake_dfs = {'AD1': fake_data}

    error_defn, error_func = validate_114()

    result = error_func(fake_dfs)

    assert result == {'AD1': [4, 5, 6]}

def test_validate_178():
    fake_data = pd.DataFrame({
        'PLACE_PROVIDER': ['PR0', 'PR1',   '', pd.NA,   '', pd.NA],
        'PLACE':          ['U1',   'T0', 'U2',  'Z1', 'T1', pd.NA], 
    })

    fake_dfs = {'Episodes': fake_data}
    
    error_defn, error_func = validate_178()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [1, 2, 4]}

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

def test_validate_147():
    fake_data = pd.DataFrame({
        'DEC': ['01/01/2021', '19/02/2010', '38/04/2019', '01/01/19', pd.NA],
    })

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_147()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [2, 3]}

def test_validate_171():
    fake_data = pd.DataFrame({
        'MC_DOB': ['01/01/2021', '19/02/2010', '38/04/2019', '01/01/19', pd.NA],
    })

    fake_dfs = {'Header': fake_data}

    error_defn, error_func = validate_171()

    result = error_func(fake_dfs)

    assert result == {'Header': [2, 3]}

def test_validate_102():
    fake_data = pd.DataFrame({
        'DOB': ['01/01/2021', '19/02/2010', '38/04/2019', '01/01/19', pd.NA],
    })

    fake_dfs = {'Header': fake_data}

    error_defn, error_func = validate_102()

    result = error_func(fake_dfs)

    assert result == {'Header': [2, 3, 4]}

def test_validate_112():
    fake_data = pd.DataFrame({
        'DATE_INT': ['01/01/2021', '19/02/2010', '38/04/2019', '01/01/19', pd.NA],
    })

    fake_dfs = {'AD1': fake_data}

    error_defn, error_func = validate_112()

    result = error_func(fake_dfs)

    assert result == {'AD1': [2, 3]}

def test_validate_115():
    fake_data = pd.DataFrame({
        'DATE_PLACED': ['01/01/2021', '19/02/2010', '38/04/2019', '01/01/19', pd.NA],
    })

    fake_dfs = {'PlacedAdoption': fake_data}

    error_defn, error_func = validate_115()

    result = error_func(fake_dfs)

    assert result == {'PlacedAdoption': [2, 3]}

def test_validate_116():
    fake_data = pd.DataFrame({
        'DATE_PLACED_CEASED': ['01/01/2021', '19/02/2010', '38/04/2019', '01/01/19', pd.NA],
    })

    fake_dfs = {'PlacedAdoption': fake_data}

    error_defn, error_func = validate_116()

    result = error_func(fake_dfs)

    assert result == {'PlacedAdoption': [2, 3]}  

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

def test_validate_113():
    fake_data = pd.DataFrame({
        'DATE_MATCH': ['22/11/2015', '08/05/2010', '38/04/2019', '01/01/19', pd.NA],
    })

    fake_dfs = {'AD1': fake_data}

    error_defn, error_func = validate_113()

    result = error_func(fake_dfs)

    assert result == {'AD1': [2, 3]}

def test_validate_134():
    fake_data_oc3 = pd.DataFrame({
        'CHILD': ['A', 'B', 'C', 'D', 'E'],
        'IN_TOUCH': [pd.NA,'XXX',pd.NA,pd.NA,pd.NA],
        'ACTIV': [pd.NA,pd.NA,'XXX',pd.NA,pd.NA],
        'ACCOM': [pd.NA,pd.NA,pd.NA,'XXX',pd.NA],
    })
    fake_data_ad1 = pd.DataFrame({
        'CHILD': ['A', 'B', 'C', 'D', 'E'],
        'DATE_INT': [pd.NA,pd.NA,'XXX',pd.NA,'XXX'],
        'DATE_MATCH': [pd.NA,'XXX','XXX',pd.NA,'XXX'],
        'FOSTER_CARE': [pd.NA,pd.NA,'XXX',pd.NA,'XXX'],
        'NB_ADOPTR': [pd.NA,pd.NA,'XXX',pd.NA,'XXX'],
        'SEX_ADOPTR': [pd.NA,pd.NA,'XXX',pd.NA,'XXX'],
        'LS_ADOPTR': [pd.NA,pd.NA,'XXX','XXX','XXX'],
    }) 

    fake_dfs = {'OC3': fake_data_oc3, 'AD1': fake_data_ad1}

    error_defn, error_func = validate_134()

    result = error_func(fake_dfs)

    assert result == {'OC3': [1, 2, 3]}

def test_validate_119():
    fake_data = pd.DataFrame({
        'DATE_PLACED_CEASED': ['22/11/2015', '08/05/2010', pd.NA, pd.NA],
        'REASON_PLACED_CEASED': ['XXX',pd.NA, '10/05/2009', pd.NA]
    })

    fake_dfs = {'PlacedAdoption': fake_data}

    error_defn, error_func = validate_119()

    result = error_func(fake_dfs)

    assert result == {'PlacedAdoption': [1, 2]}

def test_validate_142():
    fake_data = pd.DataFrame([
    { 'CHILD' : '111', 'DECOM' : '01/06/2020', 'DEC' : '04/06/2020', 'REC': 'X1' },  #0
    { 'CHILD' : '111', 'DECOM' : '05/06/2020', 'DEC' : '06/06/2020', 'REC': pd.NA },  #1  Fails
    { 'CHILD' : '111', 'DECOM' : '06/06/2020', 'DEC' : '08/06/2020', 'REC': 'X1' },  #2
    { 'CHILD' : '111', 'DECOM' : '08/06/2020', 'DEC' : '05/06/2020', 'REC': 'X1' },  #3  
    { 'CHILD' : '222', 'DECOM' : '05/06/2020', 'DEC' : '06/06/2020', 'REC': pd.NA }, #4
    { 'CHILD' : '333', 'DECOM' : '06/06/2020', 'DEC' : pd.NA, 'REC': 'E11' },        #5   Fails      
    { 'CHILD' : '333', 'DECOM' : '07/06/2020', 'DEC' : pd.NA, 'REC': pd.NA },        #6
    { 'CHILD' : '444', 'DECOM' : '08/06/2020', 'DEC' : '09/06/2020', 'REC': 'X1' },  #7
    { 'CHILD' : '444', 'DECOM' : '09/06/2020', 'DEC' : '10/06/2020', 'REC': 'E11' }, #8
    { 'CHILD' : '444', 'DECOM' : '15/06/2020', 'DEC' : pd.NA, 'REC': pd.NA },        #9
    { 'CHILD' : '555', 'DECOM' : '11/06/2020', 'DEC' : '12/06/2020', 'REC': 'X1' },   #10  
    { 'CHILD' : '6666', 'DECOM' : '12/06/2020', 'DEC' : '13/06/2020', 'REC': 'X1' },  #11
    { 'CHILD' : '6666', 'DECOM' : '13/06/2020', 'DEC' : '14/06/2020', 'REC': 'X1' },  #12
    { 'CHILD' : '6666', 'DECOM' : '14/06/2020', 'DEC' : pd.NA, 'REC': 'X1' },         #13  Fails
    { 'CHILD' : '6666', 'DECOM' : '15/06/2020', 'DEC' : '16/06/2020', 'REC': 'X1' },  #14  
    { 'CHILD' : '77777', 'DECOM' : '16/06/2020', 'DEC' : '17/06/2020', 'REC': 'X1' }, #15
    { 'CHILD' : '77777', 'DECOM' : '17/06/2020', 'DEC' : '18/06/2020', 'REC': 'X1' }, #16
    { 'CHILD' : '77777', 'DECOM' : '18/06/2020', 'DEC' : pd.NA, 'REC': 'X1' },       #17  
    { 'CHILD' : '999', 'DECOM' : '31/06/2020', 'DEC' : pd.NA, 'REC': pd.NA },  #18   Nonsense date, but should pass
    { 'CHILD' : '123', 'DECOM' : pd.NA, 'DEC' : pd.NA, 'REC': pd.NA },  #19   Nonsense dates, but should pass
    { 'CHILD' : pd.NA, 'DECOM' : pd.NA, 'DEC' : pd.NA, 'REC': pd.NA },  #20   Nonsense, but should pass
    ])

    fake_dfs = {'Episode': fake_data}

    error_defn, error_func = validate_142()

    result = error_func(fake_dfs)

    assert result == {'Episode': [1,5,13]}

def test_validate_148():
    fake_data = pd.DataFrame([
    { 'CHILD' : '111', 'DECOM' : '01/06/2020', 'DEC' : '04/06/2020', 'REC': pd.NA },  #0  Fails
    { 'CHILD' : '111', 'DECOM' : '05/06/2020', 'DEC' : '06/06/2020', 'REC': 'X1' },  #1
    { 'CHILD' : '111', 'DECOM' : '06/06/2020', 'DEC' : pd.NA, 'REC': 'X1' },         #2   Fails
    { 'CHILD' : '111', 'DECOM' : '08/06/2020', 'DEC' : '05/06/2020', 'REC': 'X1' },  #3
    { 'CHILD' : '222', 'DECOM' : '05/06/2020', 'DEC' : '06/06/2020', 'REC': pd.NA }, #4   Fails
    { 'CHILD' : '333', 'DECOM' : '06/06/2020', 'DEC' : '07/06/2020', 'REC': 'E11' }, #5  
    { 'CHILD' : '333', 'DECOM' : '07/06/2020', 'DEC' : pd.NA, 'REC': pd.NA },        #6
    { 'CHILD' : '444', 'DECOM' : '08/06/2020', 'DEC' : '09/06/2020', 'REC': 'X1' },  #7
    { 'CHILD' : '444', 'DECOM' : '09/06/2020', 'DEC' : '10/06/2020', 'REC': 'E11' }, #8
    { 'CHILD' : '444', 'DECOM' : '15/06/2020', 'DEC' : pd.NA, 'REC': pd.NA },        #9
    ])

    fake_dfs = {'Episode': fake_data}

    error_defn, error_func = validate_148()

    result = error_func(fake_dfs)

    assert result == {'Episode': [0,2,4]}

def test_validate_214():
    fake_data = pd.DataFrame([
   { 'LS' : 'V3', 'PL_POST' : 'M2 3RT', 'URN' : 'XXXXXX'},    #0  Fail
   { 'LS' : 'U1', 'PL_POST' : 'M2 3RT', 'URN' : 'SC045099'},  #1
   { 'LS' : 'U3', 'PL_POST' : pd.NA, 'URN' : 'SC045099'},     #2
   { 'LS' : 'V4', 'PL_POST' : 'M2 3RT', 'URN' : pd.NA},       #3  Fail
   { 'LS' : 'V4', 'PL_POST' : pd.NA, 'URN' : 'SC045099'},     #4  Fail
   { 'LS' : 'T1', 'PL_POST' : 'M2 3RT', 'URN' : 'SC045100'},  #5
   { 'LS' : 'U6', 'PL_POST' : 'M2 3RT', 'URN' : 'SC045101'},  #6
   { 'LS' : 'V3', 'PL_POST' : pd.NA, 'URN' : pd.NA},          #7 
  ])

    fake_dfs = {'Episode': fake_data}

    error_defn, error_func = validate_214()

    result = error_func(fake_dfs)

    assert result == {'Episode': [0,3,4]}

def test_validate_222():
    fake_data = pd.DataFrame([
    { 'PLACE' : 'H5', 'URN' : 'XXXXXX'},  #0
    { 'PLACE' : 'U1', 'URN' : 'Whatever'},  #1
    { 'PLACE' : 'U2', 'URN' : pd.NA},  #2
    { 'PLACE' : 'T1', 'URN' : pd.NA},  #3
    { 'PLACE' : 'R1', 'URN' : 'Whatever'},  #4  Fail
    { 'PLACE' : 'T2', 'URN' : 'Whatever'},  #5  Fail
  ])

    fake_dfs = {'Episode': fake_data}

    error_defn, error_func = validate_222()

    result = error_func(fake_dfs)

    assert result == {'Episode': [4,5]}

def test_validate_366():
    fake_data = pd.DataFrame([
    { 'LS' : 'V3', 'RNE' : 'S'},  #0
    { 'LS' : 'V4', 'RNE' : 'T'},  #1
    { 'LS' : 'U1', 'RNE' : pd.NA},  #2
    { 'LS' : 'U2', 'RNE' : pd.NA},  #3
    { 'LS' : 'V3', 'RNE' : 'U'},  #4  Fail
    { 'LS' : 'V3', 'RNE' : pd.NA},  #5  Fail
  ])

    fake_dfs = {'Episode': fake_data}

    error_defn, error_func = validate_366()

    result = error_func(fake_dfs)

    assert result == {'Episode': [4,5]}