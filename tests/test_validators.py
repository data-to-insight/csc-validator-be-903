from validator903.validators import *
import pandas as pd

def test_validate_202():
    fake_data = pd.DataFrame({
        'CHILD':['101','102','103','104','105','106','108','109','110'],
        'SEX':['1',2,'1','2',pd.NA,'1',pd.NA,'2','3'],
    })

    fake_data_prev = pd.DataFrame({
        'CHILD':['101','102','103','104','105','107','108','109','110'],
        'SEX':['1',1,'2',2,pd.NA,'1','2',pd.NA,'2'],
    })

    fake_dfs = {'Header': fake_data, 'Header_last': fake_data_prev}

    error_defn, error_func = validate_202()

    result = error_func(fake_dfs)

    assert result == {'Header': [1,2,6,7,8]}

def test_validate_621():
    fake_data = pd.DataFrame({
        'DOB': ['01/12/2021', '19/02/2016', '31/01/2019',  '31/01/2019', '31/01/2019'],
        'MC_DOB': ['01/01/2021', '19/12/2016',  '31/01/2019', pd.NA, '01/02/2019'],
    })

    fake_dfs = {'Header': fake_data}

    error_defn, error_func = validate_621()

    result = error_func(fake_dfs)

    assert result == {'Header': [0, 2]}

def test_validate_556():
    fake_data_episodes = pd.DataFrame({
        'CHILD': ['A', 'B', 'C'],
        'LS': ['C1', 'D1', 'D1'],
        'DECOM': [pd.NA, '15/03/2020', '15/03/2020'],
    })
    fake_data_placed_adoption = pd.DataFrame({
        'CHILD': ['A', 'B', 'C'],
        'DATE_PLACED': [pd.NA, '15/04/2020', '15/02/2020'],
    }) 

    fake_dfs = {'Episodes': fake_data_episodes, 'PlacedAdoption': fake_data_placed_adoption}

    error_defn, error_func = validate_556()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [1]}

def test_validate_393():
    fake_data = pd.DataFrame({
        'CHILD':['101','102','103','104','105'],
        'SEX':['2','1','2','2','2'],
        'MOTHER':['1',pd.NA,'0',pd.NA,pd.NA],
    })

    fake_data_episodes = pd.DataFrame({
        'CHILD':['101','102','103','104','105'],
        'LS':['C2','C2','c2','C1','v4']
    })

    fake_dfs = {'Header': fake_data, 'Episodes': fake_data_episodes}

    error_defn, error_func = validate_393()

    result = error_func(fake_dfs)

    assert result == {'Header': [3]} 

def test_validate_NoE():
    fake_data = pd.DataFrame({
        'CHILD':['101','102','103'],
        'DECOM':['14/03/2021','08/09/2021','03/10/2020'],
    })

    fake_data_prev = pd.DataFrame({
        'CHILD':['101','102'],
        'DECOM':['14/03/2021','16/06/2019']
    })

    metadata = { 
        'collection_start': '01/04/2021'
    }
    
    fake_dfs = {'Episodes': fake_data, 'Episodes_last': fake_data_prev, 'metadata': metadata}

    error_defn, error_func = validate_NoE()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [2]}

def test_validate_356():
    fake_data = pd.DataFrame({
        'DECOM':['14/03/2021', '16/06/2019', '03/10/2020', '07/09/2021'],
        'DEC': ['08/12/2020', '24/08/2021', pd.NA, '07/09/2021'],
    })

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_356()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [0]}


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

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_213()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [5,6]}

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

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_388()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [0,3,5,10,14]}

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

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_142()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [1,5,13]}

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

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_148()

    result = error_func(fake_dfs)
    
    assert result == {'Episodes': [0,2,4]}

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

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_214()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [0,3,4]}

def test_validate_222():
    fake_data = pd.DataFrame([
    { 'PLACE' : 'H5', 'URN' : 'XXXXXX'},  #0
    { 'PLACE' : 'U1', 'URN' : 'Whatever'},  #1
    { 'PLACE' : 'U2', 'URN' : pd.NA},  #2
    { 'PLACE' : 'T1', 'URN' : pd.NA},  #3
    { 'PLACE' : 'R1', 'URN' : 'Whatever'},  #4  Fail
    { 'PLACE' : 'T2', 'URN' : 'Whatever'},  #5  Fail
  ])

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_222()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [4,5]}

def test_validate_366():
    fake_data = pd.DataFrame([
    { 'LS' : 'V3', 'RNE' : 'S'},  #0
    { 'LS' : 'V4', 'RNE' : 'T'},  #1
    { 'LS' : 'U1', 'RNE' : pd.NA},  #2
    { 'LS' : 'U2', 'RNE' : pd.NA},  #3
    { 'LS' : 'V3', 'RNE' : 'U'},  #4  Fail
    { 'LS' : 'V3', 'RNE' : pd.NA},  #5  Fail
  ])

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_366()

    result = error_func(fake_dfs)
    
    assert result == {'Episodes': [4,5]}

def test_validate_628():
    fake_data_hea = pd.DataFrame({
        'CHILD': ['0','1','2','3','4','5','6'],
        'MOTHER': [1,pd.NA,0,1,0,1,1],   #1 will pass as null
    })
    fake_data_epi = pd.DataFrame({
        'CHILD': ['a','1','3','3','3','4','5'],   #So 0, 2 and 6 are the ones not in episodes
    }) 
    fake_data_oc3 = pd.DataFrame([
        {'CHILD': '0', 'IN_TOUCH': 'Whatever', 'ACTIV': pd.NA, 'ACCOM': 'Whatever'}, 
        {'CHILD': '2', 'IN_TOUCH': pd.NA, 'ACTIV': pd.NA, 'ACCOM': pd.NA},     #All null values so 2 will pass
        {'CHILD': '6', 'IN_TOUCH': 'Whatever', 'ACTIV': pd.NA, 'ACCOM': pd.NA}, 
        {'CHILD': '5', 'IN_TOUCH': 'Whatever', 'ACTIV': pd.NA, 'ACCOM': pd.NA}, 
    ])
    fake_dfs = {'Header': fake_data_hea, 'Episodes' : fake_data_epi, 'OC3' : fake_data_oc3}

    error_defn, error_func = validate_628()

    result = error_func(fake_dfs)

    assert result == {'Header': [0,6]}

def test_validate_182():
    fake_data = pd.DataFrame({
        'IMMUNISATIONS':           [pd.NA, pd.NA, pd.NA, '1'  , pd.NA, '1'  , pd.NA, '1'  ],
        'TEETH_CHECK':            [pd.NA, pd.NA, pd.NA, '1'  , pd.NA, '1'  , '1'  , '1'  ],
        'HEALTH_ASSESSMENT':      [pd.NA, pd.NA, pd.NA, '1'  , pd.NA, '1'  , pd.NA, '1'  ],
        'SUBSTANCE_MISUSE':       [pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, '1'  , '1'  , '1'  ],
        'CONVICTED':              [pd.NA, '1'  , pd.NA, pd.NA, pd.NA, '1'  , '1'  , pd.NA],
        'HEALTH_CHECK':           [pd.NA, pd.NA, '1'  , pd.NA, pd.NA, '1'  , '1'  , pd.NA],
        'INTERVENTION_RECEIVED':  [pd.NA, pd.NA, pd.NA, '1'  , pd.NA, '1'  , '1'  , pd.NA],
        'INTERVENTION_OFFERED':   [pd.NA, pd.NA, pd.NA, pd.NA, '1'  , '1'  , '1'  , pd.NA],
    }) 

    fake_dfs = {'OC2': fake_data}

    error_defn, error_func = validate_182()

    result = error_func(fake_dfs)

    assert result == {'OC2': [1, 2, 3, 4, 6]}

def test_validate_164():
    fake_data = pd.DataFrame({
        'LS': ['C2', 'C2', 'C2', 'C2', 'V3', 'V4', 'C2'],
        'PL_DISTANCE': [12.0, '12', 1003.0, pd.NA, pd.NA, pd.NA, 0.0],
    })

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_164()

    assert error_func(fake_dfs) == {'Episodes': [2, 3]}

def test_validate_169():
    fake_data = pd.DataFrame({
        'LS': ['C2', 'C2', 'C2', 'V3', 'V4'],
        'PL_LA': ['NIR', 'E03934134', pd.NA, pd.NA, pd.NA,]
    })

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_169()

    assert error_func(fake_dfs) == {'Episodes': [2]}

def test_validate_179():
    fake_data = pd.DataFrame({
        'LS': ['C2', 'C2', 'C2', 'V3', 'V4'],
        'PL_LOCATION': ['IN', 'OUT', pd.NA, pd.NA, pd.NA,]
    })

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_179()

    assert error_func(fake_dfs) == {'Episodes': [2]}

def test_validate_1015():
    fake_data = pd.DataFrame([
        {'PLACE': 'E1', 'LS': 'C1', 'PLACE_PROVIDER': 'PR1', 'PL_LA': 'auth'},
        {'PLACE': 'E1', 'LS': 'C1', 'PLACE_PROVIDER': 'PR1', 'PL_LA': 'other'},
        {'PLACE': 'U2', 'LS': 'C1', 'PLACE_PROVIDER': 'PR1', 'PL_LA': 'other'},
        {'PLACE': 'E1', 'LS': 'V3', 'PLACE_PROVIDER': 'PR1', 'PL_LA': 'other'},
        {'PLACE': 'E1', 'LS': 'C1', 'PLACE_PROVIDER': 'PR2', 'PL_LA': 'other'},
        {'PLACE': pd.NA, 'LS': 'C1', 'PLACE_PROVIDER': 'PR1', 'PL_LA': 'other'},
        {'PLACE': 'E1', 'LS': pd.NA, 'PLACE_PROVIDER': 'PR1', 'PL_LA': 'other'},
        {'PLACE': 'E1', 'LS': 'C1', 'PLACE_PROVIDER': pd.NA, 'PL_LA': 'other'},
    ])

    metadata = {
        'localAuthority': 'auth',
    }
    
    fake_dfs = {'Episodes': fake_data, 'metadata': metadata}

    error_defn, error_func = validate_1015()
    assert error_func(fake_dfs) == {'Episodes': [1]}

def test_validate_411():
    fake_data = pd.DataFrame({
        'PL_LA': ['auth', 'somewhere else', 'auth', 'auth', 'somewhere else'],
        'PL_LOCATION': ['IN', 'OUT', pd.NA, 'OUT', 'IN']
    })

    fake_dfs = {'Episodes': fake_data, 'metadata': {'localAuthority': 'auth'}}

    error_defn, error_func = validate_411()

    # Note 2 and 3 pass as the rule is specific 
    # about only checking that 'IN' is set correctly
    assert error_func(fake_dfs) == {'Episodes': [4]}

def test_validate_420():
    fake_data = pd.DataFrame({
        'LS': ['C2', 'V3', 'V4', 'V3', 'V4', 'C2'],
        'PL_LA': [pd.NA, 'E03934134', 'E059635', pd.NA, pd.NA, 'NIR']
    })

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_420()

    assert error_func(fake_dfs) == {'Episodes': [1, 2]}

def test_validate_355():
    fake_data = pd.DataFrame({
        'DECOM': ['01/01/2000', '01/02/2000', '01/03/2000', '01/04/2000', '01/05/2000', '01/06/2000' ,'04/05/2000'],
        'DEC': ['01/01/2000',   '01/03/2000',    pd.NA,     '01/04/2000', '03/05/2000', '01/06/2000' ,'01/05/2000'],
    })

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_355()

    assert error_func(fake_dfs) == {'Episodes': [0, 3, 5]}

def test_validate_586():
    fake_data = pd.DataFrame([
        {'DOB' : '01/02/2020', 'MIS_START' : pd.NA },        #0
        {'DOB' : '02/02/2020', 'MIS_START' : '07/02/2020'},  #1
        {'DOB' : '04/02/2020', 'MIS_START' : '03/02/2020'},  #2  Fails
        {'DOB' : '06/02/2020', 'MIS_START' : pd.NA },        #3
        {'DOB' : '07/02/2020', 'MIS_START' : '01/02/2020'},  #4  Fails
        {'DOB' : '08/02/2020', 'MIS_START' : '13/02/2020'},  #5
    ])

    fake_dfs = {'Missing': fake_data}

    error_defn, error_func = validate_586()

    assert error_func(fake_dfs) == {'Missing': [2, 4]}

def test_validate_630():
    fake_epi = pd.DataFrame({
        'CHILD': ['0', '1', '2', '3', '4', '5' ,'6', '7', '8'],
        'DECOM': ['01/04/2021','01/04/2021','01/04/2021','01/04/2021','31/03/2021','01/04/2021','01/04/2021','01/04/2021','01/04/2021'], 
        #4 will now pass, it's before this year
        'RNE': [  'T', 'S', 'S', 'P', 'S', 'S', 'S', 'S', 'S'],
    })
    fake_pre = pd.DataFrame({
        'CHILD':      ['2',   '4', '5' ,          '6',  '7' , '8'],
        'PREV_PERM': [ 'Z1', 'P1', 'P1',         'Z1',  pd.NA,'P1'],
        'LA_PERM':   [pd.NA, '352', pd.NA,       pd.NA, pd.NA,'352'],
        'DATE_PERM': [pd.NA, pd.NA,'01/05/2000', pd.NA, pd.NA,'05/05/2020'],
    })
    metadata = { 'collection_start': '01/04/2021' }

    fake_dfs = {'Episodes': fake_epi, 'PrevPerm': fake_pre, 'metadata': metadata}

    error_defn, error_func = validate_630()

    assert error_func(fake_dfs) == {'Episodes': [1, 5, 7]}
    

def test_validate_501():
    fake_data = pd.DataFrame([
    { 'CHILD' : '111', 'DECOM' : '01/06/2020', 'DEC' : '04/06/2020' },  #0  
    { 'CHILD' : '111', 'DECOM' : '02/06/2020', 'DEC' : '06/06/2020' },  #1   Fails
    { 'CHILD' : '111', 'DECOM' : '06/06/2020', 'DEC' : pd.NA  },        #2   
    { 'CHILD' : '111', 'DECOM' : '08/06/2020', 'DEC' : '09/06/2020' },  #3
    { 'CHILD' : '222', 'DECOM' : '10/06/2020', 'DEC' : '11/06/2020' },  #4   
    { 'CHILD' : '333', 'DECOM' : '04/06/2020', 'DEC' : '07/06/2020' }, #5  
    { 'CHILD' : '333', 'DECOM' : '05/06/2020', 'DEC' : pd.NA  },        #6   Fails
    { 'CHILD' : '444', 'DECOM' : '08/06/2020', 'DEC' : '09/06/2020'},  #7
    { 'CHILD' : '444', 'DECOM' : '08/06/2020', 'DEC' : '10/06/2020'  }, #8   Fails
    { 'CHILD' : '444', 'DECOM' : '15/06/2020', 'DEC' : pd.NA },        #9
    ])

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_501()

    result = error_func(fake_dfs)
    
    assert result == {'Episodes': [1,6,8]}

def test_validate_502():
    fake_epi = pd.DataFrame([
    { 'CHILD' : '111', 'DECOM' : '01/06/2020' },  #0  Min   Fails
    { 'CHILD' : '111', 'DECOM' : '05/06/2020' },  #1
    { 'CHILD' : '111', 'DECOM' : '06/06/2020' },  #2   
    { 'CHILD' : '123', 'DECOM' : '08/06/2020' },  #3  Min
    { 'CHILD' : '222', 'DECOM' : '05/06/2020' }, #4   Min   Fails
    { 'CHILD' : '333', 'DECOM' : '06/06/2020' }, #5  Min
    { 'CHILD' : '333', 'DECOM' : '07/06/2020' }, #6
    { 'CHILD' : '444', 'DECOM' : '08/06/2020' }, #7  Min   Fails 
    { 'CHILD' : '444', 'DECOM' : '09/06/2020' }, #8
    { 'CHILD' : '444', 'DECOM' : '15/06/2020' }, #9
    { 'CHILD' : '555', 'DECOM' : '15/06/2020' }, #10
    ])

    fake_epi_last = pd.DataFrame([
    { 'CHILD' : '111', 'DECOM' : '05/06/2020', 'DEC' : pd.NA },  
    { 'CHILD' : '123', 'DECOM' : '08/06/2020', 'DEC' : pd.NA },
    { 'CHILD' : '222', 'DECOM' : '09/06/2020', 'DEC' : pd.NA }, 
    { 'CHILD' : '333', 'DECOM' : '06/06/2020', 'DEC' : '05/06/2020' }, 
    { 'CHILD' : '333', 'DECOM' : '07/06/2020', 'DEC' : '05/06/2020' },
    { 'CHILD' : '444', 'DECOM' : '08/06/2020', 'DEC' : '05/06/2020' }, 
    { 'CHILD' : '444', 'DECOM' : '09/06/2020', 'DEC' : '05/06/2020' }, 
    { 'CHILD' : '444', 'DECOM' : '19/06/2020', 'DEC' : pd.NA }, 
    ])

    fake_dfs = {'Episodes': fake_epi, 'Episodes_last': fake_epi_last}

    error_defn, error_func = validate_502()

    result = error_func(fake_dfs)
    
    assert result == {'Episodes': [0,4,7]}

def test_validate_567():
    fake_mis = pd.DataFrame([
    { 'MIS_START' : '01/06/2020', 'MIS_END' : '05/06/2020' }, #0  
    { 'MIS_START' : '02/06/2020', 'MIS_END' : pd.NA },        #1
    { 'MIS_START' : '03/06/2020', 'MIS_END' : '01/06/2020' }, #2 Fails
    { 'MIS_START' : '04/06/2020', 'MIS_END' : '02/06/2020' }, #3 Fails
    { 'MIS_START' : pd.NA,        'MIS_END' : '05/06/2020' }, #4  
    ])

    fake_dfs = {'Missing': fake_mis}

    error_defn, error_func = validate_567()

    result = error_func(fake_dfs)
    
    assert result == {'Missing': [2,3]}

def test_validate_304():
    fake_uasc = pd.DataFrame([
    { 'DOB' : '01/06/2000', 'DUC' : '05/06/2019' }, #0 Fails 
    { 'DOB' : '02/06/2000', 'DUC' : pd.NA },        #1
    { 'DOB' : '03/06/2000', 'DUC' : '01/06/2015' }, #2
    { 'DOB' : '04/06/2000', 'DUC' : '02/06/2020' }, #3 Fails
    { 'DOB' : pd.NA,        'DUC' : '05/06/2020' }, #4  
    ])

    fake_dfs = {'UASC': fake_uasc}

    error_defn, error_func = validate_304()

    result = error_func(fake_dfs)
    
    assert result == {'UASC': [0,3]}
