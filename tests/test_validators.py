from validator903.validators import *
import pandas as pd


# Tests for 205A-205D all use these dataframes:

fake_uasc_205 = pd.DataFrame([
    {'CHILD': '101', 'DOB': '28/10/2004', 'DUC': pd.NA},#Pass C
    {'CHILD': '102', 'DOB': '04/06/2004', 'DUC': pd.NA},#Pass A
    {'CHILD': '103', 'DOB': '03/03/2002', 'DUC': '10/07/2020'},#Fail A
    {'CHILD': '104', 'DOB': '28/03/2003', 'DUC': '14/05/2021'},#Fail A
    {'CHILD': '105', 'DOB': '16/04/2001', 'DUC': '16/04/2019'},#Fail B
    {'CHILD': '106', 'DOB': '04/11/2004', 'DUC': '16/06/2021'},#Fail B
    {'CHILD': '107', 'DOB': '23/07/2002', 'DUC': '23/07/2020'},#Pass B
    {'CHILD': '108', 'DOB': '19/02/2003', 'DUC': pd.NA},#Fail C
    {'CHILD': '109', 'DOB': '14/06/2003', 'DUC': '14/06/2021'},#Fail D
    {'CHILD': '110', 'DOB': '14/06/2003', 'DUC': pd.NA},  # Fail D
])

fake_uasc_prev_205 = pd.DataFrame([
    {'CHILD': '101', 'DOB': '28/10/2004', 'DUC': pd.NA},#Pass C
    {'CHILD': '102', 'DOB': '04/06/2004', 'DUC': '20/01/2020'},#Pass A
    {'CHILD': '103', 'DOB': '03/03/2002', 'DUC': '10/07/2020'},#Fail A
    {'CHILD': '104', 'DOB': '28/03/2003', 'DUC': '14/05/2021'},#Fail A
    {'CHILD': '105', 'DOB': '16/04/2001', 'DUC': '16/04/2019'},#Fail B
    {'CHILD': '106', 'DOB': '04/11/2004', 'DUC': '04/11/2023'},#Fail B
    {'CHILD': '107', 'DOB': '23/07/2002', 'DUC': '23/07/2020'},#Pass B
    {'CHILD': '108', 'DOB': '19/02/2003', 'DUC': '19/02/2021'},#Fail C
    {'CHILD': '109', 'DOB': '14/06/2003', 'DUC': '14/06/2021'},#Fail D
    {'CHILD': '110', 'DOB': '14/06/2003', 'DUC': '14/06/2021'},  # Fail D
])

fake_header_205 = pd.DataFrame([
    {'CHILD': '101', 'DOB': '28/10/2004', 'UASC': '0'},#Pass C
    {'CHILD': '108', 'DOB': '19/02/2003', 'UASC': '0'},#Fail C
    {'CHILD': '109', 'DOB': '14/06/2003', 'UASC': '1'},#Fail D
    {'CHILD': '102', 'DOB': '04/06/2004', 'UASC': '0'},#Pass A
    {'CHILD': '103', 'DOB': '03/03/2002', 'UASC': '0'},#Fail A
    {'CHILD': '104', 'DOB': '28/03/2003', 'UASC': '0'},#Fail A
    {'CHILD': '105', 'DOB': '16/04/2001', 'UASC': '1'},#Fail B
    {'CHILD': '106', 'DOB': '04/11/2004', 'UASC': '1'},#Fail B
    {'CHILD': '107', 'DOB': '23/07/2002', 'UASC': '1'},#Pass B
    {'CHILD': '110', 'DOB': '03/03/2002', 'UASC': '0'},

])

prev_fake_header_205 = pd.DataFrame([
    {'CHILD': '102', 'DOB': '04/06/2004', 'UASC': '1'},#Pass A
    {'CHILD': '103', 'DOB': '03/03/2002', 'UASC': '1'},#Fail A
    {'CHILD': '104', 'DOB': '28/03/2003', 'UASC': '1'},#Fail A
    {'CHILD': '101', 'DOB': '28/10/2004', 'UASC': '0'},#Pass C
    {'CHILD': '105', 'DOB': '16/04/2001', 'UASC': '1'},#Fail B
    {'CHILD': '106', 'DOB': '04/11/2004', 'UASC': '1'},#Fail B
    {'CHILD': '107', 'DOB': '23/07/2002', 'UASC': '1'},#Pass B
    {'CHILD': '108', 'DOB': '19/02/2003', 'UASC': '0'},#Fail C
    {'CHILD': '109', 'DOB': '14/06/2003', 'UASC': '0'},#Fail D
    {'CHILD': '110', 'DOB': '03/03/2002', 'UASC': '0'},
])

metadata_205 = {
        'collection_start': '01/04/2020',
        'collection_end': '31/03/2021',
}

fake_dfs_205_xml = {
    'UASC': fake_uasc_205,
    'UASC_last': fake_uasc_prev_205,
    'Header': fake_header_205,
    'Header_last': prev_fake_header_205,
    'metadata': {**metadata_205, **{'file_format': 'xml'}},
}
fake_dfs_205_csv_1 = {
    'UASC': fake_uasc_205,
    'UASC_last': fake_uasc_prev_205,
    'Header': fake_header_205,
    'metadata': {**metadata_205, **{'file_format': 'csv'}},
}
fake_dfs_205_csv_2 = {
    'UASC': fake_uasc_205,
    'UASC_last': fake_uasc_prev_205,
    'metadata': {**metadata_205, **{'file_format': 'csv'}},
}


def test_validate_205A():
    error_defn, error_func = validate_205A()

    dfs = {k: v.copy() for k, v in fake_dfs_205_xml.items()}
    result = error_func(dfs)
    assert result == {'UASC': [2, 3], 'Header': [4, 5]}

    dfs = {k: v.copy() for k, v in fake_dfs_205_csv_1.items()}
    result = error_func(dfs)
    assert result == {'UASC': [2, 3, 7, 9], 'Header': [1, 4, 5, 9]}


def test_validate_205B():
    error_defn, error_func = validate_205B()

    dfs = {k: v.copy() for k, v in fake_dfs_205_xml.items()}
    result = error_func(dfs)
    assert result == {'UASC': [5], 'Header':[7]}

    dfs = {k: v.copy() for k, v in fake_dfs_205_csv_1.items()}
    result = error_func(dfs)
    assert result == {'UASC': [5], 'Header': [7]}

    dfs = {k: v.copy() for k, v in fake_dfs_205_csv_2.items()}
    result = error_func(dfs)
    assert result == {'UASC': [2, 3, 5]}


def test_validate_205C():
    error_defn, error_func = validate_205C()
    dfs = {k: v.copy() for k, v in fake_dfs_205_xml.items()}
    dfs['Header'].loc['1001'] = {'CHILD': '1001', 'DOB': 'asdsad', 'UASC': '0'}
    dfs['UASC'].loc['1001'] = {'CHILD': '1001', 'DOB': '23/07/2002', 'DUC': '01/01/2020'}

    dfs = {k: v.copy() for k, v in fake_dfs_205_xml.items()}
    result = error_func(dfs)
    assert result == {'Header': [1, 9], 'UASC': [7, 9]}

    dfs = {k: v.copy() for k, v in fake_dfs_205_csv_1.items()}
    result = error_func(dfs)
    assert result == {'Header': [], 'UASC': []}

    dfs = {k: v.copy() for k, v in fake_dfs_205_csv_2.items()}
    result = error_func(dfs)
    assert result == {'UASC': []}


def test_validate_205D():
    error_defn, error_func = validate_205D()
    result = error_func(fake_dfs_205_xml)
    assert result == {'Header': [2]}

    dfs = {k: v.copy() for k, v in fake_dfs_205_csv_2.items()}
    dfs['UASC_last'].loc['1001'] = {'CHILD': '1001', 'DOB': '23/07/2002', 'DUC': '01/01/2020'}
    dfs['UASC'].loc['1001'] = {'CHILD': '1001', 'DOB': '23/07/2002', 'DUC': '99/bad/date'}
    dfs['UASC'].loc['1022'] = {'CHILD': '1022', 'DOB': '23/07/2002', 'DUC': '01/01/2020'}
    dfs['UASC_last'].loc['1022'] = {'CHILD': '1022', 'DOB': '23/07/2002', 'DUC': pd.NA}

    result = error_func(dfs)
    assert result == {'UASC': ['1022']}

def test_validate_426():
    fake_data = pd.DataFrame([
        {'CHILD': '111', 'LS': 'V3'},  # 0
        {'CHILD': '111', 'LS': 'V3'},  # 1
        {'CHILD': '222', 'LS': 'V3'},  # 2 Fail
        {'CHILD': '222', 'LS': 'V4'},  # 3 Fail
        {'CHILD': '222', 'LS': 'X1'},  # 4
        {'CHILD': '444', 'LS': 'V3'},  # 5
        {'CHILD': '555', 'LS': 'V4'},  # 6 Fail
        {'CHILD': '555', 'LS': 'V3'},  # 7 Fail
        {'CHILD': '555', 'LS': 'V3'},  # 8 Fail
    ])

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_426()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [2, 3, 6, 7, 8]}


def test_validate_1002():
    fake_episodes_prev = pd.DataFrame({
      'CHILD': ['101','101','102','102','103'],
      'DEC': ['20/06/2020', pd.NA, pd.NA, '14/03/2021', '06/08/2020']
    })

    fake_episodes = pd.DataFrame({
      'CHILD': ['101'],
      'DEC': ['20/05/2021']
    })

    fake_oc3 = pd.DataFrame({
      'CHILD': ['101','102','103','104']
    })

    erro_defn, error_func = validate_1002()

    fake_dfs = {'Episodes': fake_episodes, 'Episodes_last': fake_episodes_prev, 'OC3': fake_oc3}
    result = error_func(fake_dfs)
    assert result == {'OC3': [3]}

def test_validate_633():
    fake_data_prevperm = pd.DataFrame({
        'CHILD': ['101', '102', '103', '6', '7', '8'],
        'LA_PERM': [pd.NA, 'SCO', '204', '458', '176', 212],
    })
    fake_dfs = {'PrevPerm':fake_data_prevperm}
    error_defn, error_func = validate_633()
    result = error_func(fake_dfs)
    assert result == {'PrevPerm':[3,4]}


def test_validate_199():
    fake_data_199_episodes_last = pd.DataFrame([
        {'CHILD': '101', 'DECOM': '15/06/2016', 'DEC': '20/12/2020', 'REC': 'E11'},
        {'CHILD': '102', 'DECOM': '08/10/2017', 'DEC': '03/03/2018', 'REC': 'E11'},
        {'CHILD': '102', 'DECOM': '06/03/2018', 'DEC': '12/08/2020', 'REC': 'E4a'},
        {'CHILD': '103', 'DECOM': '11/05/2015', 'DEC': '07/04/2019', 'REC': 'E12'},
        {'CHILD': '104', 'DECOM': '26/11/2017', 'DEC': '19/07/2020', 'REC': 'E12'},
        {'CHILD': '107', 'DECOM': '26/11/2017', 'DEC': pd.NA, 'REC': 'E12'},
    ])

    fake_data_199_episodes = pd.DataFrame([
        {'CHILD': '104', 'DECOM': '19/07/2020', 'DEC': '02/03/2021', 'REC': 'E13'},  # 0: Pass -> Fail
        {'CHILD': '103', 'DECOM': '16/04/2020', 'DEC': pd.NA, 'REC': pd.NA},  # 1: Pass -> Fail
        {'CHILD': '103', 'DECOM': '16/04/2020', 'DEC': pd.NA, 'REC': 'oo'},  # 2: Pass -> Fail
        {'CHILD': '105', 'DECOM': '02/12/2021', 'DEC': '03/12/2021', 'REC': 'X1'},  # 3: Pass
        {'CHILD': '105', 'DECOM': '03/12/2021', 'DEC': '04/12/2021', 'REC': 'E11'},  # 4:Pass
        {'CHILD': '105', 'DECOM': '03/12/2022', 'DEC': '04/12/2022', 'REC': 'E11'},  # 5: Fail
        {'CHILD': '105', 'DECOM': '12/12/2021', 'DEC': pd.NA, 'REC': pd.NA},  # 6: Fail
        {'CHILD': '107', 'DECOM': '04/12/2021', 'DEC': pd.NA, 'REC': 'XXX'},  # 7: Fail
        {'CHILD': '107', 'DECOM': '26/11/2017', 'DEC': '04/12/2021', 'REC': 'E12'},  # 8: Pass

    ])
    error_defn, error_func = validate_199()

    fake_dfs = {'Episodes': fake_data_199_episodes.copy()}
    result = error_func(fake_dfs)
    assert result == {'Episodes': [5, 6, 7]}

    fake_dfs = {'Episodes': fake_data_199_episodes, 'Episodes_last': fake_data_199_episodes_last}
    result = error_func(fake_dfs)
    assert result == {'Episodes': [0, 1, 2, 5, 6, 7]}
    
def test_validate_164():
    fake_episodes = pd.DataFrame([
        {'CHILD': '111', 'LS':'V3', 'PL_DISTANCE': '0.0'},  # 0 ignore: LS

        {'CHILD': '222', 'LS':'V1', 'PL_DISTANCE': pd.NA},  # 1
        {'CHILD': '222', 'LS':'V5', 'PL_DISTANCE': '-2'},  # 2 fail

        {'CHILD': '333', 'LS':'V1', 'PL_DISTANCE': '3.5'},  # 3 pass
        {'CHILD': '333', 'LS':'V2', 'PL_DISTANCE': '1000'},  # 4 fail

        {'CHILD': '345', 'LS':'V7', 'PL_DISTANCE': '1380'},  # 5 ignore: UASC
    ])
    fake_header = pd.DataFrame([
        {'CHILD': '111', 'UASC': '0'},
        {'CHILD': '222', 'UASC': '0'},
        {'CHILD': '333', 'UASC': '0'},
        {'CHILD': '345', 'UASC': '0'},
    ])
    fake_header_last = pd.DataFrame([
        {'CHILD': '111', 'UASC': '0'},
        {'CHILD': '222', 'UASC': '0'},
        {'CHILD': '333', 'UASC': '0'},
        {'CHILD': '345', 'UASC': '1'},
    ])

    fake_dfs = {'Episodes': fake_episodes, 'Header': fake_header, 'Header_last':fake_header_last}

    error_defn, error_func = validate_164()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [2, 4]}

    uasc_last = pd.DataFrame([
        {'CHILD': '333', 'DUC': 'something'},  # [3] in episodes - passes now
        {'CHILD': '345', 'DUC': pd.NA}   # [8] in episodes - still fails
    ])

    dfs = {'Episodes': fake_episodes,
           'Header': fake_header,
           'UASC_last': uasc_last}
    result = error_func(dfs)
    assert result == {'Episodes': [2, 5]}

def test_validate_554():
    fake_placed_adoption = pd.DataFrame([
        {'CHILD': 101, 'DATE_PLACED': '26/05/2022'},
        # 0
        {'CHILD': 102, 'DATE_PLACED': pd.NA},
        # 1
        {'CHILD': 103, 'DATE_PLACED': '26/05/2020',},  # 2
        {'CHILD': 104, 'DATE_PLACED': '22/01/2020'},
        # 3
        {'CHILD': 105, 'DATE_PLACED': '11/01/2020',},  # 4
    ])
    fake_data_episodes = pd.DataFrame([
        # first E1 episode is first episode
        {'CHILD': 101, 'DECOM': '01/01/2020', 'LS': 'E1',},  # 0 fail DATE_PLACED>DECOM
        {'CHILD': 101, 'DECOM': '11/01/2020', 'LS': 'T1',},  # 1
        {'CHILD': 101, 'DECOM': '22/01/2020', 'LS': 'A3',},  # 2
        # no E1 episode
        {'CHILD': 102, 'DECOM': '11/01/2020', 'LS': 'A4',},  # 4
        {'CHILD': 102, 'DECOM': '01/01/2020', 'LS': 'U1', },  # 3
        # first E1 episode is not first episode
        {'CHILD': 103, 'DECOM': '01/01/2020', 'LS': 'U1',},  # 5
        {'CHILD': 103, 'DECOM': '22/07/2020', 'LS': 'E1',},  # 6 pass
        {'CHILD': 103, 'DECOM': '11/01/2020', 'LS': 'T2',},  # 7

        {'CHILD': 104, 'DECOM': '01/02/2016', 'LS': 'E1',},  # 8 fail DATE_PLACED>DECOM
        {'CHILD': 104, 'DECOM': '11/01/2020', 'LS': 'X1',},  # 9
        {'CHILD': 104, 'DECOM': '01/01/2020', 'LS': 'A3',},  # 10

        {'CHILD': 105, 'DECOM': '11/01/2020', 'LS': 'E1', },  # 11 pass DATE_PLACED equals DECOM
        {'CHILD': 105, 'DECOM': '01/01/2020', 'LS': pd.NA, },  # 12
    ])
    fake_dfs = {'Episodes':fake_data_episodes, 'PlacedAdoption':fake_placed_adoption}
    error_defn, error_func = validate_554()
    result = error_func(fake_dfs)
    assert result == {'Episodes': [0,8], 'PlacedAdoption':[0,3]}

def test_validate_229():
    fake_data_eps = pd.DataFrame([
        {'CHILD': '1111', 'PLACE_PROVIDER': 'PR1', 'URN': 1,},  # 0 fail
        {'CHILD': '1111', 'PLACE_PROVIDER': 'PR2', 'URN': pd.NA,},  # 1 ignore: URN is nan
        {'CHILD': '1111', 'PLACE_PROVIDER': 'PR2', 'URN': 4,},  # 2 pass

        {'CHILD': '2222', 'PLACE_PROVIDER': 'PR1', 'URN': 'XXXXXXX',},  # 3 ignore: URN

        {'CHILD': '3333', 'PLACE_PROVIDER': 'PR2', 'URN': 2,},  # 4  fail
        {'CHILD': '3333', 'PLACE_PROVIDER': 'PR1', 'URN': 2,},  # 5  pass

        {'CHILD': '4444', 'PLACE_PROVIDER': 'PR2', 'URN': 3,},  # 6 pass

        {'CHILD': '5555', 'PLACE_PROVIDER': 'PR1', 'URN': 4,},  # 7 fail
        {'CHILD': '5555', 'PLACE_PROVIDER': 'PR2', 'URN': 1,},  # 8 pass
    ])
    fake_provider_info = pd.DataFrame([
        {'URN': 1, 'LA_CODE_INFERRED': 'other', },  # 0
        {'URN': 2, 'LA_CODE_INFERRED': 'auth', },  # 1
        {'URN': 3, 'LA_CODE_INFERRED': 'other', },  # 2
        {'URN': 4, 'LA_CODE_INFERRED': pd.NA, },  # 3
    ])
    metadata = {'localAuthority': 'auth', 'provider_info':fake_provider_info}

    fake_dfs = {'Episodes':fake_data_eps, 'metadata':metadata}
    error_defn, error_func = validate_229()
    result = error_func(fake_dfs)

    assert result == {'Episodes':[0,4,7]}

def test_validate_406():
    fake_episodes = pd.DataFrame([
        {'CHILD': '111', 'PL_DISTANCE': 'XX1'},  # 0 fail
        {'CHILD': '222', 'PL_DISTANCE': pd.NA},  # 1
        {'CHILD': '222', 'PL_DISTANCE': 'XX1'},  # 2 fail
        {'CHILD': '333', 'PL_DISTANCE': pd.NA},  # 3
        {'CHILD': '333', 'PL_DISTANCE': 'XX1'},  # 4 ignore: it is not present in any uasc table.
        {'CHILD': '345', 'PL_DISTANCE': pd.NA},  # 5
        {'CHILD': '444', 'PL_DISTANCE': 'XX1'},  # 6 fail
        {'CHILD': '444', 'PL_DISTANCE': pd.NA},  # 7
    ])
    fake_header = pd.DataFrame([
        {'CHILD': '111', 'UASC': '1'},  # 0
        {'CHILD': '222', 'UASC': '0'},  # 2
        {'CHILD': '333', 'UASC': '0'},  # 4
        {'CHILD': '345', 'UASC': '1'},  # 5
        {'CHILD': '444', 'UASC': '0'},  # 6
    ])
    fake_header_last = pd.DataFrame([
        {'CHILD': '111', 'UASC': '0'},  # 0
        {'CHILD': '222', 'UASC': '1'},  # 2
        {'CHILD': '333', 'UASC': '0'},  # 4
        {'CHILD': '345', 'UASC': '0'},  # 5
        {'CHILD': '444', 'UASC': '1'},  # 6
    ])

    fake_dfs = {'Episodes': fake_episodes, 'Header': fake_header, 'Header_last':fake_header_last}

    error_defn, error_func = validate_406()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [0, 2, 6]}


def test_validate_227():
    fake_data_eps = pd.DataFrame([
        {'CHILD': '1111', 'DECOM': '01/01/2014', 'URN': 1, },  # 0 pass
        {'CHILD': '1111', 'DECOM': '01/02/2015', 'URN': pd.NA, },  # 1 ignore: URN not provided
        {'CHILD': '1111', 'DECOM': '01/01/2016', 'URN': 3, },  # 2 pass

        {'CHILD': '2222', 'DECOM': '01/01/2010', 'URN': 'XXXXXXX', },  # 3 ignore

        {'CHILD': '3333', 'DECOM': '01/01/2010', 'URN': 2, },  # 4 pass
        {'CHILD': '3333', 'DECOM': '25/12/2015', 'URN': 2, },  # 5 fail DECOM after REG_END

        {'CHILD': '4444', 'DECOM': '25/12/2016', 'URN': 1, },  # 6 fail. DECOM after REG_END

        {'CHILD': '5555', 'DECOM': '01/01/2010', 'URN': 4, },  # 7 ignore: REG_END not provided
        {'CHILD': '5555', 'DECOM': '25/12/2015', 'URN': 1, },  # 8 fail DECOM equals REG_END
    ])
    provider_info = pd.DataFrame([
        {'URN': 1, 'REG_END': '25/12/2015', },  # 0
        {'URN': 2, 'REG_END': '21/02/2014', },  # 1
        {'URN': 3, 'REG_END': '25/12/2017', },  # 2
        {'URN': 3, 'REG_END': pd.NA, },  # 3
    ])
    provider_info['REG_END'] = pd.to_datetime(provider_info['REG_END'], format='%d/%m/%Y', errors='coerce')

    metadata = {'provider_info': provider_info}

    fake_dfs = {'Episodes': fake_data_eps, 'metadata': metadata}
    error_defn, error_func = validate_227()
    result = error_func(fake_dfs)

    assert result == {'Episodes': [5, 6, 8]}



def test_validate_224():
    fake_data_eps = pd.DataFrame([
        {'CHILD': '1111', 'PLACE_PROVIDER': 'PR2', 'URN': 1, },  # 0 fail
        {'CHILD': '1111', 'PLACE_PROVIDER': 'PR5', 'URN': pd.NA, },  # 1 ignore
        {'CHILD': '1111', 'PLACE_PROVIDER': 'PR0', 'URN': 3, },  # 2 fail

        {'CHILD': '2222', 'PLACE_PROVIDER': 'PR3', 'URN': 'XXXXXXX', },  # 3 ignore

        {'CHILD': '3333', 'PLACE_PROVIDER': 'PR0', 'URN': 2, },  # 4 pass
        {'CHILD': '3333', 'PLACE_PROVIDER': 'PR3', 'URN': 2, },  # 5 fail

        {'CHILD': '4444', 'PLACE_PROVIDER': 'PR3', 'URN': 1, },  # 6 pass

        {'CHILD': '5555', 'PLACE_PROVIDER': 'PR3', 'URN': 4, },  # 7 fail - if PROVIDER_CODES is null something is wrong
        {'CHILD': '5555', 'PLACE_PROVIDER': 'PR4', 'URN': 1, },  # 8 pass
    ])
    fake_provider_info = pd.DataFrame([
        {'URN': 1, 'PROVIDER_CODES': 'PR1,PR3,PR4', },  # 0
        {'URN': 2, 'PROVIDER_CODES': 'PR0', },  # 1
        {'URN': 3, 'PROVIDER_CODES': 'PR1', },  # 2
        {'URN': 4, 'PROVIDER_CODES': pd.NA, },  # 3
    ])
    metadata = {'provider_info': fake_provider_info}

    fake_dfs = {'Episodes': fake_data_eps, 'metadata': metadata}
    error_defn, error_func = validate_224()
    result = error_func(fake_dfs)

    assert result == {'Episodes': [0, 2, 5, 7]}



def test_validate_221():
    fake_data_eps = pd.DataFrame([
        {'CHILD': '1111', 'LS': 'V3', 'PLACE': 'R3', 'PL_POST': 'A11 5KE', 'URN': 1, },  # 0 ignore: LS is V3
        {'CHILD': '1111', 'LS': 'V2', 'PLACE': 'R3', 'PL_POST': 'PR5', 'URN': pd.NA, },  # 1 ignore: URN value
        {'CHILD': '1111', 'LS': 'V2', 'PLACE': 'K1', 'PL_POST': 'S25 1WO', 'URN': 3, },  # 2 fail

        {'CHILD': '2222', 'LS': 'V2', 'PLACE': 'K2', 'PL_POST': 'PR3', 'URN': 'XXXXXXX', },  # 3 ignore: URN value

        {'CHILD': '3333', 'LS': 'V2', 'PLACE': 'R3', 'PL_POST': 'S25 1WO', 'URN': 2, },  # 4 pass
        {'CHILD': '3333', 'LS': 'V2', 'PLACE': 'xx', 'PL_POST': 'S25 1WO', 'URN': 2, },  # 5 ignore: PLACE value

        {'CHILD': '4444', 'LS': 'V2', 'PLACE': 'S1', 'PL_POST': 'N9 5PY', 'URN': 1, },  # 6 fail

        {'CHILD': '5555', 'LS': 'V2', 'PLACE': 'S1', 'PL_POST': 'N9 5PY', 'URN': 4, },  # 7 fail
        {'CHILD': '5555', 'LS': 'V2', 'PLACE': 'R3', 'PL_POST': pd.NA, 'URN': 1, },  # 8 ignore: PL_POST value
    ])
    fake_provider_info = pd.DataFrame([
        {'URN': 1, 'POSTCODE': 'A115KE', },  # 0
        {'URN': 2, 'POSTCODE': 'S251WO', },  # 1
        {'URN': 3, 'POSTCODE': 'V29XX', },  # 2
        {'URN': 4, 'POSTCODE': pd.NA, },  # 3 should NaNs be ignored?
    ])
    metadata = {'provider_info': fake_provider_info}

    fake_dfs = {'Episodes': fake_data_eps, 'metadata': metadata}
    error_defn, error_func = validate_221()
    result = error_func(fake_dfs)

    assert result == {'Episodes': [2, 6, 7]}



def test_validate_228():
    fake_data_eps = pd.DataFrame([
        {'CHILD': '1111', 'DEC': pd.NA, 'URN': 1, },  # 0 pass REG_END is after March 31st of collection year
        {'CHILD': '1111', 'DEC': '01/02/2015', 'URN': pd.NA, },  # 1 ignore: URN not provided
        {'CHILD': '1111', 'DEC': pd.NA, 'URN': 3, },  # 2 fail REG_END is before March 31st of collection year

        {'CHILD': '2222', 'DEC': '01/01/2010', 'URN': 'XXXXXXX', },  # 3 ignore: URN

        {'CHILD': '3333', 'DEC': '01/01/2010', 'URN': 2, },  # 4 pass
        {'CHILD': '3333', 'DEC': '25/12/2015', 'URN': 2, },  # 5 fail DEC after REG_END

        {'CHILD': '4444', 'DEC': '25/12/2016', 'URN': 1, },  # 6 fail. DEC after REG_END

        {'CHILD': '5555', 'DEC': '01/01/2010', 'URN': 4, },  # 7 ignore: REG_END is null
        {'CHILD': '5555', 'DEC': '25/12/2015', 'URN': 1, },  # 8 pass DEC equals REG_END
    ])
    fake_provider_info = pd.DataFrame([
        {'URN': 1, 'REG_END': '25/12/2015', },  # 0
        {'URN': 2, 'REG_END': '21/02/2014', },  # 1
        {'URN': 3, 'REG_END': '01/02/2015', },  # 2
        {'URN': 4, 'REG_END': pd.NA, },  # 3
    ])
    fake_provider_info['REG_END'] = pd.to_datetime(fake_provider_info['REG_END'], format='%d/%m/%Y', errors='raise')
    metadata = {'collection_start': '01/04/2014', 'collection_end': '31/03/2015', 'provider_info': fake_provider_info}

    fake_dfs = {'Episodes': fake_data_eps, 'metadata': metadata}
    error_defn, error_func = validate_228()
    result = error_func(fake_dfs)

    assert result == {'Episodes': [2, 5, 6]}



def test_validate_219():
    fake_data_eps = pd.DataFrame([
        {'CHILD': '1111', 'PLACE': 'PR5', 'URN': 1, },  # 0 fail
        {'CHILD': '1111', 'PLACE': 'PR5', 'URN': pd.NA, },  # 1 ignore: URN
        {'CHILD': '1111', 'PLACE': 'PR7', 'URN': 3, },  # 2 fail

        {'CHILD': '2222', 'PLACE': 'PR5', 'URN': 'XXXXXXX', },  # 3 ignore: URN

        {'CHILD': '3333', 'PLACE': 'PR1', 'URN': 2, },  # 4 pass
        {'CHILD': '3333', 'PLACE': 'PR3', 'URN': 2, },  # 5 pass

        {'CHILD': '4444', 'PLACE': 'PR5', 'URN': 1, },  # 6 fail

        {'CHILD': '5555', 'PLACE': 'PR5', 'URN': 4, },  # 7 fail - PLACE_CODES should not be null so probly needs a look
        {'CHILD': '5555', 'PLACE': 'PR2', 'URN': 1, },  # 8 pass
    ])
    fake_provider_info = pd.DataFrame([
        {'URN': 1, 'PLACE_CODES': 'PR2', },  # 0
        {'URN': 2, 'PLACE_CODES': 'PR1,PR3,PR5', },  # 1
        {'URN': 3, 'PLACE_CODES': 'PR5,PR4,PR2', },  # 2
        {'URN': 4, 'PLACE_CODES': pd.NA, },  # 3
    ])
    metadata = {'provider_info': fake_provider_info}

    fake_dfs = {'Episodes': fake_data_eps, 'metadata': metadata}
    error_defn, error_func = validate_219()
    result = error_func(fake_dfs)

    assert result == {'Episodes': [0, 2, 6, 7]}



def test_validate_1008():
    fake_data_eps = pd.DataFrame([
        {'CHILD': '1111', 'URN': 'SC999999', },  # 0 pass
        {'CHILD': '1111', 'URN': pd.NA, },  # 1 ignore
        {'CHILD': '1111', 'URN': 1234567, },  # 2 pass: digits will be converted to strings before comparison.

        {'CHILD': '2222', 'URN': 'XXXXXXX', },  # 3 pass: accepted placeholder value

        {'CHILD': '3333', 'URN': '1234567', },  # 4 pass
        {'CHILD': '3333', 'URN': '2345', },  # 5 fail

        {'CHILD': '4444', 'URN': '999999', },  # 6 pass

        {'CHILD': '5555', 'URN': '5b67891', },  # 7 fail
        {'CHILD': '5555', 'URN': 'XXXXXX', },  # 8 fail: 6 Xs instead of seven
    ])

    metadata = {
        'provider_info':
            pd.DataFrame({'URN': ['1234567', 'SC999999', '999999']})
    }
    fake_dfs = {'Episodes': fake_data_eps, 'metadata': metadata}
    error_defn, error_func = validate_1008()
    result = error_func(fake_dfs)

    assert result == {'Episodes': [5, 7, 8]}


def test_validate_218():
    fake_data_eps = pd.DataFrame([

        {'CHILD': '1111', 'PLACE': 'H5', 'DEC': '01/02/2014', 'PL_LA': 'o', 'URN': 'xx'},  # 0 ignore: of PLACE value
        {'CHILD': '1111', 'PLACE': 'C2', 'DEC': '01/06/2015', 'PL_LA': 'W06000008', 'URN': 'xx'},  # 1 ignore: PL_LA is Wales
        {'CHILD': '1111', 'PLACE': 'C2', 'DEC': '01/02/2016', 'PL_LA': 'o', 'URN': 'xx'},  # 2 pass

        {'CHILD': '2222', 'PLACE': 'C2', 'DEC': '01/02/2014', 'PL_LA': 'o', 'URN': 'xx'},  # 3 ignore: DEC < coll. end
        {'CHILD': '2222', 'PLACE': 'xx', 'DEC': pd.NA, 'PL_LA': 'o', 'URN': pd.NA},  # 4 fail
        {'CHILD': '2222', 'PLACE': 'R5', 'DEC': '01/02/2016', 'PL_LA': 'o', 'URN': 'xx'},  # 5 ignore: of PLACE value

        {'CHILD': '3333', 'PLACE': 'C2', 'DEC': '01/03/2014', 'PL_LA': 'o', 'URN': pd.NA},  # 6 ignore: DEC
        {'CHILD': '3333', 'PLACE': 'C2', 'DEC': '04/01/2016', 'PL_LA': 'o', 'URN': pd.NA},  # 7 fail

        {'CHILD': '4444', 'PLACE': 'C2', 'DEC': '01/02/2016', 'PL_LA': 'o', 'URN': pd.NA},  # 8 fail
        {'CHILD': '4444', 'PLACE': 'C2', 'DEC': '01/04/2017', 'PL_LA': 'o', 'URN': pd.NA},  # 9 fail

        {'CHILD': '5555', 'PLACE': 'C2', 'DEC': '31/03/2015', 'PL_LA': 'o', 'URN': pd.NA},  # 10 ignore: DEC
        {'CHILD': '5555', 'PLACE': 'C2', 'DEC': '04/01/2016', 'PL_LA': 'SCO', 'URN': pd.NA},  # 11 ignore: in Scotland
    ])

    metadata = {'collection_start': '01/04/2015'}

    fake_dfs = {'Episodes': fake_data_eps, 'metadata': metadata}
    error_defn, error_func = validate_218()

    result = error_func(fake_dfs)
    assert result == {'Episodes': [4, 7, 8, 9]}


def test_validate_543():
    fake_data_episodes = pd.DataFrame([
        {'CHILD': 101, 'DECOM': '01/03/1980', 'DEC': '31/03/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},  # CLA
        {'CHILD': 102, 'DECOM': '01/03/1980', 'DEC': '30/03/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},  # CLA
        {'CHILD': 103, 'DECOM': '01/03/1980', 'DEC': '01/01/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},  # CLA
        {'CHILD': 104, 'DECOM': '01/02/1970', 'DEC': pd.NA, 'LS': 'o', 'REC': '!!', 'RNE': 'o'},  # CLA
        {'CHILD': 105, 'DECOM': '01/03/1979', 'DEC': '01/01/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},  # CLA
        {'CHILD': 105, 'DECOM': '01/01/1981', 'DEC': '01/01/1983', 'LS': 'o', 'REC': 'oo', 'RNE': 'o'},  # CLA
        {'CHILD': 106, 'DECOM': '01/03/1980', 'DEC': '01/01/1982', 'LS': 'V3', 'REC': 'X1', 'RNE': 'o'},  # not CLA: V3
        {'CHILD': 107, 'DECOM': '01/03/1980', 'DEC': '01/01/1982', 'LS': 'V3', 'REC': '!!', 'RNE': 'o'},  # not CLA: REC
    ])
    fake_data = pd.DataFrame({
        'CHILD': [101, 102, 103, 104,
                  105, 106, 107, 333],
        'DOB': ['08/03/1973', '22/06/1968', pd.NA, '13/10/1968',
                '10/01/1966', '01/01/1965', '01/01/1965', '01/01/1965'],
        'CONVICTED': [pd.NA, pd.NA, pd.NA, 1,
                      pd.NA, pd.NA, pd.NA, pd.NA],
        # 0 pass: under 10
        # 1 fail : CLA is true, over 10, and CONVICTED is not provided
        # 2 pass: DOB is nan
        # 3 pass: under 5 (born in future), but CONVICTED provided
        # 4 fail: CLA is true, over 10, and CONVICTED is not provided
        # 5 pass: not CLA
        # 6 pass: not CLA
        # 7 pass: not in episodes -> not CLA
    })

    metadata = {'collection_start': '01/04/1980', 'collection_end': '31/03/1981'}

    fake_dfs = {'OC2': fake_data, 'metadata': metadata, 'Episodes': fake_data_episodes}

    error_defn, error_func = validate_543()

    result = error_func(fake_dfs)

    assert result == {'OC2': [1, 4]}


def test_validate_392A():
    fake_episodes = pd.DataFrame([
        {'CHILD': '111', 'LS': 'L1', 'PL_DISTANCE': 'XX1'},  # 0
        {'CHILD': '222', 'LS': 'L1', 'PL_DISTANCE': pd.NA},  # 1 fail
        {'CHILD': '222', 'LS': 'V3', 'PL_DISTANCE': 'XX1'},  # 2
        {'CHILD': '333', 'LS': 'L1', 'PL_DISTANCE': pd.NA},  # 3 fail
        {'CHILD': '333', 'LS': 'V4', 'PL_DISTANCE': 'XX1'},  # 4
        {'CHILD': '345', 'LS': 'L1', 'PL_DISTANCE': pd.NA},  # 5 fail
        {'CHILD': '444', 'LS': 'L1', 'PL_DISTANCE': 'XX1'},  # 6
        {'CHILD': '444', 'LS': 'V3', 'PL_DISTANCE': pd.NA},  # 7 pass since LS isin [V3, V4]
        {'CHILD': '555', 'LS': 'L1', 'PL_DISTANCE': pd.NA},  # 8 fail

    ])
    fake_header = pd.DataFrame([
        {'CHILD': '111', 'UASC': '1'},  # 0
        {'CHILD': '222', 'UASC': '0'},  # 2
        {'CHILD': '333', 'UASC': '0'},  # 4
        {'CHILD': '345', 'UASC': '0'},  # 5
        {'CHILD': '444', 'UASC': '0'},  # 6
        {'CHILD': '555', 'UASC': '0'},  # 6
    ])
    fake_header_last = pd.DataFrame([
        {'CHILD': '111', 'UASC': '0'},  # 0
        {'CHILD': '222', 'UASC': '0'},  # 2
        {'CHILD': '333', 'UASC': '0'},  # 4
        {'CHILD': '345', 'UASC': '0'},  # 5
        {'CHILD': '444', 'UASC': '1'},  # 6
    ])


    error_defn, error_func = validate_392A()

    dfs = {'Episodes': fake_episodes, 'Header': fake_header, 'Header_last':fake_header_last}
    result = error_func(dfs)
    assert result == {'Episodes': [1, 3, 5, 8]}

    uasc_last = pd.DataFrame([
        {'CHILD': '333', 'DUC': 'something'},  # [3] in episodes - passes now
        {'CHILD': '555', 'DUC': pd.NA}   # [8] in episodes - still fails
    ])

    dfs = {'Episodes': fake_episodes,
           'Header': fake_header,
           'UASC_last': uasc_last}
    result = error_func(dfs)
    assert result == {'Episodes': [1, 5, 8]}


def test_validate_1001():
    # DOB always 01/01/2000
    # next to each episode, approx days in each age bracket is listed like so:      under 14  :  14-16  :  over 16
    eps = pd.DataFrame([
        # [0] - PASS: more than 91 relevant days
        {'CHILD': '1111', 'LS': 'C2', 'DECOM': '01/01/2014', 'DEC': '01/02/2014', 'REC': 'o'},  # :30:
        {'CHILD': '1111', 'LS': 'C2', 'DECOM': '01/02/2015', 'DEC': '01/06/2015', 'REC': 'o'},  # :120:
        {'CHILD': '1111', 'LS': 'C2', 'DECOM': '01/01/2016', 'DEC': '01/02/2016', 'REC': 'o'},  # ::1

        # [1] - FAIL: less than 91 days
        {'CHILD': '2222', 'LS': 'C2', 'DECOM': '01/01/2010', 'DEC': '01/02/2014', 'REC': 'o'},  # :30:
        {'CHILD': '2222', 'LS': 'C2', 'DECOM': '01/01/2010', 'DEC': pd.NA, 'REC': 'o'},  # Duplicate DECOM, missing
                                                                                         # DEC - should get dropped
        {'CHILD': '2222', 'LS': 'C2', 'DECOM': '25/12/2015', 'DEC': '01/02/2016', 'REC': 'o'},  # :7:30

        # [2] - FAIL: more than 91 days but not after 14th bday
        {'CHILD': '3333', 'LS': 'C2', 'DECOM': '01/01/2010', 'DEC': '01/03/2014', 'REC': 'o'},  # 120:60:
        {'CHILD': '3333', 'LS': 'C2', 'DECOM': '25/12/2015', 'DEC': '04/01/2016', 'REC': 'o'},  # :7:3

        # [3] - PASS: more than 91 days, all after 16th bday
        {'CHILD': '4444', 'LS': 'C2', 'DECOM': '01/01/2016', 'DEC': '01/02/2016', 'REC': 'o'},  # ::30
        {'CHILD': '4444', 'LS': 'C2', 'DECOM': '25/12/2016', 'DEC': '01/04/2017', 'REC': 'o'},  # ::120

        # [-] - PASS: not in OC3
        {'CHILD': '5555', 'LS': 'C2', 'DECOM': '01/01/2010', 'DEC': '01/05/2012', 'REC': 'o'},  # 120:60:
        {'CHILD': '5555', 'LS': 'C2', 'DECOM': '25/12/2015', 'DEC': '04/01/2016', 'REC': 'o'},  # :7:3

        # [4] - FAIL: more than 91 days but none after 16th bday
        {'CHILD': '6006', 'LS': 'C2', 'DECOM': '01/01/2014', 'DEC': '01/02/2014', 'REC': 'o'},  # :30:
        {'CHILD': '6006', 'LS': 'C2', 'DECOM': '01/02/2015', 'DEC': '01/08/2015', 'REC': 'o'},  # :180:

        # [5] - FAIL: enough days but including V3 episode
        {'CHILD': '7777', 'LS': 'C2', 'DECOM': '01/01/2013', 'DEC': '01/03/2014', 'REC': 'o'},  # 365:60:
        {'CHILD': '7777', 'LS': 'V3', 'DECOM': '01/01/2015', 'DEC': '01/02/2015', 'REC': 'o'},  # :30: (doesnt count)
        {'CHILD': '7777', 'LS': 'C2', 'DECOM': '25/12/2015', 'DEC': '04/01/2016', 'REC': 'o'},  # :7:3

        # [6] - FAIL:  more than 91 days but final REC E11/E12
        {'CHILD': '8888', 'LS': 'C2', 'DECOM': '01/01/2014', 'DEC': '01/02/2014', 'REC': 'o'},  # :30:
        {'CHILD': '8888', 'LS': 'C2', 'DECOM': '01/02/2015', 'DEC': '01/08/2015', 'REC': 'o'},  # :180:
        {'CHILD': '8888', 'LS': 'C2', 'DECOM': '01/02/2016', 'DEC': '01/03/2016', 'REC': 'o'},  # ::30
        {'CHILD': '8888', 'LS': 'C2', 'DECOM': '01/03/2017', 'DEC': '01/05/2017', 'REC': 'E11'},  # ::60 but E11

        # [8] - PASS: more than 91 days if missing DEC filled in
        {'CHILD': '9999', 'LS': 'C2', 'DECOM': '01/01/2010', 'DEC': '01/05/2012', 'REC': 'o'},  # 120:60:
        {'CHILD': '9999', 'LS': 'C2', 'DECOM': '01/06/2017', 'DEC': pd.NA, 'REC': 'o'},  # :40:120
    ])

    metadata = {'collection_end': '01/10/2017'}

    # Split episodes into current and previous year dataframes
    eps['DECOM_dt'] = pd.to_datetime(eps['DECOM'], format='%d/%m/%Y', errors='coerce')
    first_ep_per_child = eps.groupby('CHILD')['DECOM_dt'].idxmin()
    prev_eps = eps.loc[first_ep_per_child].copy().drop('DECOM_dt', axis=1)
    current_eps = eps.drop(index=first_ep_per_child[:-4],
                           columns='DECOM_dt')  # keep a couple eps in both df's, so we know dups dont break it

    assert len(prev_eps) + len(current_eps) == len(eps) + 4, (
        '(test logic problem) creating current/prev episodes tables didnt work as intended'
    )

    oc3 = pd.DataFrame({
        'CHILD': ['1111', '2222', '3333', '4444',
                  '6006', '7777', '8888', '9999'
                  '1010101010'],  # '1010101010' not in episodes
    })

    header = pd.DataFrame({
        'CHILD': ['1111', '2222', '3333', '4444',
                  '6006', '7777', '8888',
                  '1010101010']
    })
    header['DOB'] = '01/01/2000'

    erro_defn, error_func = validate_1001()

    fake_dfs = {'Episodes': current_eps, 'OC3': oc3, 'Header': header,
                'Episodes_last': prev_eps,
                'metadata': metadata}
    result = error_func(fake_dfs)
    assert result == {'OC3': [1, 2, 4, 5, 6, 7]}


def test_validate_302():
    fake_data = pd.DataFrame({
        'CHILD': ['101', '102', '101', '102', '103',
                  '104', '104'],
        'RNE': ['S', 'S', 'X1', pd.NA, 'S',
                'X', 'X'],
        'DECOM': ['16/03/2021', '17/06/2020', '20/03/2020', pd.NA, '23/08/2020',
                  '01/02/1988', '03/04/1994'],
    })

    fake_data_child = pd.DataFrame({
        'CHILD': ['101', '102', '103', '104'],
        'DOB': ['16/03/2021', '23/09/2019', '31/12/2020', '01/01/1995'],
    })

    fake_dfs = {'Episodes': fake_data, 'Header': fake_data_child}

    error_defn, error_func = validate_302()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [2, 4, 5], 'Header': [0, 2, 3]}


def test_validate_336():
    fake_data_episodes = pd.DataFrame([
        {'CHILD': '111', 'DECOM': '01/01/2020', 'PLACE': 'U1', },  # 0 ignored no previous episode
        {'CHILD': '111', 'DECOM': '11/01/2020', 'PLACE': 'T1', },  # 1
        {'CHILD': '111', 'DECOM': '22/01/2020', 'PLACE': 'A3', },  # 2 fail (T1 -> A3)

        {'CHILD': '123', 'DECOM': '11/01/2020', 'PLACE': 'A4', },  # 4 pass (U1 -> A4)
        {'CHILD': '123', 'DECOM': '01/01/2020', 'PLACE': 'U1', },  # 3

        {'CHILD': '333', 'DECOM': '01/01/2020', 'PLACE': 'U1', },  # 5
        {'CHILD': '333', 'DECOM': '22/01/2020', 'PLACE': 'A3', },  # 6 fail (T2 -> A3)
        {'CHILD': '333', 'DECOM': '11/01/2020', 'PLACE': 'T2', },  # 7

        {'CHILD': '444', 'DECOM': '22/01/2020', 'PLACE': 'A4', },  # 8 fail (X1 -> A4)
        {'CHILD': '444', 'DECOM': '11/01/2020', 'PLACE': 'X1', },  # 9
        {'CHILD': '444', 'DECOM': '01/01/2020', 'PLACE': 'A3', },  # 10 ignored no previous episode

        {'CHILD': '666', 'DECOM': '01/01/2020', 'PLACE': 'A5', },  # 11

        {'CHILD': '777', 'DECOM': '11/01/2020', 'PLACE': 'A4', },  # 12 fail (null -> A4)
        {'CHILD': '777', 'DECOM': '01/01/2020', 'PLACE': pd.NA, },  # 13
    ])
    fake_dfs = {'Episodes': fake_data_episodes}
    error_defn, error_func = validate_336()
    result = error_func(fake_dfs)
    assert result == {'Episodes': [2, 6, 8, 12]}


def test_validate_105():
    fake_header = pd.DataFrame({
        'UASC': [0, 1, pd.NA, '', '0', '1', '2', 2]
    })
    error_defn, error_func = validate_105()

    fake_dfs = {'Header': fake_header, 'metadata': {'file_format': 'csv'}}
    result = error_func(fake_dfs)
    assert result == {}

    fake_dfs = {'Header': fake_header, 'metadata': {'file_format': 'xml'}}
    result = error_func(fake_dfs)
    assert result == {'Header': [2, 3, 6, 7]}


def test_validate_434():
    fake_eps = pd.DataFrame([
        {'CHILD': '111', 'DECOM': '01/01/2020', 'RNE': 'L', 'LS': '--', 'PL_POST': 'ooo', 'URN': '---'},  # 0
        {'CHILD': '111', 'DECOM': '01/02/2020', 'RNE': 'P', 'LS': '--', 'PL_POST': 'ooo', 'URN': '---'},  # 1
        {'CHILD': '111', 'DECOM': '01/12/2020', 'RNE': 'L', 'LS': '--', 'PL_POST': 'ooo', 'URN': '---'},
        # 2 fail: LS same as [3]
        {'CHILD': '111', 'DECOM': '01/03/2020', 'RNE': 'P', 'LS': '--', 'PL_POST': 'ooo', 'URN': '---'},  # 3
        {'CHILD': '222', 'DECOM': '01/01/2020', 'RNE': 'L', 'LS': '--', 'PL_POST': '---', 'URN': '---'},  # 4
        {'CHILD': '222', 'DECOM': '01/02/2020', 'RNE': 'L', 'LS': 'xx', 'PL_POST': '---', 'URN': '---'},  # 5
        {'CHILD': '222', 'DECOM': '01/03/2020', 'RNE': 'L', 'LS': 'oo', 'PL_POST': '---', 'URN': 'xxx'},  # 6 fail: URN
        {'CHILD': '222', 'DECOM': '01/04/2020', 'RNE': 'L', 'LS': 'oo', 'PL_POST': 'xxx', 'URN': 'xxx'},
        # 7 fail: PL_POST
    ])
    fake_eps['PLACE'] = '---'
    fake_eps['PLACE_PROVIDER'] = '---'
    fake_dfs = {'Episodes': fake_eps}
    error_defn, error_func = validate_434()
    result = error_func(fake_dfs)
    assert result == {'Episodes': [2, 6, 7]}


def test_validate_601():
    fake_data_episodes = pd.DataFrame([
        {'CHILD': '101', 'DEC': '01/01/2009', 'REC': 'E45', 'DECOM': '01/01/2009'},  # 0

        {'CHILD': '102', 'DEC': '01/01/2021', 'REC': 'E11', 'DECOM': '01/01/2001'},  # 1 fail
        {'CHILD': '102', 'DEC': '20/12/2021', 'REC': 'E15', 'DECOM': '20/12/2001'},  # 2
        {'CHILD': '102', 'DEC': '03/07/2020', 'REC': 'E12', 'DECOM': '03/01/2019'},  # 3 fail
        {'CHILD': '102', 'DEC': '03/04/2019', 'REC': 'E48', 'DECOM': '03/04/2008'},  # 4

        {'CHILD': '103', 'DEC': '26/05/2020', 'REC': 'E12', 'DECOM': '01/01/2002'},  # 5 pass

        {'CHILD': '104', 'DEC': '10/01/2002', 'REC': 'E11', 'DECOM': '10/01/2002'},  # 6
        {'CHILD': '104', 'DEC': '11/02/2010', 'REC': 'X1', 'DECOM': '11/02/2010'},  # 7
        {'CHILD': '104', 'DEC': '25/01/2002', 'REC': 'X1', 'DECOM': '25/01/2002'},  # 8

        {'CHILD': '105', 'DEC': '25/01/2002', 'REC': 'E47', 'DECOM': '25/01/2002'},  # 9
        {'CHILD': '105', 'DEC': pd.NA, 'REC': 'E45', 'DECOM': pd.NA},  # 10
    ])
    fake_data_ad1 = pd.DataFrame({
        'CHILD': ['101', '102', '103', '104', '105'],
        'DATE_INT': [pd.NA, pd.NA, 'XXX', pd.NA, 'XXX'],
        'DATE_MATCH': [pd.NA, 'XXX', 'XXX', pd.NA, 'XXX'],
        'FOSTER_CARE': [pd.NA, pd.NA, 'XXX', pd.NA, 'XXX'],
        'NB_ADOPTR': [pd.NA, pd.NA, 'XXX', pd.NA, 'XXX'],
        'SEX_ADOPTR': [pd.NA, pd.NA, 'XXX', pd.NA, 'XXX'],
        'LS_ADOPTR': [pd.NA, pd.NA, 'XXX', 'XXX', 'XXX'],
    })
    metadata = {
        'collection_start': '01/04/2020',
        'collection_end': '31/03/2021'
    }
    fake_dfs = {'Episodes': fake_data_episodes, 'AD1': fake_data_ad1, 'metadata': metadata}
    error_defn, error_func = validate_601()
    result = error_func(fake_dfs)

    assert result == {'AD1': [1, ], 'Episodes': [1, 3]}


def test_validate_561():
    fake_placed_adoption = pd.DataFrame([
        {'CHILD': 101, 'DATE_PLACED_CEASED': '26/05/2000', 'DATE_PLACED': '26/05/2019', 'REASON_PLACED_CEASED': 'xx'},
        # 0
        {'CHILD': 102, 'DATE_PLACED_CEASED': '01/07/2018', 'DATE_PLACED': '26/05/2000', 'REASON_PLACED_CEASED': 'xx'},
        # 1
        {'CHILD': 103, 'DATE_PLACED_CEASED': '26/05/2000', 'DATE_PLACED': pd.NA, 'REASON_PLACED_CEASED': 'xx'},  # 2
        {'CHILD': 104, 'DATE_PLACED_CEASED': '26/05/2017', 'DATE_PLACED': '01/02/2016', 'REASON_PLACED_CEASED': 'xx'},
        # 3
        {'CHILD': 106, 'DATE_PLACED_CEASED': pd.NA, 'DATE_PLACED': '26/05/2029', 'REASON_PLACED_CEASED': 'xx'},  # 4
    ])

    fake_pa_last = pd.DataFrame([
        {'CHILD': 101, 'DATE_PLACED_CEASED': pd.NA, 'DATE_PLACED': '26/05/2019', 'REASON_PLACED_CEASED': 'xx'},
        # 0 fail
        {'CHILD': 102, 'DATE_PLACED_CEASED': '01/07/2018', 'DATE_PLACED': '26/05/2000', 'REASON_PLACED_CEASED': 'xx'},
        # 1 fail
        {'CHILD': 103, 'DATE_PLACED_CEASED': '26/05/2000', 'DATE_PLACED': pd.NA, 'REASON_PLACED_CEASED': 'xx'},  # 2
        {'CHILD': 104, 'DATE_PLACED_CEASED': '26/05/2017', 'DATE_PLACED': '01/02/2016', 'REASON_PLACED_CEASED': 'xx'},
        # 3
        {'CHILD': 105, 'DATE_PLACED_CEASED': pd.NA, 'DATE_PLACED': '26/05/2019', 'REASON_PLACED_CEASED': pd.NA},
        # 4 pass
        {'CHILD': 106, 'DATE_PLACED_CEASED': 'xx', 'DATE_PLACED': '01/07/2019', 'REASON_PLACED_CEASED': 'xx'},
        # 5 pass
    ])

    fake_dfs = {'PlacedAdoption': fake_placed_adoption, 'PlacedAdoption_last': fake_pa_last}
    error_defn, error_func = validate_561()
    result = error_func(fake_dfs)
    assert result == {'PlacedAdoption': [0, 1, 3]}


def test_validate_560():
    fake_placed_adoption = pd.DataFrame([
        {'CHILD': 101, 'DATE_PLACED_CEASED': '26/05/2000', 'DATE_PLACED': '26/05/2019'},  # 0 --- FAIL
        {'CHILD': 102, 'DATE_PLACED_CEASED': '01/07/2018', 'DATE_PLACED': '26/05/2000'},  # 1
        {'CHILD': 103, 'DATE_PLACED_CEASED': '26/05/2000', 'DATE_PLACED': pd.NA},  # 2
        {'CHILD': 104, 'DATE_PLACED_CEASED': '26/05/2017', 'DATE_PLACED': '01/02/2016'},  # 3
        {'CHILD': 105, 'DATE_PLACED_CEASED': pd.NA, 'DATE_PLACED': '27/05/2019'},  # 4 --- FAIL
        {'CHILD': 106, 'DATE_PLACED_CEASED': '34rd/Dec/-1000A.D', 'DATE_PLACED': '34rd/Dec/-1000A.D'},  # 5
        {'CHILD': 107, 'DATE_PLACED_CEASED': 'different', 'DATE_PLACED': 'also different'},  # 6
    ])
    fake_pa_last = pd.DataFrame([
        {'CHILD': 101, 'DATE_PLACED_CEASED': pd.NA, 'DATE_PLACED': '26/05/2000'},  # 0
        {'CHILD': 102, 'DATE_PLACED_CEASED': '01/07/2018', 'DATE_PLACED': '26/05/2000'},  # 1
        {'CHILD': 103, 'DATE_PLACED_CEASED': '26/05/2000', 'DATE_PLACED': pd.NA},  # 2
        {'CHILD': 104, 'DATE_PLACED_CEASED': '26/05/2017', 'DATE_PLACED': '01/02/2016'},  # 3
        {'CHILD': 105, 'DATE_PLACED_CEASED': pd.NA, 'DATE_PLACED': '26/05/2019'},  # 4
        {'CHILD': 106, 'DATE_PLACED_CEASED': pd.NA, 'DATE_PLACED': '34rd/Dec/-1000A.D'},  # 5
        {'CHILD': 107, 'DATE_PLACED_CEASED': '34rd/Dec/-1000A.D', 'DATE_PLACED': '20/20/2020'},  # 6
    ])
    fake_dfs = {'PlacedAdoption': fake_placed_adoption, 'PlacedAdoption_last': fake_pa_last}
    error_defn, error_func = validate_560()
    result = error_func(fake_dfs)
    assert result == {'PlacedAdoption': [0, 4]}


def test_validate_545():
    fake_data_episodes = pd.DataFrame([
        {'CHILD': 101, 'DECOM': '01/03/1980', 'DEC': '31/03/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},  # CLA
        {'CHILD': 102, 'DECOM': '01/03/1980', 'DEC': '30/03/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},  # CLA
        {'CHILD': 103, 'DECOM': '01/03/1980', 'DEC': '01/01/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},  # CLA
        {'CHILD': 104, 'DECOM': '01/02/1970', 'DEC': pd.NA, 'LS': 'o', 'REC': '!!', 'RNE': 'o'},  # CLA
        {'CHILD': 105, 'DECOM': '01/03/1979', 'DEC': '01/01/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},  # CLA
        {'CHILD': 105, 'DECOM': '01/01/1981', 'DEC': '01/01/1983', 'LS': 'o', 'REC': 'oo', 'RNE': 'o'},  # CLA
        {'CHILD': 106, 'DECOM': '01/03/1980', 'DEC': '01/01/1982', 'LS': 'V3', 'REC': 'X1', 'RNE': 'o'},  # not CLA: V3
        {'CHILD': 107, 'DECOM': '01/03/1980', 'DEC': '01/01/1982', 'LS': 'V3', 'REC': '!!', 'RNE': 'o'},  # not CLA: REC
    ])
    fake_data = pd.DataFrame({
        'CHILD': [101, 102, 103, 104,
                  105, 106, 107, 333],
        'DOB': ['08/03/1973', '22/06/1977', pd.NA, '13/10/2000',
                '10/01/1978', '01/01/1978', '01/01/1978', '01/01/1978'],
        'HEALTH_CHECK': [pd.NA, pd.NA, pd.NA, 1,
                         pd.NA, pd.NA, pd.NA, pd.NA],
        # 0 pass: over 5
        # 1 fail : CLA is true, under 5, and HEALTH_CHECK is not provided
        # 2 pass: DOB is nan
        # 3 pass: under 5 (born in future), but HEALTH_CHECK provided
        # 4 fail: CLA is true, under 5, and HEALTH_CHECK is not provided
        # 5 pass: not CLA
        # 6 pass: not CLA
        # 7 pass: not in episodes -> not CLA
    })

    metadata = {'collection_start': '01/04/1980', 'collection_end': '31/03/1981'}

    fake_dfs = {'OC2': fake_data, 'metadata': metadata, 'Episodes': fake_data_episodes}

    error_defn, error_func = validate_545()

    result = error_func(fake_dfs)

    assert result == {'OC2': [1, 4]}


def test_validate_546():
    fake_data_episodes = pd.DataFrame([
        {'CHILD': 101, 'DECOM': '01/03/1980', 'DEC': '31/03/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},
        {'CHILD': 102, 'DECOM': '01/03/1980', 'DEC': '30/03/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},
        {'CHILD': 103, 'DECOM': '01/03/1980', 'DEC': '01/01/1981', 'LS': 'V3', 'REC': 'X1', 'RNE': 'o'},  # False
        {'CHILD': 104, 'DECOM': '01/02/1970', 'DEC': pd.NA, 'LS': 'o', 'REC': '!!', 'RNE': 'o'},

        {'CHILD': 105, 'DECOM': '01/03/1979', 'DEC': '01/01/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},
    ])
    fake_data = pd.DataFrame({
        'CHILD': [101, 102, 103, 104, 105],
        'DOB': ['08/03/1963', '22/06/1957', pd.NA, '13/10/2000', '10/01/1948'],
        'HEALTH_CHECK': [1, 1, pd.NA, 1, pd.NA],
        # 0 fail because conditions are met but HEALTH_CHECK is provided
        # 1 fail because conditions are met but HEALTH_CHECK is provided
        # 2 ignore: DOB is nan
        # 3 ignore: CLA is false
        # 4 pass
    })

    metadata = {'collection_start': '01/04/1980', 'collection_end': '31/03/1981'}

    fake_dfs = {'OC2': fake_data, 'metadata': metadata, 'Episodes': fake_data_episodes}

    error_defn, error_func = validate_546()

    result = error_func(fake_dfs)

    assert result == {'OC2': [0, 1]}


def test_validate_1003():
    fake_data_episodes = pd.DataFrame([
        {'CHILD': 101, 'DECOM': '01/03/1980', 'RNE': 'S'},  # 0 fail

        {'CHILD': 102, 'DECOM': '01/03/1980', 'RNE': 'o'},
        {'CHILD': 102, 'DECOM': '01/03/1980', 'RNE': 'S'},  # 2 ignore DATE_PLACED is nan

        {'CHILD': 103, 'DECOM': '01/02/1970', 'RNE': 'o'},
        {'CHILD': 103, 'DECOM': '01/03/1979', 'RNE': 'S'},  # 4 fail
        {'CHILD': 103, 'DECOM': '01/01/1981', 'RNE': 'S'},

        {'CHILD': 104, 'DECOM': '01/03/1979', 'RNE': 'o'},  # ignore no RNE is S
        {'CHILD': 104, 'DECOM': '01/01/1981', 'RNE': 'o'},

        {'CHILD': 105, 'DECOM': '01/03/1979', 'RNE': 'o'},
        {'CHILD': 105, 'DECOM': '01/01/1981', 'RNE': 'o'},
        {'CHILD': 105, 'DECOM': '01/01/1981', 'RNE': 'S'},  # 10 pass
    ])
    fake_placed_adoption = pd.DataFrame([
        {'CHILD': 101, 'DATE_PLACED': '26/05/1978'},  # 0 fail
        {'CHILD': 102, 'DATE_PLACED': pd.NA},  # 1
        {'CHILD': 103, 'DATE_PLACED': '26/05/1970'},  # 2 fail
        {'CHILD': 104, 'DATE_PLACED': '01/02/1960'},  # 3
        {'CHILD': 105, 'DATE_PLACED': '26/05/2019'},  # 4
    ])
    fake_dfs = {'Episodes': fake_data_episodes, 'PlacedAdoption': fake_placed_adoption}
    error_defn, error_func = validate_1003()
    result = error_func(fake_dfs)
    assert result == {'Episodes': [0, 4], 'PlacedAdoption': [0, 2]}


def test_validate_334():
    fake_data_episodes = pd.DataFrame([
        {'CHILD': 101, 'DECOM': '01/03/1980', 'RNE': 'S'},  # 0 fail

        {'CHILD': 102, 'DECOM': '01/03/1980', 'RNE': 'o'},
        {'CHILD': 102, 'DECOM': '01/03/1980', 'RNE': 'S'},  # 2 ignore DATE_PLACED is nan

        {'CHILD': 103, 'DECOM': '01/02/1970', 'RNE': 'o'},
        {'CHILD': 103, 'DECOM': '01/03/1979', 'RNE': 'S'},
        {'CHILD': 103, 'DECOM': '01/01/1980', 'RNE': 'S'},  # 5 pass

        {'CHILD': 104, 'DECOM': '01/03/1979', 'RNE': 'o'},  # ignore no RNE is S
        {'CHILD': 104, 'DECOM': '01/01/1981', 'RNE': 'o'},

        {'CHILD': 105, 'DECOM': '01/03/1979', 'RNE': 'o'},
        {'CHILD': 105, 'DECOM': '01/01/2020', 'RNE': 'S'},  # 9 fail
        {'CHILD': 105, 'DECOM': '26/05/2021', 'RNE': 'o'},
    ])
    fake_placed_ad1 = pd.DataFrame([
        {'CHILD': 101, 'DATE_INT': '26/05/1978'},  # 0 fail
        {'CHILD': 102, 'DATE_INT': pd.NA},  # 1
        {'CHILD': 103, 'DATE_INT': '26/05/1981'},  # 2 pass
        {'CHILD': 104, 'DATE_INT': '01/02/1960'},  # 3
        {'CHILD': 105, 'DATE_INT': '26/05/2019'},  # 4 fail
    ])
    fake_dfs = {'Episodes': fake_data_episodes, 'AD1': fake_placed_ad1}
    error_defn, error_func = validate_334()
    result = error_func(fake_dfs)
    assert result == {'Episodes': [0, 9], 'AD1': [0, 4]}


def test_validate_559():
    metadata = {
        'collection_start': '01/04/2020',
        'collection_end': '31/03/2021'
    }
    fake_placed_adoption = pd.DataFrame([
        {'CHILD': 101, 'DATE_PLACED': '26/05/2022'},  # 0
        {'CHILD': 102, 'DATE_PLACED': '26/05/2021'},  # 1
        {'CHILD': 103, 'DATE_PLACED': pd.NA},  # 2
        {'CHILD': 104, 'DATE_PLACED': '01/02/2016'},  # 3
        {'CHILD': 105, 'DATE_PLACED': '26/05/2019'},  # 4
    ])
    fake_last_pa = pd.DataFrame([
        {'CHILD': 101, 'DATE_PLACED': '26/05/2000'},  # 0
        {'CHILD': 102, 'DATE_PLACED': pd.NA},  # 1
        {'CHILD': 103, 'DATE_PLACED': '26/05/2000'},  # 2
        {'CHILD': 104, 'DATE_PLACED': '01/02/2016'},  # 3
        {'CHILD': 105, 'DATE_PLACED': pd.NA},  # 4
    ])
    fake_dfs = {'PlacedAdoption': fake_placed_adoption, 'PlacedAdoption_last': fake_last_pa, 'metadata': metadata}
    error_defn, error_func = validate_559()
    result = error_func(fake_dfs)
    assert result == {'PlacedAdoption': [4, ]}


def test_validate_521():
    fake_ad1 = pd.DataFrame({
        "DATE_INT": ['08/03/2020', '22/07/2020', '13/10/2021', '22/06/2020', pd.NA, ],
        "CHILD": ['111', '123', '333', '444', '678', ]})
    fake_data_episodes = pd.DataFrame([
        {'CHILD': '111', 'DECOM': '01/01/2020', 'PLACE': 'A6', },  # 0 pass
        {'CHILD': '111', 'DECOM': '01/11/2020', 'PLACE': 'A5', },  # 1 fail
        {'CHILD': '111', 'DECOM': '22/01/2020', 'PLACE': 'X1', },  # 2 ignore PLACE not in list

        {'CHILD': '123', 'DECOM': pd.NA, 'PLACE': 'A5', },  # 3 ignore DECOM is nan
        {'CHILD': '123', 'DECOM': '11/01/2020', 'PLACE': 'X1', },  # 4 ignore PLACE not in list

        {'CHILD': '333', 'DECOM': '01/01/2020', 'PLACE': 'A6', },  # 5 pass
        {'CHILD': '333', 'DECOM': '22/01/2020', 'PLACE': 'X1', },  # 6 ignore PLACE not in list
        {'CHILD': '333', 'DECOM': '11/01/2020', 'PLACE': 'U1', },  # 7 ignore PLACE not in list

        {'CHILD': '444', 'DECOM': '22/06/2020', 'PLACE': 'A3', },  # 8 fail
        {'CHILD': '444', 'DECOM': '11/01/2020', 'PLACE': 'X1', },  # 9 ignore PLACE not in list
        {'CHILD': '444', 'DECOM': '01/01/2020', 'PLACE': 'A3', },  # 10 pass

        {'CHILD': '678', 'DECOM': '01/01/2020', 'PLACE': 'A4', },  # 11 ignore DATE_INT is nan
    ])
    fake_dfs = {'Episodes': fake_data_episodes, 'AD1': fake_ad1}
    error_defn, error_func = validate_521()
    result = error_func(fake_dfs)
    assert result == {'Episodes': [1, 8], 'AD1': [0, 3]}


def test_validate_1000():
    fake_episodes_prev = pd.DataFrame({
        'CHILD': ['101', '101', '102', '102', '103'],
        'REC': ['X1', pd.NA, pd.NA, 'E2', 'E4a']
    })

    fake_episodes = pd.DataFrame({
        'CHILD': ['104', '105'],
        'REC': ['X1', 'E2']
    })

    fake_oc3 = pd.DataFrame({
        'CHILD': ['101', '102', '103', '104', '105']
    })

    erro_defn, error_func = validate_1000()

    fake_dfs = {'Episodes': fake_episodes, 'Episodes_last': fake_episodes_prev, 'OC3': fake_oc3}
    result = error_func(fake_dfs)
    assert result == {'OC3': [1, 4]}

    fake_dfs = {'Episodes': fake_episodes, 'OC3': fake_oc3}
    result = error_func(fake_dfs)
    assert result == {'OC3': [4]}


def test_validate_579():
    fake_adopt_place = pd.DataFrame([
        {'CHILD': '111', 'DATE_PLACED': '01/06/2020', 'DATE_PLACED_CEASED': '05/06/2020'},  # 0
        {'CHILD': '111', 'DATE_PLACED': '04/06/2020', 'DATE_PLACED_CEASED': pd.NA},  # 1 Fails overlaps
        {'CHILD': '222', 'DATE_PLACED': '03/06/2020', 'DATE_PLACED_CEASED': '04/06/2020'},  # 2
        {'CHILD': '222', 'DATE_PLACED': '04/06/2020', 'DATE_PLACED_CEASED': pd.NA},  # 3
        {'CHILD': '222', 'DATE_PLACED': '07/06/2020', 'DATE_PLACED_CEASED': '09/06/2020'},
        # 4 Fails, previous end is null
        {'CHILD': '333', 'DATE_PLACED': '02/06/2020', 'DATE_PLACED_CEASED': '04/06/2020'},  # 5
        {'CHILD': '333', 'DATE_PLACED': '03/06/2020', 'DATE_PLACED_CEASED': '09/06/2020'},  # 6 Fails overlaps
        {'CHILD': '555', 'DATE_PLACED': pd.NA, 'DATE_PLACED_CEASED': '05/06/2020'},  # 7
        {'CHILD': '555', 'DATE_PLACED': pd.NA, 'DATE_PLACED_CEASED': '05/06/2020'},  # 8
    ])

    fake_dfs = {'PlacedAdoption': fake_adopt_place}

    error_defn, error_func = validate_579()

    result = error_func(fake_dfs)

    assert result == {'PlacedAdoption': [1, 4, 6]}


def test_validate_351():
    fake_data_header = pd.DataFrame({
        'CHILD': ['101', '102', '103', '104', '105', ],
        'DOB': [pd.NA, '11/11/2020', '03/10/1995', '01/04/2000', '01/01/1999', ]
    })
    metadata = {
        'collection_start': '01/04/2021',
    }
    fake_dfs = {'Header': fake_data_header, 'metadata': metadata}

    error_defn, error_func = validate_351()
    result = error_func(fake_dfs)

    assert result == {'Header': [2, 4]}


def test_validate_301():
    fake_data_header = pd.DataFrame([
        {'CHILD': 101, 'DOB': '01/07/2021', },  # 0 fail
        {'CHILD': 102, 'DOB': '02/06/2000', },  # 1
        {'CHILD': 103, 'DOB': '03/06/2000', },  # 2
        {'CHILD': 104, 'DOB': '04/06/2022', },  # 3 fail
        {'CHILD': 105, 'DOB': pd.NA, },  # 4
    ])

    metadata = {
        'collection_start': '01/04/2020',
        'collection_end': '31/03/2021'
    }

    fake_dfs = {'Header': fake_data_header, 'metadata': metadata}
    error_defn, error_func = validate_301()
    result = error_func(fake_dfs)
    assert result == {'Header': [0, 3]}


def test_validate_577():
    fake_data_mis = pd.DataFrame([
        {'CHILD': '1', 'MIS_START': '01/01/1981', 'MIS_END': pd.NA, },  # 0

        {'CHILD': '2', 'MIS_START': '01/01/1981', 'MIS_END': '02/06/2020', },  # 1

        {'CHILD': '3', 'MIS_START': '01/01/1981', 'MIS_END': '03/06/2022', },  # 2 fail: fail1 fail2
        {'CHILD': '3', 'MIS_START': '01/01/1981', 'MIS_END': '03/06/2020', },  # 3 pass: fail with the first, pass with the second

        {'CHILD': '4', 'MIS_START': '01/01/1981', 'MIS_END': '04/06/2020', },  # 4

        {'CHILD': '5', 'MIS_START': '01/01/1981', 'MIS_END': '01/01/1982', },  # 5 passes with full period of care DECOM-DEC (7/8) and 9
        {'CHILD': '5', 'MIS_START': '01/01/1981', 'MIS_END': '01/01/2000', },  # 6 pass: fails with first set of episodes(7/8 poc), but passes with next period of care (9)

        {'CHILD': '6', 'MIS_START': '01/01/1981', 'MIS_END': '01/01/1981', },  # 7 fail when compared with DECOM
        {'CHILD': '7', 'MIS_START': pd.NA, 'MIS_END': '01/01/1981', },  # 8 ignore fail: MIS_START is NaN
        {'CHILD': '8', 'MIS_START': '01/01/1981', 'MIS_END': pd.NA, }, # 9 fail: MIS_END is nan

        {'CHILD': '9', 'MIS_START': '01/01/2020', 'MIS_END': pd.NA, },  # 10 fail: MIS_END is nan
        {'CHILD': '9', 'MIS_START': '01/01/2021', 'MIS_END': pd.NA, }, # 11 pass: ongoing mis-ep during ongoing poc
        {'CHILD': '9', 'MIS_START': '04/06/2020', 'MIS_END': '04/06/2021', },  # 12 pass: ends during a poc (?!)

    ])
    fake_data_eps = pd.DataFrame([
        {'CHILD': '1', 'DECOM':'01/04/1977', 'DEC': '31/03/1981', 'LS': 'o', 'REC': 'X1', }, # 0
        {'CHILD': '2', 'DECOM':'01/04/1979', 'DEC': '30/03/1981', 'LS': 'o', 'REC': pd.NA, }, # 1
        {'CHILD': '88','DECOM':'01/05/1980', 'DEC': '01/01/1981', 'LS': 'o', 'REC': 'xx', },  # 2

        {'CHILD': '3', 'DECOM':'01/04/1980', 'DEC': '01/01/1981', 'LS': 'V3', 'REC': 'kk', },  # 3
        {'CHILD': '3', 'DECOM':'01/04/2020', 'DEC': '01/01/2021', 'LS': 'V3', 'REC': 'kk', }, # 4
        {'CHILD': '3', 'DECOM':'01/01/2021', 'DEC': '05/10/2021', 'LS': 'V3', 'REC': 'kk', }, # 5

        {'CHILD': '4', 'DECOM':'01/04/1981', 'DEC': pd.NA, 'LS': 'o', 'REC': '!!', },  # 6

        {'CHILD': '5', 'DECOM':'01/04/1978', 'DEC': '01/01/1981', 'LS': 'o', 'REC': 'xx', },  # 7 --poc start
        {'CHILD': '5', 'DECOM':'01/01/1981', 'DEC': '01/01/1990', 'LS': 'o', 'REC': 'xx', },  # 8  poc end--
        {'CHILD': '5', 'DECOM':'01/04/1983', 'DEC': '04/06/2020', 'LS': 'o', 'REC': 'kk', },  # 9

        {'CHILD': '6', 'DECOM':'01/04/1983', 'DEC': '04/06/2020', 'LS': 'o', 'REC': 'kk', }, # 10

        {'CHILD': '7', 'DECOM':'01/04/1983', 'DEC': '04/06/2020', 'LS': 'o', 'REC': 'kk', }, # 11

        {'CHILD': '8', 'DECOM':'01/04/1983', 'DEC': '04/06/2020', 'LS': 'o', 'REC': 'xx', }, # 12

        {'CHILD': '9', 'DECOM': '01/01/2020', 'DEC': '04/06/2020', 'LS': 'o', 'REC': '<--', },  # 10
        {'CHILD': '9', 'DECOM': '04/06/2020', 'DEC': '11/08/2020', 'LS': 'o', 'REC': '-', },  # 10
        {'CHILD': '9', 'DECOM': '11/08/2020', 'DEC': '01/12/2020', 'LS': 'o', 'REC': '-->', },  # 10
        {'CHILD': '9', 'DECOM': '22/12/2020', 'DEC': '25/12/2020', 'LS': 'o', 'REC': '<->', },  # 10
        {'CHILD': '9', 'DECOM': '01/01/2021', 'DEC': '22/02/2021', 'LS': 'o', 'REC': '<--', },  # 10
        {'CHILD': '9', 'DECOM': '22/02/2021', 'DEC': '08/08/2021', 'LS': 'V3', 'REC': '-', },  # 10
        {'CHILD': '9', 'DECOM': '08/08/2021', 'DEC': pd.NA, 'LS': 'o', 'REC': '--o', },  # 10

    ])

    fake_dfs = {'Episodes': fake_data_eps, 'Missing': fake_data_mis}
    error_defn, error_func = validate_577()
    result = error_func(fake_dfs)

    assert result == {'Missing': [0, 1, 2, 7, 9, 10]}


def test_validate_460():
    fake_data = pd.DataFrame({
        'CHILD': ['101', '102', '101', '102', '103', '104'],
        'REC': ['E17', 'E17', 'X1', pd.NA, 'E17', 'E17'],
        'DEC': ['16/03/2023', '17/06/2020', '20/03/2020', pd.NA, '23/08/2020', '23/08/2020'],
    })

    fake_data_child = pd.DataFrame({
        'CHILD': ['101', '102', '103', '104'],
        'DOB': ['16/03/2005', '23/09/2002', '31/12/2000', pd.NA],
    })

    fake_dfs = {'Episodes': fake_data, 'Header': fake_data_child}

    error_defn, error_func = validate_460()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [1]}


def test_validate_578():
    fake_data_mis = pd.DataFrame([
        {'CHILD': '1', 'MIS_START': '01/06/2020', },  # 0 fail
        {'CHILD': '2', 'MIS_START': '02/06/2020', },  # 1 fail

        {'CHILD': '3', 'MIS_START': '03/06/2022', },  # 2 fail: fail1 fail2
        {'CHILD': '3', 'MIS_START': '03/06/2020', },  # 3 fail with the first, pass with the second : pass

        {'CHILD': '4', 'MIS_START': '04/06/2020', },  # 4

        {'CHILD': '5', 'MIS_START': '01/01/1982', },  # 5 passes with full period of care DECOM-DEC (7/8) and 9
        {'CHILD': '5', 'MIS_START': '01/01/2000', },  # 6 pass: fails with first set of episodes(7/8 poc), but passes with next period of care (9)

        {'CHILD': '6', 'MIS_START': '01/01/1981', },  # 7 fail when compared with DECOM
        {'CHILD': '77', 'MIS_START': '01/01/1981', },  # 8 pass
        {'CHILD': '8888', 'MIS_START': '01/01/2049', },  # 8 pass
    ])
    fake_data_eps = pd.DataFrame([
        {'CHILD': '1', 'DECOM':'01/04/1977', 'DEC': '31/03/1981', 'LS': 'o', 'REC': 'X1', }, # 0
        {'CHILD': '2', 'DECOM':'01/04/1979', 'DEC': '30/03/1981', 'LS': 'o', 'REC': pd.NA, }, # 1
        {'CHILD': '88','DECOM':'01/05/1980', 'DEC': '01/01/1981', 'LS': 'o', 'REC': 'xx', },  # 2

        {'CHILD': '3', 'DECOM':'01/04/1980', 'DEC': '01/01/1981', 'LS': 'V3', 'REC': 'kk', },  # 3
        {'CHILD': '3', 'DECOM':'01/04/2020', 'DEC': '01/01/2021', 'LS': 'V3', 'REC': 'kk', }, # 4 --not poc
        {'CHILD': '3', 'DECOM':'01/01/2021', 'DEC': '05/10/2021', 'LS': 'V3', 'REC': 'kk', }, # 5 due to LS value--

        {'CHILD': '4', 'DECOM':'01/04/1981', 'DEC': pd.NA, 'LS': 'o', 'REC': '!!', },  # 6

        {'CHILD': '5', 'DECOM':'01/04/1978', 'DEC': '01/01/1981', 'LS': 'o', 'REC': 'X1', },  # 7 --poc start
        {'CHILD': '5', 'DECOM':'01/01/1981', 'DEC': '01/01/1990', 'LS': 'o', 'REC': 'xx', },  # 8  poc end--
        {'CHILD': '5', 'DECOM':'01/04/1983', 'DEC': '04/06/2020', 'LS': 'o', 'REC': 'kk', },  # 9

        {'CHILD': '6', 'DECOM':'01/04/1983', 'DEC': '04/06/2020', 'LS': 'o', 'REC': 'kk', }, # 10

        {'CHILD': '8888', 'DECOM': '01/04/1983', 'DEC': '04/06/2020', 'LS': 'o', 'REC': 'kk', },  # 10
        {'CHILD': '8888', 'DECOM': '04/06/2020', 'DEC': pd.NA, 'LS': 'o', 'REC': 'kk', },  # 10

    ])

    fake_dfs = {'Episodes': fake_data_eps, 'Missing': fake_data_mis}
    error_defn, error_func = validate_578()
    result = error_func(fake_dfs)

    assert result == {'Missing': [0, 1, 2, 7]}

def test_validate_391():
    fake_data_oc3 = pd.DataFrame({
        'CHILD': ['A', 'B', 'C', 'D', 'E'],
        'DOB': ['01/01/2001', '01/01/2016', '20/12/1997', '01/01/2002', '03/01/2004', ],
        'IN_TOUCH': ['DIED', 'Yes', 'RHOM', pd.NA, pd.NA],
        'ACTIV': [pd.NA, pd.NA, 'XXX', pd.NA, pd.NA],
        'ACCOM': [pd.NA, pd.NA, pd.NA, 'XXX', pd.NA],
    })
    metadata = {
        'collection_end': '31/03/2018'
    }

    fake_dfs = {'OC3': fake_data_oc3, 'metadata': metadata}
    error_defn, error_func = validate_391()
    result = error_func(fake_dfs)
    assert result == {'OC3': [1, 3]}


def test_validate_625():
    fake_data_header = pd.DataFrame({
        'CHILD': ['101', '102', '103'],
        'MC_DOB': ['01/11/2021', '19/12/2016', pd.NA],
        # 0 MC_DOB > collection_end FAIL
        # 1 MC_DOB < collection_end but > DEC of latest episode FAIL
        # 2 MC_DOB not provided IGNORE
    })
    fake_data_episodes = pd.DataFrame({
        'CHILD': ['101', '101', '102', '102', '103', '103', '103'],
        'DEC': ['02/12/2021', '11/11/2012', '03/10/2014', '11/11/2015', '01/01/2020', '11/11/2020', '01/02/2020']
    })
    metadata = {
        'collection_end': '31/03/2021'
    }
    fake_dfs = {'metadata': metadata, 'Episodes': fake_data_episodes, 'Header': fake_data_header}
    error_defn, error_func = validate_625()
    result = error_func(fake_dfs)
    assert result == {'Episodes': [0, 3], 'Header': [0, 1]}


def test_validate_514():
    fake_data = pd.DataFrame({
        'LS_ADOPTR': ['L0', 'xx', 'L0', pd.NA, 'L0'],
        'SEX_ADOPTR': ['M1', 'F1', 'xx', pd.NA, 'xxx'],
    })

    fake_dfs = {'AD1': fake_data}

    error_defn, error_func = validate_514()

    result = error_func(fake_dfs)

    assert result == {'AD1': [2, 4, ]}


def test_validate_632():
    fake_data_prevperm = pd.DataFrame({
        'CHILD': ['101', '102', '103', '104', '105', '106', '107', '108', '109', '110'],
        'DATE_PERM': ['xx/10/2011', '17/06/2001', '01/05/2000', pd.NA, '05/ZZ/2020', 'ZZ/05/2021', 'ZZ/ZZ/ZZZZ',
                      'ZZ/ZZ/1993', 'ZZ/ZZ/ZZ', '01/13/2000'],
    })

    fake_data_episodes = pd.DataFrame([
        {'CHILD': '101', 'DECOM': '20/10/2011', },  # 0 - fail! DATE_PERM is not in appropriate format
        {'CHILD': '102', 'DECOM': '19/11/2021', },  # 1 pass
        {'CHILD': '102', 'DECOM': '17/06/2001', },  # 2 - fail! DATE_PERM == DECOM
        {'CHILD': '103', 'DECOM': pd.NA, },  # 3 ignore DECOM is nan
        {'CHILD': '104', 'DECOM': '11/09/2015', },  # 4 pass DATE_PERM is nan
        {'CHILD': '105', 'DECOM': '01/03/2021', },  # 5 - fail! DATE_PERM wrong format
        {'CHILD': '106', 'DECOM': '01/07/2021', },  # 6 pass
        {'CHILD': '107', 'DECOM': '01/07/2021', },  # 7 pass
        {'CHILD': '108', 'DECOM': '01/07/2021', },  # 8 pass
        {'CHILD': '109', 'DECOM': '01/07/2021', },  # 9 - fail! wrong zeds in DATE_PERM
        {'CHILD': '110', 'DECOM': '01/07/2021', },  # 10 - fail! wrong month in DATE_PERM
    ])
    fake_dfs = {'PrevPerm': fake_data_prevperm, 'Episodes': fake_data_episodes}
    error_defn, error_func = validate_632()
    result = error_func(fake_dfs)
    # desired
    assert result == {'Episodes': [0, 2, 5, 9, 10], 'PrevPerm': [0, 1, 4, 8, 9]}


def test_validate_165():
    fake_data_oc3 = pd.DataFrame({
        'CHILD': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
        'IN_TOUCH': [pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, 'YES', pd.NA, pd.NA, pd.NA],
        'ACTIV': [pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, 'XXX', pd.NA, pd.NA, pd.NA],
        'ACCOM': [pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, 'XXX', pd.NA, pd.NA],
    })
    fake_data_episodes = pd.DataFrame([
        {'CHILD': 101, 'DECOM': '01/01/2020', 'DEC': '01/05/2020', 'LS': 'C2'},  # 0
        {'CHILD': 102, 'DECOM': '11/01/2020', 'DEC': '11/05/2020', 'LS': 'C2'},  # 1
        {'CHILD': 103, 'DECOM': '30/03/2020', 'DEC': '30/05/2020', 'LS': 'C2'},  # 2
        {'CHILD': 103, 'DECOM': '30/03/2020', 'DEC': '30/05/2020', 'LS': 'C2'},  # 2
        {'CHILD': 104, 'DECOM': '01/01/2020', 'DEC': '01/05/2020', 'LS': 'C2'},  # 3
        {'CHILD': 105, 'DECOM': '11/05/2020', 'DEC': '11/08/2020', 'LS': 'C2'},  # 4
        {'CHILD': 105, 'DECOM': '01/01/2020', 'DEC': '01/05/2020', 'LS': 'C2'},  # 5
        {'CHILD': 106, 'DECOM': '22/01/2020', 'DEC': '22/05/2020', 'LS': 'C2'},  # 6
        {'CHILD': 107, 'DECOM': '11/01/2020', 'DEC': '11/05/2020', 'LS': 'C2'},  # 7
        {'CHILD': 108, 'DECOM': '22/01/2020', 'DEC': '22/05/2020', 'LS': 'C2'},  # 8
        {'CHILD': 109, 'DECOM': '25/03/2020', 'DEC': '25/03/2020', 'LS': 'C2'},  # 9
        {'CHILD': 110, 'DECOM': '01/01/2020', 'DEC': '01/05/2020', 'LS': 'V3'},  # 10
        {'CHILD': 110, 'DECOM': '01/11/2021', 'DEC': '01/11/2021', 'LS': 'C2'},  # 11
        {'CHILD': 111, 'DECOM': '01/11/2020', 'DEC': '01/11/2020', 'LS': 'V3'},  # 12
    ])
    fake_data_header = pd.DataFrame([
        {'CHILD': 101, 'SEX': '1', 'MOTHER': pd.NA},  # 0 pass: male no value
        {'CHILD': 102, 'SEX': '2', 'MOTHER': '0'},  # 1 pass
        {'CHILD': 103, 'SEX': '2', 'MOTHER': 0},  # 2 pass
        {'CHILD': 104, 'SEX': '2', 'MOTHER': 1},  # 3 pass
        {'CHILD': 105, 'SEX': '2', 'MOTHER': pd.NA},  # 4 fail: no value
        {'CHILD': 106, 'SEX': '2', 'MOTHER': '2'},  # 5 fail: invalid value
        {'CHILD': 107, 'SEX': '1', 'MOTHER': '1'},  # 6 fail: male value
        {'CHILD': 108, 'SEX': '2', 'MOTHER': pd.NA},  # 7 fail: has OC3 data but also has episode in collection year
        {'CHILD': 109, 'SEX': '2', 'MOTHER': pd.NA},  # 8 pass: has OC3 and no episode in collection year
        {'CHILD': 110, 'SEX': '2', 'MOTHER': 1},
        # 9 pass: no non-V3/V4 episode in collection year and no OC3
        {'CHILD': 111, 'SEX': '2', 'MOTHER': pd.NA},  # 10 pass: V3 episode
    ])
    metadata = {
        'collection_start': '01/04/2020',
        'collection_end': '31/03/2021'
    }
    fake_dfs = {'Header': fake_data_header, 'Episodes': fake_data_episodes, 'OC3': fake_data_oc3, 'metadata': metadata}
    error_defn, error_func = validate_165()
    result = error_func(fake_dfs)

    assert result == {'Header': [4, 5, 6, 7], 'OC3': [4, 5, 6, 7]}


def test_validate_1014():
    fake_data_uasc = pd.DataFrame([
        {'CHILD': 101, 'DOB': '01/06/2000', 'DUC': '05/06/2019'},  # 0
        {'CHILD': 102, 'DOB': '02/06/2000', 'DUC': pd.NA},  # 1
        {'CHILD': 105, 'DOB': '03/06/2000', 'DUC': '01/06/2015'},  # 2
        {'CHILD': 107, 'DOB': '04/06/2000', 'DUC': '02/06/2020'},  # 3
        {'CHILD': 110, 'DOB': pd.NA, 'DUC': '05/06/2020'},  # 4 Fails
        {'CHILD': 111, 'DOB': pd.NA, 'DUC': '05/06/2020'},  # 5 Fails
    ])
    fake_data_oc3 = pd.DataFrame({
        'CHILD': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
        'IN_TOUCH': [pd.NA, 'YES', 'YES', pd.NA, 'Yes', 'No', 'YES', 'YES', pd.NA, pd.NA, '!!'],
        'ACTIV': [pd.NA, pd.NA, 'XXX', pd.NA, 'XXX', pd.NA, pd.NA, 'XXX', pd.NA, 'XXX', '!!'],
        'ACCOM': [pd.NA, pd.NA, pd.NA, 'XXX', 'XXX', pd.NA, pd.NA, pd.NA, 'XXX', pd.NA, pd.NA],
    })
    fake_data_episodes = pd.DataFrame([
        {'CHILD': 101, 'DECOM': '01/01/2020', 'DEC': '01/01/2020', },  # 0
        {'CHILD': 102, 'DECOM': '11/01/2020', 'DEC': '11/01/2020', },  # 1
        {'CHILD': 103, 'DECOM': '30/03/2020', 'DEC': '30/03/2020', },  # 2
        {'CHILD': 104, 'DECOM': '01/01/2020', 'DEC': '01/01/2020', },  # 3

        {'CHILD': 105, 'DECOM': '11/05/2020', 'DEC': '11/05/2020', },  # 4 eps in range
        {'CHILD': 105, 'DECOM': '01/01/2020', 'DEC': '01/01/2020', },  # 5

        {'CHILD': 106, 'DECOM': '22/01/2020', 'DEC': '22/01/2020', },  # 6
        {'CHILD': 107, 'DECOM': '11/01/2020', 'DEC': '11/01/2020', },  # 7
        {'CHILD': 108, 'DECOM': '22/01/2020', 'DEC': '22/01/2020', },  # 8
        {'CHILD': 109, 'DECOM': '25/03/2020', 'DEC': '25/03/2020', },  # 9

        {'CHILD': 110, 'DECOM': '01/01/2020', 'DEC': '01/01/2020', },  # 10 fail.
        {'CHILD': 110, 'DECOM': '01/11/2021', 'DEC': '01/11/2021', },  # 11

        {'CHILD': 111, 'DECOM': '01/11/2019', 'DEC': '31/03/2021', },  # 12
    ])

    metadata = {
        'collection_start': '01/04/2020',
        'collection_end': '31/03/2021'
    }
    fake_dfs = {'UASC': fake_data_uasc, 'Episodes': fake_data_episodes, 'OC3': fake_data_oc3, 'metadata': metadata}
    error_defn, error_func = validate_1014()
    result = error_func(fake_dfs)
    # assert result == {'UASC': [2], 'Episodes': [4,5], 'OC3':[4]}
    assert result == {'UASC': [1, 3, 4], 'OC3': [1, 6, 9]}


def test_validate_197B():
    metadata = {'collection_start': '01/04/1980',
                'collection_end': '31/03/1981'}

    eps = pd.DataFrame([
        {'CHILD': '1', 'DECOM': '01/03/1980', 'DEC': '31/03/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},
        {'CHILD': '2', 'DECOM': '01/03/1980', 'DEC': '30/03/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},
        {'CHILD': '3333', 'DECOM': '01/03/1980', 'DEC': '01/01/1981', 'LS': 'V3', 'REC': 'X1', 'RNE': 'o'},
        {'CHILD': '4', 'DECOM': '01/02/1970', 'DEC': pd.NA, 'LS': 'o', 'REC': '!!', 'RNE': 'o'},
        {'CHILD': '5', 'DECOM': '01/03/1979', 'DEC': '01/01/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},
        {'CHILD': '5', 'DECOM': '01/01/1981', 'DEC': pd.NA, 'LS': 'o', 'REC': pd.NA, 'RNE': 'o'},
        {'CHILD': '6666', 'DECOM': '01/03/1979', 'DEC': '01/01/1981', 'LS': 'o', 'REC': '!!', 'RNE': 'o'},
        {'CHILD': '6666', 'DECOM': '01/01/1981', 'DEC': pd.NA, 'LS': 'o', 'REC': pd.NA, 'RNE': 'o'},
        {'CHILD': '7777', 'DECOM': '01/03/1979', 'DEC': '01/01/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},
        {'CHILD': '7777', 'DECOM': '01/01/1981', 'DEC': '01/07/1981', 'LS': 'o', 'REC': 'o', 'RNE': 'S'},
        {'CHILD': '8888', 'DECOM': '01/01/1981', 'DEC': '31/03/1999', 'LS': 'o', 'REC': 'o', 'RNE': 'S'},
        {'CHILD': '9009', 'DECOM': '01/03/1980', 'DEC': '31/03/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},
        {'CHILD': '1010', 'DECOM': '01/03/1980', 'DEC': '31/03/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},

    ])

    oc2 = pd.DataFrame({
        'CHILD':
            ['9999999999', '1', '2', '3333',
             '99999999', '8888', '5', '9009',
             '1010'],
        'SDQ_SCORE':
            ['OK', pd.NA, pd.NA, pd.NA,
             pd.NA, 'OK', pd.NA, pd.NA,
             pd.NA],
        'SDQ_REASON':
            ['SDQ1', pd.NA, pd.NA, 'OK',
             pd.NA, 'OK', 'OK!', pd.NA,
             pd.NA],
        'DOB':
            ['01/04/1970', '31/03/1964', '31/03/1977', '01/04/1970',
             '01/04/1970', '01/04/1970', '01/07/1970', '01/01/1977',
             '09/09/1963'],
    })


    test_dfs = {'Episodes': eps, 'OC2': oc2, 'metadata': metadata}

    error_defn, error_func = validate_197B()

    test_result = error_func(test_dfs)

    assert test_result == {'OC2': [1, 2, 7, 8]}


def test_validate_157():
    metadata = {'collection_start': '01/04/1980',
                'collection_end': '31/03/1981'}

    eps = pd.DataFrame([
        {'CHILD': '1', 'DECOM': '01/03/1980', 'DEC': '31/03/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},
        {'CHILD': '2', 'DECOM': '01/03/1980', 'DEC': '30/03/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},
        {'CHILD': '3333', 'DECOM': '01/03/1980', 'DEC': '01/01/1981', 'LS': 'V3', 'REC': 'X1', 'RNE': 'o'},
        {'CHILD': '4', 'DECOM': '01/02/1970', 'DEC': pd.NA, 'LS': 'o', 'REC': '!!', 'RNE': 'o'},
        {'CHILD': '5', 'DECOM': '01/03/1979', 'DEC': '01/01/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},
        {'CHILD': '5', 'DECOM': '01/01/1981', 'DEC': pd.NA, 'LS': 'o', 'REC': pd.NA, 'RNE': 'o'},
        {'CHILD': '6666', 'DECOM': '01/03/1979', 'DEC': '01/01/1981', 'LS': 'o', 'REC': '!!', 'RNE': 'o'},
        {'CHILD': '6666', 'DECOM': '01/01/1981', 'DEC': pd.NA, 'LS': 'o', 'REC': pd.NA, 'RNE': 'o'},
        {'CHILD': '7777', 'DECOM': '01/03/1979', 'DEC': '01/01/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},
        {'CHILD': '7777', 'DECOM': '01/01/1981', 'DEC': '01/07/1981', 'LS': 'o', 'REC': 'o', 'RNE': 'S'},
        {'CHILD': '8888', 'DECOM': '01/01/1981', 'DEC': '31/03/1999', 'LS': 'o', 'REC': 'o', 'RNE': 'S'},
    ])

    oc2 = pd.DataFrame({
        'CHILD':
            ['9999999999', '1', '2', '3333',
             '99999999', '8888', '5'],
        'SDQ_SCORE':
            ['OK', pd.NA, pd.NA, pd.NA,
             pd.NA, 'OK', pd.NA],
        'SDQ_REASON':
            ['SDQ1', 'SDQ1', 'SDQ1', 'OK',
             pd.NA, 'OK', 'OK!'],
        'DOB':
            ['01/04/1970', '31/03/1965', '01/04/1976', '01/04/1970',
             '01/04/1970', '01/04/1970', '01/07/1970'],
    })

    test_dfs = {'Episodes': eps, 'OC2': oc2, 'metadata': metadata}

    error_defn, error_func = validate_157()

    test_result = error_func(test_dfs)

    assert test_result == {'OC2': [1, 2]}


def test_validate_357():
    episodes = pd.DataFrame([
        {'CHILD': '000', 'DECOM': '01/01/2001', 'RNE': '!!'},
        {'CHILD': '111', 'DECOM': '11/11/2011', 'RNE': 'ok'},
        {'CHILD': '111', 'DECOM': '01/01/2000', 'RNE': 'S'},
        {'CHILD': '222', 'DECOM': '11/11/2011', 'RNE': 'ok'},
        {'CHILD': '222', 'DECOM': pd.NA, 'RNE': 'ok'},
        {'CHILD': '222', 'DECOM': '01/01/2001', 'RNE': 'S'},
        {'CHILD': '333', 'DECOM': '12/12/2012', 'RNE': 'ok'},
        {'CHILD': '333', 'DECOM': '01/01/2001', 'RNE': '!!'},
        {'CHILD': '333', 'DECOM': '05/05/2005', 'RNE': 'ok'},
        {'CHILD': '444', 'DECOM': '05/05/2005', 'RNE': pd.NA},  # !!
        {'CHILD': '555', 'DECOM': '01/01/1990', 'RNE': 'ok'},  # ok - before collection_start
    ])
    metadata = {
        'collection_start': '31/03/1995'
    }
    test_dfs = {'Episodes': episodes,
                'metadata': metadata}

    error_defn, error_func = validate_357()

    test_result = error_func(test_dfs)

    assert test_result == {'Episodes': [0, 7, 9]}


def test_validate_117():
    metadata = {
        'collection_end': '31/03/2018'
    }
    fake_placed_adoption = pd.DataFrame([
        {'CHILD': 101, 'DATE_PLACED_CEASED': '26/05/2000', 'DATE_PLACED': '26/05/2000'},  # 0
        {'CHILD': 102, 'DATE_PLACED_CEASED': '01/07/2018', 'DATE_PLACED': '26/05/2000'},
        # 1 Fail DATE_PLACED_CEASED > collection_end
        {'CHILD': 103, 'DATE_PLACED_CEASED': '26/05/2000', 'DATE_PLACED': pd.NA},  # 2
        {'CHILD': 104, 'DATE_PLACED_CEASED': '26/05/2017', 'DATE_PLACED': '01/02/2016'},
        # 3 Fail greater than DEC of latest episode
        {'CHILD': 105, 'DATE_PLACED_CEASED': pd.NA, 'DATE_PLACED': '26/05/2019'},  # 4 Fail DATE_PLACED > collection_end
    ])
    fake_data_eps = pd.DataFrame([
        {'CHILD': 101, 'DEC': '01/01/2009', 'REC': 'E45', 'DECOM': '01/01/2009'},  # 0
        {'CHILD': 102, 'DEC': '01/01/2001', 'REC': 'A3', 'DECOM': '01/01/2001'},  # 1
        {'CHILD': 102, 'DEC': '20/12/2001', 'REC': 'E15', 'DECOM': '20/12/2001'},  # 2
        {'CHILD': 102, 'DEC': '03/01/2019', 'REC': 'E46', 'DECOM': '03/01/2019'},  # 3 Fail
        {'CHILD': 102, 'DEC': '03/04/2008', 'REC': 'E48', 'DECOM': '03/04/2008'},  # 4
        {'CHILD': 103, 'DEC': '01/01/2002', 'REC': 'X2', 'DECOM': '01/01/2002'},  # 5
        {'CHILD': 104, 'DEC': '10/01/2002', 'REC': 'E11', 'DECOM': '10/01/2002'},  # 6
        {'CHILD': 104, 'DEC': '11/02/2010', 'REC': 'X1', 'DECOM': '11/02/2010'},  # 7 Fail Ignored
        {'CHILD': 104, 'DEC': '25/01/2002', 'REC': 'X1', 'DECOM': '25/01/2002'},  # 8 Ignored REC is X1
        {'CHILD': 105, 'DEC': '25/01/2002', 'REC': 'E47', 'DECOM': '25/01/2002'},  # 9
        {'CHILD': 105, 'DEC': pd.NA, 'REC': 'E45', 'DECOM': pd.NA},  # 10
    ])
    # TODO: in  the scenario where the REC of the latest episodes is X1, should the episode before the lastest
    #  be considered instead?. This will entail filtering by X1 before doing idxmax. Is this what this rule means?.

    fake_dfs = {'Episodes': fake_data_eps, 'metadata': metadata, 'PlacedAdoption': fake_placed_adoption}
    error_defn, error_func = validate_117()
    result = error_func(fake_dfs)
    assert result == {'Episodes': [3, 6, 9], 'PlacedAdoption': [1, 3, 4]}


def test_validate_118():
    fake_placed_adoption = pd.DataFrame({
        'DATE_PLACED_CEASED': ['08/03/2020', '22/06/2020', '13/10/2022', pd.NA],
        "CHILD": ['101', '102', '103', '104'],
    })
    fake_data_episodes = pd.DataFrame([
        {'CHILD': '101', 'LS': 'L1', 'DECOM': '01/01/2019'},  # 0 Fail DATE_PLACED_CEASED is before collection_start
        {'CHILD': '102', 'LS': 'V3', 'DECOM': '01/01/2022'},  # 1 skip fail because LS is V3
        {'CHILD': '102', 'LS': 'X0', 'DECOM': '20/12/2020'},  # 2 fail
        {'CHILD': '102', 'LS': 'L1', 'DECOM': '03/01/2021'},  # 3
        {'CHILD': '102', 'LS': 'L1', 'DECOM': '03/04/2022'},  # 4
        {'CHILD': '103', 'LS': 'X2', 'DECOM': '01/01/2019'},  # 5 pass
        {'CHILD': '104', 'LS': 'L1', 'DECOM': '01/01/2019'},  # 6 drop.na drops this child
    ])
    metadata = {
        'collection_start': '01/04/2020',
    }
    fake_dfs = {'Episodes': fake_data_episodes, 'PlacedAdoption': fake_placed_adoption, 'metadata': metadata, }
    error_defn, error_func = validate_118()
    result = error_func(fake_dfs)
    assert result == {'Episodes': [0, 2], 'PlacedAdoption': [0, 1]}


def test_validate_352():
    fake_data = pd.DataFrame({
        'CHILD': ['101', '102', '101', '102', '103'],
        'RNE': ['S', 'S', 'X1', pd.NA, 'S'],
        'DECOM': ['16/03/2021', '17/06/2020', '20/03/2020', pd.NA, '23/08/2020'],
    })

    fake_data_child = pd.DataFrame({
        'CHILD': ['101', '102', '103', '103'],
        'DOB': ['16/03/2005', '23/09/2002', '31/12/2000', '31/12/2000'],
    })

    fake_dfs = {'Episodes': fake_data, 'Header': fake_data_child}

    error_defn, error_func = validate_352()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [4]}


def test_validators_1007():
    # TODO change name to test_validate_1007()
    fake_data_oc3 = pd.DataFrame({
        'CHILD': ['A', 'B', 'C', 'D', 'E'],
        'DOB': ['01/01/2001', '01/01/2016', '20/12/1997', '01/01/2000', '03/01/2000', ],
        'IN_TOUCH': ['DIED', 'Yes', 'RHOM', pd.NA, 'DIED'],
        'ACTIV': [pd.NA, pd.NA, 'XXX', pd.NA, 'XXX'],
        'ACCOM': [pd.NA, pd.NA, pd.NA, 'XXX', 'XXX'],
    })
    fake_data_episodes = pd.DataFrame({
        'CHILD': ['A', 'B', 'C', 'D', 'E'],
        'REC': [pd.NA, 'E12', 'X1', pd.NA, 'E11'],
        'DEC': ['15/03/2021', pd.NA, '20/03/2020', pd.NA, '23/08/2020'],
    })
    metadata = {
        'collection_end': '31/03/2018'
    }

    fake_dfs = {'Episodes': fake_data_episodes, 'OC3': fake_data_oc3, 'metadata': metadata}
    error_defn, error_func = validate_1007()
    result = error_func(fake_dfs)
    assert result == {'Episodes': [0, 3], 'OC3': [0, 3]}


def test_validate_210():
    fake_data_header = pd.DataFrame({
        'CHILD': ['111', '123', '333', '444', '667'],
        'UPN': ['UN4', pd.NA, 'UN3', 'UN4', 'UN4', ],
    })
    fake_data_epi = pd.DataFrame([
        {'CHILD': '111', 'DECOM': '01/01/2020', },  # 0
        {'CHILD': '111', 'DECOM': '11/01/2020', },  # 1
        {'CHILD': '111', 'DECOM': '30/03/2020', },  # 2 fail
        {'CHILD': '123', 'DECOM': '01/01/2020', },  # 3
        {'CHILD': '123', 'DECOM': '11/01/2020', },  # 4
        {'CHILD': '333', 'DECOM': '01/01/2020', },  # 5
        {'CHILD': '333', 'DECOM': '22/01/2020', },  # 6
        {'CHILD': '333', 'DECOM': '11/01/2020', },  # 7
        {'CHILD': '444', 'DECOM': '22/01/2020', },  # 8
        {'CHILD': '444', 'DECOM': '25/03/2020', },  # 9 fail
        {'CHILD': '444', 'DECOM': '01/01/2020', },  # 10
        {'CHILD': '667', 'DECOM': '01/01/2020', },  # 11
    ])
    metadata = {
        'collection_end': '31/03/2020'
    }

    fake_dfs = {'Episodes': fake_data_epi, 'Header': fake_data_header, 'metadata': metadata}
    error_defn, error_func = validate_210()
    result = error_func(fake_dfs)
    assert result == {'Episodes': [2, 9], 'Header': [0, 3]}


def test_validate_209():
    fake_data_header = pd.DataFrame({
        'CHILD': ['101', '102', '103', '104', '105', '106', '107'],
        'UPN': [pd.NA, 'H801200001001', 'UN1', 'UN2', pd.NA, 'UN1', pd.NA],
        'DOB': ['01/01/2020', '11/11/2020', '03/10/2015', '11/11/2020', '01/01/2020', '11/11/2020', '01/02/2020']
    })
    metadata = {
        'collection_start': '01/04/2025',
    }
    fake_dfs = {'Header': fake_data_header, 'metadata': metadata}

    error_defn, error_func = validate_209()
    result = error_func(fake_dfs)

    assert result == {'Header': [2]}


def test_validate_198():
    metadata = {'collection_start': '01/04/1980',
                'collection_end': '31/03/1981'}

    eps = pd.DataFrame([
        {'CHILD': '1', 'DECOM': '01/03/1980', 'DEC': '31/03/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},
        {'CHILD': '2', 'DECOM': '01/03/1980', 'DEC': '30/03/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},
        {'CHILD': '3', 'DECOM': '01/03/1980', 'DEC': '01/01/1981', 'LS': 'V3', 'REC': 'X1', 'RNE': 'o'},  # False
        {'CHILD': '4', 'DECOM': '01/02/1970', 'DEC': pd.NA, 'LS': 'o', 'REC': '!!', 'RNE': 'o'},
        {'CHILD': '5555', 'DECOM': '01/03/1979', 'DEC': '01/01/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},
        {'CHILD': '5555', 'DECOM': '01/01/1981', 'DEC': pd.NA, 'LS': 'o', 'REC': pd.NA, 'RNE': 'o'},
        {'CHILD': '6', 'DECOM': '01/03/1979', 'DEC': '01/01/1981', 'LS': 'o', 'REC': '!!', 'RNE': 'o'},  # !! - False
        {'CHILD': '6', 'DECOM': '01/01/1981', 'DEC': pd.NA, 'LS': 'o', 'REC': pd.NA, 'RNE': 'o'},  # False
        {'CHILD': '7777', 'DECOM': '01/03/1979', 'DEC': '01/01/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},  # False
        {'CHILD': '7777', 'DECOM': '01/01/1981', 'DEC': '01/07/1981', 'LS': 'o', 'REC': 'o', 'RNE': 'S'},  # !! - False
        {'CHILD': '8', 'DECOM': '01/01/1981', 'DEC': '31/03/1999', 'LS': 'o', 'REC': 'o', 'RNE': 'S'},  # False
    ])

    oc2 = pd.DataFrame({'CHILD': ['999999', '1', '2', '3', '9999', '8'],
                        'SDQ_REASON': ['!!!!!', pd.NA, 'OO', '!!', pd.NA, '!!']})

    fake_dfs = {'Episodes': eps,
                'OC2': oc2,
                'metadata': metadata}

    error_defn, error_func = validate_198()

    result = error_func(fake_dfs)

    assert result == {'OC2': [0, 3, 5]}


def test_validate_607():
    fake_data_eps = pd.DataFrame([
        {'CHILD': 101, 'DEC': '01/01/2021', 'REC': pd.NA, 'LS': 'L1', },  # 0 Ignore: REC is null
        {'CHILD': 102, 'DEC': '01/01/2001', 'REC': 'A3', 'LS': 'V4', },  # 1 Ignore: LS is V4
        {'CHILD': 103, 'DEC': '20/12/2001', 'REC': 'E15', 'LS': 'V3', },  # 2 Ignore: LS is V3
        {'CHILD': 104, 'DEC': '03/01/2020', 'REC': 'E46', 'LS': 'L4', },  # 3 Ignore: DEC out of range
        {'CHILD': 105, 'DEC': '03/04/2020', 'REC': 'E48', 'LS': 'L1', },  # 4 FAIL
        {'CHILD': 105, 'DEC': '01/07/2020', 'REC': 'X2', 'LS': 'XO', },  # 5 FAIL
        {'CHILD': 105, 'DEC': '10/01/2021', 'REC': 'E11', 'LS': 'L4', },  # 6 FAIL
        {'CHILD': 108, 'DEC': '11/02/2021', 'REC': 'E48', 'LS': 'L1', },  # 7
        {'CHILD': 109, 'DEC': '25/01/2002', 'REC': 'X1', 'LS': 'XO', },  # 8 Ignore: REC is X1
        {'CHILD': 110, 'DEC': '25/01/2021', 'REC': 'E47', 'LS': pd.NA, },  # 9
        {'CHILD': 111, 'DEC': pd.NA, 'REC': 'E45', 'LS': 'L4', },  # 10 Ignore : DEC is null
        {'CHILD': 112, 'DEC': '25/08/2020', 'REC': 'E46', 'LS': 'XO', },  # 11
    ])
    fake_data_header = pd.DataFrame([
        {'CHILD': 101, 'SEX': '2', 'MOTHER': pd.NA},  # 0 FAIL Ignore: REC is null
        {'CHILD': 102, 'SEX': '2', 'MOTHER': '0'},  # 1 Ignore: LS is V4
        {'CHILD': 103, 'SEX': '2', 'MOTHER': pd.NA},  # 2 Ignore: LS is V3
        {'CHILD': 104, 'SEX': '2', 'MOTHER': pd.NA},  # 3 Ignore: DEC out of range
        {'CHILD': 105, 'SEX': '2', 'MOTHER': pd.NA},  # 4 FAIL
        {'CHILD': 108, 'SEX': '1', 'MOTHER': pd.NA},  # 5
        {'CHILD': 109, 'SEX': '2', 'MOTHER': '0'},  # 6 Ignore: REC is X1
        {'CHILD': 110, 'SEX': '2', 'MOTHER': pd.NA},  # 7 FAIL
        {'CHILD': 111, 'SEX': '2', 'MOTHER': '0'},  # 8 Ignore : DEC is null
        {'CHILD': 112, 'SEX': '2', 'MOTHER': '1'},  # 9
    ])
    metadata = {
        'collection_start': '01/04/2020',
        'collection_end': '31/03/2021'
    }
    fake_dfs = {'Header': fake_data_header, 'Episodes': fake_data_eps, 'metadata': metadata}
    error_defn, error_func = validate_607()
    result = error_func(fake_dfs)
    assert result == {'Header': [4, 7], 'Episodes': [4, 5, 6, 9]}


def test_validate_1010():
    fake_episodes_prev = pd.DataFrame({
        'CHILD': ['101', '101',
                  '102', '102',
                  '103', '103', '103'],
        'DEC': ['20/06/2020', pd.NA,  # ok - has current episodes
                pd.NA, '14/03/2021',  # ok - 'open' episode not latest by DECOM
                '01/01/2020', pd.NA, '01/05/2020'],  # Fail!
        'DECOM': ['01/01/2020', '11/11/2020',
                  '03/10/2020', '11/11/2020',
                  '01/01/2020', '11/11/2020', '01/02/2020']
    })

    fake_episodes = pd.DataFrame({
        'CHILD': ['101'],
        'DEC': ['20/05/2021']
    })

    fake_oc3 = pd.DataFrame({
        'CHILD': ['101', '102', '103']
    })

    fake_dfs = {'Episodes': fake_episodes, 'Episodes_last': fake_episodes_prev, 'OC3': fake_oc3}

    erro_defn, error_func = validate_1010()

    result = error_func(fake_dfs)

    assert result == {'OC3': [2]}


def test_validate_525():
    fake_placed_adoption = pd.DataFrame({
        'DATE_PLACED_CEASED': ['08/03/2020', '22/06/2020', '13/10/2022', '24/10/2021', pd.NA],
        "CHILD": ['104', '105', '107', '108', '109'],
    })
    fake_data_ad1 = pd.DataFrame({
        'CHILD': ['104', '105', '107', '108', '109'],
        'DATE_INT': [pd.NA, pd.NA, 'XXX', pd.NA, 'XXX'],
        'DATE_MATCH': [pd.NA, 'XXX', 'XXX', pd.NA, 'XXX'],
        'FOSTER_CARE': [pd.NA, pd.NA, 'XXX', pd.NA, 'XXX'],
        'NB_ADOPTR': [pd.NA, pd.NA, 'XXX', pd.NA, 'XXX'],
        'SEX_ADOPTR': [pd.NA, pd.NA, 'XXX', pd.NA, 'XXX'],
        'LS_ADOPTR': [pd.NA, pd.NA, 'XXX', 'XXX', 'XXX'],
    })

    fake_dfs = {'PlacedAdoption': fake_placed_adoption, 'AD1': fake_data_ad1}
    error_defn, error_func = validate_525()
    result = error_func(fake_dfs)
    assert result == {'PlacedAdoption': [1, 2, 3], 'AD1': [1, 2, 3]}


def test_validate_335():
    fake_data_eps = pd.DataFrame({
        'PLACE': ['A2', '--', 'A1', '--',
                  'A4', '--', 'A5', 'A3'],
        'REC': ['E1', 'E1', 'E1', 'E12',
                'E11', 'E1', '--', 'E12'],
        'CHILD': ['10', '11', '12', '13',
                  '14', '15', '16', '17']
    })
    fake_data_ad1 = pd.DataFrame({
        'FOSTER_CARE': [0, 1, '0', '1',
                        2, 'former foster carer', '', pd.NA],
        'CHILD': ['10', '11', '12', '13',
                  '14', '15', '16', '17']
    })
    fake_dfs = {'Episodes': fake_data_eps, 'AD1': fake_data_ad1}
    error_defn, error_func = validate_335()
    result = error_func(fake_dfs)
    assert result == {'Episodes': [0], 'AD1': [0]}


def test_validate_215():
    fake_data_oc2 = pd.DataFrame({
        'CHILD': ['A', 'B', 'C', 'D', 'E'],
        'IMMUNISATIONS': ['1', pd.NA, '1', pd.NA, '1'],
        'TEETH_CHECK': ['1', pd.NA, '1', '1', '1'],
        'HEALTH_ASSESSMENT': ['1', pd.NA, '1', pd.NA, '1'],
        'SUBSTANCE_MISUSE': [pd.NA, pd.NA, '1', '1', '1'],
        'CONVICTED': [pd.NA, pd.NA, '1', '1', pd.NA],
        'HEALTH_CHECK': [pd.NA, pd.NA, '1', '1', pd.NA],
        'INTERVENTION_RECEIVED': ['1', pd.NA, '1', '1', pd.NA],
        'INTERVENTION_OFFERED': [pd.NA, '1', '1', '1', pd.NA],
    })
    fake_data_oc3 = pd.DataFrame({
        'CHILD': ['A', 'B', 'C', 'D', 'E'],
        'IN_TOUCH': ['DIED', 'Yes', 'RHOM', pd.NA, pd.NA],
        'ACTIV': [pd.NA, pd.NA, 'XXX', pd.NA, pd.NA],
        'ACCOM': [pd.NA, pd.NA, pd.NA, 'XXX', pd.NA],
    })
    fake_dfs = {'OC3': fake_data_oc3, 'OC2': fake_data_oc2}
    error_defn, error_func = validate_215()
    result = error_func(fake_dfs)
    assert result == {'OC3': [0, 1, 2, 3], 'OC2': [0, 1, 2, 3]}


def test_validate_399():
    # change log

    # index 6 and 7 are changed to the same child such that though both have the review information, index 6 would no longer trigger the error because the child has another episode (index 7) where LS is not V3/V4.
    # Index 0 and 1 have been same to the same child such that all its episodes have LS V3/V4 and the error is trigged though index zero does not have the review information and would not have triggered the error on its own.
    # index 6 truly reflects the change. It would have failed earlier but it passes now since the child's other LS is not V3

    # test data assumes that child IDs cannot repeat in the header and reviews tables.

    fake_data_episodes = pd.DataFrame({
        'CHILD': ['101', '101', '103', '104', '105', '106', '108', '108'],
        'LS': ['V4', 'V4', 'V3', 'L4', pd.NA, 'V4', 'V3', 'XO'],
    })
    fake_data_header = pd.DataFrame({
        'CHILD': ['101', '102', '103', '104', '105', '106', '108', '109'],
        'MOTHER': ['0', '0', pd.NA, pd.NA, 1, 0, 1, pd.NA],
    })
    fake_data_reviews = pd.DataFrame({
        'CHILD': ['101', '102', '103', '104', '105', '106', '108', '109'],
        'REVIEW': ['31/12/2008', '01/01/2012', pd.NA, '01/01/2009', '01/01/2012', '01/01/2017', '01/01/2021',
                   '01/01/2015'],
        'REVIEW_CODE': ['PN1', 'PN2', pd.NA, 'PN4', 'PN5', 'PN6', 'PN7', 'PN0'],
    })
    fake_dfs = {'Header': fake_data_header, 'Reviews': fake_data_reviews, 'Episodes': fake_data_episodes}
    error_defn, error_func = validate_399()
    result = error_func(fake_dfs)
    assert result == {'Header': [0, 5], 'Reviews': [0, 5], 'Episodes': [0, 1, 5, ]}


def test_validate_226():
    fake_data_epi = pd.DataFrame([
        {'CHILD': '111', 'DECOM': '01/01/2020', 'PLACE': 'U1', 'REASON_PLACE_CHANGE': 'XXX'},  # 0
        {'CHILD': '111', 'DECOM': '11/01/2020', 'PLACE': 'T1', 'REASON_PLACE_CHANGE': pd.NA},  # 1 Fail
        {'CHILD': '111', 'DECOM': '22/01/2020', 'PLACE': 'X1', 'REASON_PLACE_CHANGE': pd.NA},  # 2
        {'CHILD': '123', 'DECOM': '01/01/2020', 'PLACE': 'U1', 'REASON_PLACE_CHANGE': pd.NA},  # 3
        {'CHILD': '123', 'DECOM': '11/01/2020', 'PLACE': 'X1', 'REASON_PLACE_CHANGE': pd.NA},  # 4
        {'CHILD': '333', 'DECOM': '01/01/2020', 'PLACE': 'T2', 'REASON_PLACE_CHANGE': pd.NA},  # 5
        {'CHILD': '333', 'DECOM': '22/01/2020', 'PLACE': 'X1', 'REASON_PLACE_CHANGE': 'CHANGE'},  # 6
        {'CHILD': '333', 'DECOM': '11/01/2020', 'PLACE': 'U1', 'REASON_PLACE_CHANGE': pd.NA},  # 7
        {'CHILD': '444', 'DECOM': '22/01/2020', 'PLACE': 'T1', 'REASON_PLACE_CHANGE': 'XXX'},  # 8 Fail
        {'CHILD': '444', 'DECOM': '11/01/2020', 'PLACE': 'X1', 'REASON_PLACE_CHANGE': pd.NA},  # 9
        {'CHILD': '444', 'DECOM': '01/01/2020', 'PLACE': 'T3', 'REASON_PLACE_CHANGE': pd.NA},  # 10 Pass
        {'CHILD': '666', 'DECOM': '01/01/2020', 'PLACE': 'T4', 'REASON_PLACE_CHANGE': pd.NA},  # 11 Pass
    ])
    fake_dfs = {'Episodes': fake_data_epi}
    error_defn, error_func = validate_226()
    result = error_func(fake_dfs)
    assert result == {'Episodes': [1, 8]}


def test_validate_358():
    fake_data_eps = pd.DataFrame([
        {'CHILD': 101, 'DECOM': '01/01/2009', 'LS': 'J3'},  # 0 Fail
        {'CHILD': 102, 'DECOM': '01/01/2001', 'LS': 'X'},  # 1
        {'CHILD': 103, 'DECOM': '20/12/2001', 'LS': 'L2'},  # 2
        {'CHILD': 104, 'DECOM': '03/01/2018', 'LS': 'J2'},  # 3 Pass
        {'CHILD': 105, 'DECOM': '03/04/2008', 'LS': 'J1'},  # 4 Fail
        {'CHILD': 106, 'DECOM': '01/01/2002', 'LS': 'L2'},  # 5
        {'CHILD': 107, 'DECOM': '10/01/2002', 'LS': 'X'},  # 6
        {'CHILD': 108, 'DECOM': '11/02/2012', 'LS': 'J1'},  # 7 Pass
        {'CHILD': 109, 'DECOM': '25/01/2002', 'LS': 'L2'},  # 8
        {'CHILD': 110, 'DECOM': '25/01/2002', 'LS': 'L2'},  # 9
        {'CHILD': 111, 'DECOM': pd.NA, 'LS': 'J2'},  # 10 ignored by dropna
        {'CHILD': 112, 'DECOM': '25/01/2002', 'LS': 'J3'},  # 11 ignored by dropna
    ])
    fake_data_header = pd.DataFrame([
        {'CHILD': 101, 'DOB': '01/01/2000', },  # 0
        {'CHILD': 102, 'DOB': '01/01/2001', },  # 1
        {'CHILD': 103, 'DOB': '20/12/2001', },  # 2
        {'CHILD': 104, 'DOB': '01/01/2000', },  # 3
        {'CHILD': 105, 'DOB': '03/01/2000', },  # 4
        {'CHILD': 106, 'DOB': '01/01/2002', },  # 5
        {'CHILD': 107, 'DOB': '10/01/2002', },  # 6
        {'CHILD': 108, 'DOB': '11/01/2002', },  # 7
        {'CHILD': 109, 'DOB': '25/01/2002', },  # 8
        {'CHILD': 110, 'DOB': '25/01/2002', },  # 9
        {'CHILD': 111, 'DOB': '25/01/2002', },  # 10
        {'CHILD': 112, 'DOB': pd.NA, }  # 11
    ])
    fake_dfs = {'Episodes': fake_data_eps, 'Header': fake_data_header}
    error_defn, error_func = validate_358()
    result = error_func(fake_dfs)
    assert result == {'Episodes': [0, 4], 'Header': [0, 4]}


def test_validate_407():
    fake_data_eps = pd.DataFrame([
        {'CHILD': 101, 'DEC': '01/01/2009', 'REC': 'E45'},  # 0 pass
        {'CHILD': 102, 'DEC': '01/01/2001', 'REC': 'A3'},  # 1
        {'CHILD': 103, 'DEC': '20/12/2001', 'REC': 'E15'},  # 2
        {'CHILD': 104, 'DEC': '03/01/2019', 'REC': 'E46'},  # 3 fail
        {'CHILD': 105, 'DEC': '03/04/2008', 'REC': 'E48'},  # 4 pass
        {'CHILD': 106, 'DEC': '01/01/2002', 'REC': 'X2'},  # 5
        {'CHILD': 107, 'DEC': '10/01/2002', 'REC': 'E11'},  # 6
        {'CHILD': 108, 'DEC': '11/02/2020', 'REC': 'E48'},  # 7 fail
        {'CHILD': 109, 'DEC': '25/01/2002', 'REC': 'X1'},  # 8
        {'CHILD': 110, 'DEC': '25/01/2002', 'REC': 'E47'},  # 9
        {'CHILD': 111, 'DEC': pd.NA, 'REC': 'E45'},  # 10 ignored by dropna
        {'CHILD': 112, 'DEC': '25/01/2002', 'REC': 'E46'},  # 11 ignored by dropna
    ])
    fake_data_header = pd.DataFrame([
        {'CHILD': 101, 'DOB': '01/01/2000', },  # 0
        {'CHILD': 102, 'DOB': '01/01/2001', },  # 1
        {'CHILD': 103, 'DOB': '20/12/2001', },  # 2
        {'CHILD': 104, 'DOB': '01/01/2000', },  # 3
        {'CHILD': 105, 'DOB': '03/01/2000', },  # 4
        {'CHILD': 106, 'DOB': '01/01/2002', },  # 5
        {'CHILD': 107, 'DOB': '10/01/2002', },  # 6
        {'CHILD': 108, 'DOB': '11/01/2002', },  # 7
        {'CHILD': 109, 'DOB': '25/01/2002', },  # 8
        {'CHILD': 110, 'DOB': '25/01/2002', },  # 9
        {'CHILD': 111, 'DOB': '25/01/2002', },  # 10
        {'CHILD': 112, 'DOB': pd.NA, }  # 11
    ])
    fake_dfs = {'Episodes': fake_data_eps, 'Header': fake_data_header}
    error_defn, error_func = validate_407()
    result = error_func(fake_dfs)
    assert result == {'Episodes': [3, 7], 'Header': [3, 7]}


def test_validate_634():
    fake_data_prevperm = pd.DataFrame({
        'CHILD': ['101', '102', '103', '6', '7', '8'],
        'PREV_PERM': ['Z1', pd.NA, pd.NA, 'Z1', pd.NA, 'P1'],
        'LA_PERM': [pd.NA, '352', pd.NA, '352', pd.NA, '352'],
        'DATE_PERM': [pd.NA, pd.NA, '01/05/2000', pd.NA, pd.NA, '05/05/2020'],
        # last 3 rows will disappear after merging on CHILD
    })
    fake_data_episodes = pd.DataFrame([
        {'CHILD': '101', 'DECOM': '20/10/2011', },  # 0
        {'CHILD': '102', 'DECOM': '19/11/2021', },  # 1
        {'CHILD': '102', 'DECOM': '17/06/2001', },  # 2
        {'CHILD': '103', 'DECOM': '04/04/2002', },  # 3
        {'CHILD': '103', 'DECOM': '11/09/2015', },  # 4
        {'CHILD': '103', 'DECOM': '01/03/2016', },  # 5
    ])
    fake_dfs = {
        'PrevPerm': fake_data_prevperm,
        'Episodes': fake_data_episodes,
        'metadata': {'collection_start': '01/04/2016'}
    }
    error_defn, error_func = validate_634()

    result = error_func(fake_dfs)

    assert result == {'PrevPerm': [0, 2], 'Episodes': [0, 3, 4, 5]}


def test_validate_442():
    fake_data_episodes = pd.DataFrame({
        'CHILD': ['101', '102', '103', '104', '105', '106', '108', '999'],
        'LS': [pd.NA, 'L4', pd.NA, 'L4', 'L1', 'V4', 'V3', 'XO'],
    })
    fake_data_header = pd.DataFrame({
        'CHILD': ['101', '102', '103', '104', '105', '106', '108'],
        'UPN': [pd.NA, 'H801200001001', 'UN1', 'UN2', pd.NA, 'UN3', pd.NA],
    })
    fake_dfs = {'Episodes': fake_data_episodes, 'Header': fake_data_header}
    error_defn, error_func = validate_442()
    result = error_func(fake_dfs)

    assert result == {'Episodes': [0, 4, 7], 'Header': [0, 4]}


def test_validate_344():
    fake_data_oc3 = pd.DataFrame({
        'CHILD': ['A', 'B', 'C', 'D', 'E'],
        'IN_TOUCH': ['DIED', 'Yes', 'RHOM', pd.NA, 'DIED'],
        'ACTIV': [pd.NA, pd.NA, 'XXX', pd.NA, 'XXX'],
        'ACCOM': [pd.NA, pd.NA, pd.NA, 'XXX', 'XXX'],
    })
    fake_dfs = {'OC3': fake_data_oc3}
    error_defn, error_func = validate_344()
    result = error_func(fake_dfs)
    assert result == {'OC3': [2, 4]}


def test_validate_345():
    fake_data_oc3 = pd.DataFrame({
        'CHILD': ['A', 'B', 'C', 'D', 'E'],
        'IN_TOUCH': ['No', 'YES', 'YES', pd.NA, 'Yes'],
        'ACTIV': [pd.NA, 0, 'XXX', pd.NA, 'XXX'],
        'ACCOM': [0, pd.NA, '0', 'XXX', 'XXX'],
    })
    fake_dfs = {'OC3': fake_data_oc3}
    error_defn, error_func = validate_345()
    result = error_func(fake_dfs)
    assert result == {'OC3': [1, 2]}


def test_validate_384():
    fake_data = pd.DataFrame([
        {'CHILD': '11', 'PLACE': 'U1', 'LS': 'V4', },  # 0
        {'CHILD': '202', 'PLACE': 'x', 'LS': 'D1', },  # 1
        {'CHILD': '3003', 'PLACE': 'U4', 'LS': 'V3', },  # 2
        {'CHILD': '40004', 'PLACE': 'P1', 'LS': 'V3', },  # 3
        {'CHILD': '5005', 'PLACE': 'A5', 'LS': 'x', },  # 4
        {'CHILD': '606', 'PLACE': 'A6', 'LS': 'V4', },  # 5
        {'CHILD': '77', 'PLACE': 'x', 'LS': 'x'},  # 6
    ])
    fake_dfs = {'Episodes': fake_data}
    error_defn, error_func = validate_384()
    result = error_func(fake_dfs)
    assert result == {'Episodes': [0, 2]}


def test_validate_390():
    fake_data = pd.DataFrame([
        {'CHILD': '11', 'PLACE': 'P1', 'LS': 'x', 'REC': 'E11'},  # 0
        {'CHILD': '202', 'PLACE': 'x', 'LS': 'D1', 'REC': 'x'},  # 1
        {'CHILD': '3003', 'PLACE': 'A4', 'LS': 'D1', 'REC': 'E12'},  # 2
        {'CHILD': '40004', 'PLACE': 'P1', 'LS': 'V2', 'REC': 'E12'},  # 3
        {'CHILD': '5005', 'PLACE': 'A5', 'LS': 'x', 'REC': 'E11'},  # 4
        {'CHILD': '606', 'PLACE': 'A6', 'LS': 'V2', 'REC': 'x'},  # 5
        {'CHILD': '77', 'PLACE': 'x', 'LS': 'x', 'REC': 'x'},  # 6
    ])
    fake_dfs = {'Episodes': fake_data}
    error_defn, error_func = validate_390()
    result = error_func(fake_dfs)
    assert result == {'Episodes': [0, 3]}


def test_validate_378():
    fake_data = pd.DataFrame([
        {'CHILD': '11', 'PLACE': 'P1', 'LS': 'x', 'REC': 'x'},  # 0
        {'CHILD': '202', 'PLACE': 'x', 'LS': 'D1', 'REC': 'x'},  # 1
        {'CHILD': '3003', 'PLACE': 'A4', 'LS': 'D1', 'REC': 'E12'},  # 2
        {'CHILD': '40004', 'PLACE': 'P1', 'LS': 'V2', 'REC': 'E12'},  # 3
        {'CHILD': '5005', 'PLACE': 'A5', 'LS': 'x', 'REC': 'x'},  # 4
        {'CHILD': '606', 'PLACE': 'A6', 'LS': 'V2', 'REC': 'x'},  # 5
        {'CHILD': '77', 'PLACE': 'x', 'LS': 'x', 'REC': 'x'},  # 6
    ])
    fake_dfs = {'Episodes': fake_data}
    error_defn, error_func = validate_378()
    result = error_func(fake_dfs)
    assert result == {'Episodes': [3]}


def test_validate_398():
    fake_data = pd.DataFrame({
        'HOME_POST': ['AB1 0JD', 'invalid', 'AB1 0JD', 'invalid', 'AB10JD', ],
        'LS': ['V3', 'U1', 'V4', 'T1', 'U1'],
        'PL_POST': ['AB1 0JD', 'AB1 0JD', pd.NA, 'invalid', 'AB1 0JD', ],
    })
    fake_dfs = {'Episodes': fake_data}
    error_defn, error_func = validate_398()
    result = error_func(fake_dfs)
    assert result == {'Episodes': [0, 2]}


def test_validate_451():
    fake_data = pd.DataFrame({
        'CHILD': ['101', '102', '101', '102', '103', '104'],
        'REC': ['E11', 'E12', 'X1', pd.NA, 'E11', 'E11'],
        'DEC': ['15/03/2021', '17/06/2020', '20/03/2020', pd.NA, '23/08/2020', pd.NA],
        'LS': ['J2', 'X', 'J2', 'D1', 'D', 'D1']})
    fake_dfs = {'Episodes': fake_data}
    error_defn, error_func = validate_451()
    result = error_func(fake_dfs)
    assert result == {'Episodes': [3]}


def test_validate_519():
    fake_data = pd.DataFrame({
        'LS_ADOPTR': ['L2', 'L4', pd.NA, 'L2', 'L2', 'L2', 'L4'],
        'SEX_ADOPTR': ['MM', 'FF', 'MM', 'M1', 'MF', pd.NA, 'xxxxx'],
    })

    fake_dfs = {'AD1': fake_data}

    error_defn, error_func = validate_519()

    result = error_func(fake_dfs)

    assert result == {'AD1': [3, 5]}


def test_validate_520():
    fake_ad1 = pd.DataFrame({
        'LS_ADOPTR': ['L11', 'L11', pd.NA, 'L4', 'L11', 'L1', 'L4'],
        'SEX_ADOPTR': ['MM', 'FF', 'MM', 'M1', 'MF', 'F1', 'xxxxx'],
    })
    fake_dfs = {'AD1': fake_ad1}
    error_defn, error_func = validate_520()
    result = error_func(fake_dfs)
    assert result == {'AD1': [0, 1]}


def test_validate_522():
    fake_placed_data = pd.DataFrame([
        {'CHILD': '11', 'DATE_PLACED_CEASED': '26/05/2000', 'DATE_PLACED': '26/05/2000'},  # 0
        {'CHILD': '202', 'DATE_PLACED_CEASED': '01/02/2003', 'DATE_PLACED': '26/05/2000'},  # 1
        {'CHILD': '3003', 'DATE_PLACED_CEASED': '26/05/2000', 'DATE_PLACED': pd.NA},  # 2
        {'CHILD': '40004', 'DATE_PLACED_CEASED': '26/05/2000', 'DATE_PLACED': '01/02/2003'},  # 3 Fail
        {'CHILD': '606', 'DATE_PLACED_CEASED': pd.NA, 'DATE_PLACED': '26/05/2000'},  # 4
    ])
    fake_dfs = {'PlacedAdoption': fake_placed_data}
    error_defn, error_func = validate_522()
    result = error_func(fake_dfs)
    assert result == {'PlacedAdoption': [3]}


def test_validate_563():
    fake_placed = pd.DataFrame([
        {'CHILD': '11', 'DATE_PLACED_CEASED': pd.NA, 'REASON_PLACED_CEASED': pd.NA, 'DATE_PLACED': '26/05/2000'},  # 0
        {'CHILD': '202', 'DATE_PLACED_CEASED': '01/02/2003', 'REASON_PLACED_CEASED': 'invalid dont matter',
         'DATE_PLACED': '26/05/2000'},  # 1
        {'CHILD': '3003', 'DATE_PLACED_CEASED': pd.NA, 'REASON_PLACED_CEASED': pd.NA, 'DATE_PLACED': '26/05/2000'},  # 2
        {'CHILD': '40004', 'DATE_PLACED_CEASED': '26/05/2001', 'REASON_PLACED_CEASED': 'some sample reason',
         'DATE_PLACED': pd.NA},  # 3: Fail
        {'CHILD': '606', 'DATE_PLACED_CEASED': pd.NA, 'REASON_PLACED_CEASED': pd.NA, 'DATE_PLACED': '26/05/2000'},  # 4
    ])

    fake_dfs = {'PlacedAdoption': fake_placed}
    error_defn, error_func = validate_563()
    result = error_func(fake_dfs)
    assert result == {'PlacedAdoption': [3]}


def test_validate_544():
    fake_data = pd.DataFrame({
        'CONVICTED': [pd.NA, 1, '1', 1, '1', 1, '1', 1, '1', 1],
        'IMMUNISATIONS': [pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, 1],
        'TEETH_CHECK': [pd.NA, pd.NA, pd.NA, pd.NA, '1', pd.NA, pd.NA, pd.NA, pd.NA, 1],
        'HEALTH_ASSESSMENT': [pd.NA, pd.NA, pd.NA, pd.NA, '1', pd.NA, pd.NA, pd.NA, pd.NA, 1],
        'SUBSTANCE_MISUSE': [pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, 1],
    })

    fake_dfs = {'OC2': fake_data}

    error_defn, error_func = validate_544()

    result = error_func(fake_dfs)

    assert result == {'OC2': [1, 2, 3, 4, 5, 6, 7, 8]}

def test_validate_158():
    fake_data = pd.DataFrame({
        'INTERVENTION_RECEIVED': ['1', pd.NA, '0', '1', '1', '0'],
        'INTERVENTION_OFFERED': [pd.NA, '1', '0', '1', '0', '1'],
    })

    fake_dfs = {'OC2': fake_data}

    error_defn, error_func = validate_158()

    result = error_func(fake_dfs)

    assert result == {'OC2': [3, 4]}


def test_validate_133():
    fake_data = pd.DataFrame({
        'ACCOM': ['B1', 'B2', pd.NA, 'S2', 'K1', 'X', '1'],
    })

    fake_dfs = {'OC3': fake_data}

    error_defn, error_func = validate_133()

    result = error_func(fake_dfs)

    assert result == {'OC3': [5, 6]}


def test_validate_565():
    fake_data = pd.DataFrame([
        {'MISSING': 'M', 'MIS_START': pd.NA},  # 0
        {'MISSING': pd.NA, 'MIS_START': '07/02/2020'},  # 1
        {'MISSING': 'A', 'MIS_START': '03/02/2020'},  # 2
        {'MISSING': pd.NA, 'MIS_START': pd.NA},  # 3
        {'MISSING': 'M', 'MIS_START': pd.NA},  # 4
        {'MISSING': 'A', 'MIS_START': '13/02/2020'},  # 5
    ])

    fake_dfs = {'Missing': fake_data}

    error_defn, error_func = validate_565()

    assert error_func(fake_dfs) == {'Missing': [1]}


def test_validate_433():
    fake_data_episodes = pd.DataFrame([
        {'CHILD': '101', 'DECOM': '20/10/2021', 'RNE': 'S', 'DEC': '20/11/2021'},  # 0: Ignore
        {'CHILD': '102', 'DECOM': '19/11/2021', 'RNE': 'P', 'DEC': pd.NA},  # 1 [102:2nd]
        {'CHILD': '102', 'DECOM': '17/06/2021', 'RNE': 'P', 'DEC': '19/11/2021'},  # 2 [102:1st]
        {'CHILD': '103', 'DECOM': '04/04/2020', 'RNE': 'B', 'DEC': '12/09/2020'},  # 3 [103:1st]
        {'CHILD': '103', 'DECOM': '11/09/2020', 'RNE': 'B', 'DEC': '06/05/2021'},  # 4 [103:2nd] ]Fail!
        {'CHILD': '103', 'DECOM': '07/05/2021', 'RNE': 'B', 'DEC': pd.NA},  # 5 [103:3rd] Fail!
    ])

    fake_dfs = {'Episodes': fake_data_episodes}

    error_defn, error_func = validate_433()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [4, 5]}


def test_validate_437():
    fake_data_episodes = pd.DataFrame({
        'CHILD': ['101', '102', '102', '103', '103', '103', '104', '104', '104', '104', '105', '105'],
        'DECOM': ['20/10/2021', '19/11/2021', '17/06/2021', '04/04/2020', '11/09/2020', '07/05/2021', '15/02/2020',
                  '09/04/2020', '24/09/2020', '30/06/2021', pd.NA, '20/12/2020'],
        'REC': ['E2', 'E15', 'X1', 'X1', 'E15', pd.NA, 'X1', 'E4a', 'X1', pd.NA, 'E2', 'X1'],
    })

    fake_dfs = {'Episodes': fake_data_episodes}

    error_defn, error_func = validate_437()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [4]}


def test_validate_547():
    fake_data = pd.DataFrame({
        'HEALTH_CHECK': [pd.NA, 1, '1', 1,
                         '1', 0, 1, pd.NA],
        'IMMUNISATIONS': [pd.NA, pd.NA, pd.NA, 1,
                          pd.NA, pd.NA, 1, pd.NA],
        'TEETH_CHECK': [pd.NA, pd.NA, pd.NA, '1',
                        '1', pd.NA, 1, '1'],
        'HEALTH_ASSESSMENT': [pd.NA, pd.NA, pd.NA, 0,
                              '1', pd.NA, 1, 0],
        'SUBSTANCE_MISUSE': [pd.NA, pd.NA, pd.NA, 0,
                             pd.NA, pd.NA, 1, '1'],
    })

    fake_dfs = {'OC2': fake_data}

    error_defn, error_func = validate_547()

    result = error_func(fake_dfs)

    assert result == {'OC2': [1, 2, 4]}


def test_validate_635():
    fake_data_prevperm = pd.DataFrame({
        'CHILD': ['2', '4', '5', '6', '7', '8'],
        'PREV_PERM': ['Z1', pd.NA, pd.NA, 'Z1', pd.NA, 'P1'],
        'LA_PERM': [pd.NA, '352', pd.NA, '352', pd.NA, '352'],
        'DATE_PERM': [pd.NA, pd.NA, '01/05/2000', pd.NA, pd.NA, '05/05/2020'],
    })

    fake_dfs = {'PrevPerm': fake_data_prevperm}
    error_defn, error_func = validate_635()
    result = error_func(fake_dfs)
    assert result == {'PrevPerm': [1, 2]}


def test_validate_217():
    fake_data = pd.DataFrame({
        'PLACE': ['A3', 'A5', 'A3', pd.NA, 'U1', 'A3', 'A5', 'A5'],
        'DECOM': ['01/04/2015', '31/12/2015', '20/01/2016', pd.NA, '01/10/2017', '20/02/2016', '01/01/2017',
                  '01/04/2013'],
        'RNE': ['S', 'T', 'U', pd.NA, 'X', 'X', 'X', 'X'],
    })

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_217()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [5, 6]}


def test_validate_518():
    fake_data = pd.DataFrame({
        'LS_ADOPTR': ['L4', 'L4', pd.NA, 'L4', 'L4', 'L1', 'L4'],
        'SEX_ADOPTR': ['MM', 'FF', 'MM', 'M1', 'MF', 'F1', 'xxxxx'],
    })

    fake_dfs = {'AD1': fake_data}

    error_defn, error_func = validate_518()

    result = error_func(fake_dfs)

    assert result == {'AD1': [3, 4, 6]}


def test_validate_517():
    fake_data = pd.DataFrame({
        'LS_ADOPTR': ['L3', 'L1', pd.NA, 'L3', 'L3', 'L4', 'L3'],
        'SEX_ADOPTR': ['MF', 'MF', 'MM', 'M1', 'FF', 'F1', 'xxxxx'],
    })

    fake_dfs = {'AD1': fake_data}

    error_defn, error_func = validate_517()

    result = error_func(fake_dfs)

    assert result == {'AD1': [3, 4, 6]}


def test_validate_558():
    fake_data_episodes = pd.DataFrame({
        'CHILD': ['0', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'],
        'REC': ['x', 'E11', 'E12', 'E11', 'E12', 'E11', 'E12', 'E11', 'E11', 'A3'],
    })
    fake_data_placed_adoption = pd.DataFrame({
        'CHILD': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'],
        'DATE_PLACED_CEASED': [pd.NA, pd.NA, pd.NA, pd.NA, '01/01/2020', '15/04/2020', pd.NA, '28th Jan 1930'],
    })

    fake_dfs = {'Episodes': fake_data_episodes, 'PlacedAdoption': fake_data_placed_adoption}

    error_defn, error_func = validate_558()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [5, 6, 8]}


def test_validate_185():
    metadata = {'collection_start': '01/04/1980',
                'collection_end': '31/03/1981'}

    eps = pd.DataFrame([
        {'CHILD': '1', 'DECOM': '01/03/1980', 'DEC': '31/03/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},
        {'CHILD': '2', 'DECOM': '01/03/1980', 'DEC': '30/03/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},
        {'CHILD': '3', 'DECOM': '01/03/1980', 'DEC': '01/01/1981', 'LS': 'V3', 'REC': 'X1', 'RNE': 'o'},  # False
        {'CHILD': '4', 'DECOM': '01/02/1970', 'DEC': pd.NA, 'LS': 'o', 'REC': '!!', 'RNE': 'o'},
        {'CHILD': '5555', 'DECOM': '01/03/1979', 'DEC': '01/01/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},
        {'CHILD': '5555', 'DECOM': '01/01/1981', 'DEC': pd.NA, 'LS': 'o', 'REC': pd.NA, 'RNE': 'o'},
        {'CHILD': '6', 'DECOM': '01/03/1979', 'DEC': '01/01/1981', 'LS': 'o', 'REC': '!!', 'RNE': 'o'},  # !! - False
        {'CHILD': '6', 'DECOM': '01/01/1981', 'DEC': pd.NA, 'LS': 'o', 'REC': pd.NA, 'RNE': 'o'},  # False
        {'CHILD': '7777', 'DECOM': '01/03/1979', 'DEC': '01/01/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},  # False
        {'CHILD': '7777', 'DECOM': '01/01/1981', 'DEC': '01/07/1981', 'LS': 'o', 'REC': 'o', 'RNE': 'S'},  # !! - False
        {'CHILD': '8', 'DECOM': '01/01/1981', 'DEC': '31/03/1999', 'LS': 'o', 'REC': 'o', 'RNE': 'S'},  # False
    ])

    oc2 = pd.DataFrame({'CHILD': ['999999', '1', '2', '3', '9999', '8'],
                        'SDQ_SCORE': ['!!!!!', pd.NA, 'OO', '!!', pd.NA, '!!']})

    fake_dfs = {'Episodes': eps,
                'OC2': oc2,
                'metadata': metadata}

    error_defn, error_func = validate_185()

    result = error_func(fake_dfs)

    assert result == {'OC2': [0, 3, 5]}


def test_validate_186():
    metadata = {'collection_start': '01/04/1980',
                'collection_end': '31/03/1981'}

    eps = pd.DataFrame([
        {'CHILD': '1', 'DECOM': '01/03/1980', 'DEC': '31/03/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},
        {'CHILD': '2', 'DECOM': '01/03/1980', 'DEC': '30/03/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},
        {'CHILD': '3', 'DECOM': '01/03/1980', 'DEC': '01/01/1981', 'LS': 'V3', 'REC': 'X1', 'RNE': 'o'},  # False
        {'CHILD': '4', 'DECOM': '01/02/1970', 'DEC': pd.NA, 'LS': 'o', 'REC': '!!', 'RNE': 'o'},
        {'CHILD': '5555', 'DECOM': '01/03/1979', 'DEC': '01/01/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},
        {'CHILD': '5555', 'DECOM': '01/01/1981', 'DEC': pd.NA, 'LS': 'o', 'REC': pd.NA, 'RNE': 'o'},
        {'CHILD': '6', 'DECOM': '01/03/1979', 'DEC': '01/01/1981', 'LS': 'o', 'REC': '!!', 'RNE': 'o'},  # !! - False
        {'CHILD': '6', 'DECOM': '01/01/1981', 'DEC': pd.NA, 'LS': 'o', 'REC': pd.NA, 'RNE': 'o'},  # False
        {'CHILD': '7777', 'DECOM': '01/03/1979', 'DEC': '01/01/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},  # False
        {'CHILD': '7777', 'DECOM': '01/01/1981', 'DEC': '01/07/1981', 'LS': 'o', 'REC': 'o', 'RNE': 'S'},  # !! - False
        {'CHILD': '8', 'DECOM': '01/01/1981', 'DEC': '31/03/1999', 'LS': 'o', 'REC': 'o', 'RNE': 'S'},  # False
    ])

    oc2 = pd.DataFrame({'CHILD': ['999999', '1', '2', '3',
                                  '9999', '8', '5555'],
                        'DOB': ['01/01/1974', '01/04/1976', '01/01/1978', '01/01/1974',
                                '01/01/1974', '01/01/1974', '01/01/1955'],
                        'SDQ_SCORE': ['OO', pd.NA, 'OO', 'OO',
                                      pd.NA, pd.NA, pd.NA]})

    fake_dfs = {'Episodes': eps,
                'OC2': oc2,
                'metadata': metadata}

    error_defn, error_func = validate_186()

    result = error_func(fake_dfs)

    assert result == {'OC2': [1, ]}


def test_validate_187():
    metadata = {'collection_start': '01/04/1980',
                'collection_end': '31/03/1981'}

    eps = pd.DataFrame([
        {'CHILD': '1', 'DECOM': '01/03/1980', 'DEC': '31/03/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},
        {'CHILD': '2', 'DECOM': '01/03/1980', 'DEC': '30/03/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},
        {'CHILD': '3333', 'DECOM': '01/03/1980', 'DEC': '01/01/1981', 'LS': 'V3', 'REC': 'X1', 'RNE': 'o'},  # False
        {'CHILD': '4', 'DECOM': '01/02/1970', 'DEC': pd.NA, 'LS': 'o', 'REC': '!!', 'RNE': 'o'},
        {'CHILD': '5', 'DECOM': '01/03/1979', 'DEC': '01/01/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},
        {'CHILD': '5', 'DECOM': '01/01/1981', 'DEC': pd.NA, 'LS': 'o', 'REC': pd.NA, 'RNE': 'o'},
        {'CHILD': '6666', 'DECOM': '01/03/1979', 'DEC': '01/01/1981', 'LS': 'o', 'REC': '!!', 'RNE': 'o'},  # !! - False
        {'CHILD': '6666', 'DECOM': '01/01/1981', 'DEC': pd.NA, 'LS': 'o', 'REC': pd.NA, 'RNE': 'o'},  # False
        {'CHILD': '7777', 'DECOM': '01/03/1979', 'DEC': '01/01/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},  # False
        {'CHILD': '7777', 'DECOM': '01/01/1981', 'DEC': '01/07/1981', 'LS': 'o', 'REC': 'o', 'RNE': 'S'},  # !! - False
        {'CHILD': '8888', 'DECOM': '01/01/1981', 'DEC': '31/03/1999', 'LS': 'o', 'REC': 'o', 'RNE': 'S'},  # False
        {'CHILD': '9', 'DECOM': '05/04/1980', 'DEC': pd.NA, 'LS': 'o', 'REC': 'xx', 'RNE': 'S'},
        # nCLA True DECOM>col_start and RNE==S
        {'CHILD': '10', 'DECOM': pd.NA, 'DEC': '05/04/1980', 'LS': 'o', 'REC': 'xx', 'RNE': 'S'},
        # nCLA True DEC>col_start and REC!=X1
        {'CHILD': '11', 'DECOM': pd.NA, 'DEC': '05/04/1980', 'LS': 'V3', 'REC': pd.NA, 'RNE': 'S'},
        # nCLA True DEC>col_start and LS in [V3, V4]

    ])

    oc3 = pd.DataFrame({
        'CHILD':
            ['9999999999', '1', '2', '3333',
             '99999999', '8888', '5', '9', '10', '11'],
        'IN_TOUCH':
            ['OK', '!!!', pd.NA, 'OK',
             pd.NA, pd.NA, pd.NA, 'xx', 'xx', 'xx'],
    })
    other_oc3_cols = ['ACTIV', 'ACCOM']
    oc3 = oc3.assign(**{col: pd.NA for col in other_oc3_cols})

    ad1 = pd.DataFrame({
        'CHILD':
            ['1', '2', '3333', '7777',
             '99999999', '8888', '5', '9', '10', '11'],
        'DATE_INT':
            [pd.NA, pd.NA, 'OK', 'OK',
             pd.NA, pd.NA, '!!!', 'xx', 'xx', 'xx'],
    })

    other_ad1_cols = ['DATE_MATCH', 'FOSTER_CARE', 'NB_ADOPTR', 'SEX_ADOPTR', 'LS_ADOPTR']
    ad1 = ad1.assign(**{col: pd.NA for col in other_ad1_cols})

    fake_dfs = {'Episodes': eps,
                'OC3': oc3,
                'AD1': ad1,
                'metadata': metadata}

    error_defn, error_func = validate_187()

    result = error_func(fake_dfs)

    assert result == {'OC3': [1, ],
                      'AD1': [6, ]}


def test_validate_188():
    metadata = {'collection_end': '31/03/1981'}

    oc2 = pd.DataFrame({
        'CHILD': ['0', '1', '2', '3', '4'],
        'DOB': ['01/01/1970', '01/01/1980', '01/01/1970', '31/03/1977', '01/04/1977'],
        'SDQ_SCORE': ['OK', '!!!', pd.NA, 'OK', '!!!']
    })

    oc2['SDQ_REASON'] = pd.NA

    fake_dfs = {'OC2': oc2,
                'metadata': metadata}

    error_defn, error_func = validate_188()

    result = error_func(fake_dfs)

    assert result == {'OC2': [1, 4]}


def test_validate_189():
    metadata = {'collection_start': '01/04/1980'}

    oc2 = pd.DataFrame({
        'CHILD': ['0', '1', '2', '3'],
        'DOB': ['01/04/1963', '02/04/1963', '01/01/1970', '31/03/1960'],
        'SDQ_SCORE': ['!!!', 'OK', pd.NA, pd.NA],
        'SDQ_REASON': [pd.NA, pd.NA, pd.NA, pd.NA]
    })

    fake_dfs = {'OC2': oc2,
                'metadata': metadata}

    error_defn, error_func = validate_189()

    result = error_func(fake_dfs)

    assert result == {'OC2': [0, ]}


def test_validate_190():
    metadata = {'collection_start': '01/04/1980',
                'collection_end': '31/03/1981'}

    eps = pd.DataFrame([
        {'CHILD': '1', 'DECOM': '01/03/1980', 'DEC': '31/03/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},
        {'CHILD': '2', 'DECOM': '01/03/1980', 'DEC': '30/03/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},
        {'CHILD': '3333', 'DECOM': '01/03/1980', 'DEC': '01/01/1981', 'LS': 'V3', 'REC': 'X1', 'RNE': 'o'},  # False
        {'CHILD': '4', 'DECOM': '01/02/1970', 'DEC': pd.NA, 'LS': 'o', 'REC': '!!', 'RNE': 'o'},
        {'CHILD': '5', 'DECOM': '01/03/1979', 'DEC': '01/01/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},
        {'CHILD': '5', 'DECOM': '01/01/1981', 'DEC': pd.NA, 'LS': 'o', 'REC': pd.NA, 'RNE': 'o'},
        {'CHILD': '6666', 'DECOM': '01/03/1979', 'DEC': '01/01/1981', 'LS': 'o', 'REC': '!!', 'RNE': 'o'},  # !! - False
        {'CHILD': '6666', 'DECOM': '01/01/1981', 'DEC': pd.NA, 'LS': 'o', 'REC': pd.NA, 'RNE': 'o'},  # False
        {'CHILD': '7777', 'DECOM': '01/03/1979', 'DEC': '01/01/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},  # False
        {'CHILD': '7777', 'DECOM': '01/01/1981', 'DEC': '01/07/1981', 'LS': 'o', 'REC': 'o', 'RNE': 'S'},  # !! - False
        {'CHILD': '8888', 'DECOM': '01/01/1981', 'DEC': '31/03/1999', 'LS': 'o', 'REC': 'o', 'RNE': 'S'},  # False
    ])

    oc2 = pd.DataFrame({
        'CHILD':
            ['9999999999', '1', '2', '3333',
             '99999999', '8888', '5'],
        'CONVICTED':
            ['!!!', 'OK', pd.NA, pd.NA,
             pd.NA, '!!!', 'OK'],
    })
    other_oc2_cols = ['HEALTH_CHECK', 'IMMUNISATIONS', 'TEETH_CHECK', 'HEALTH_ASSESSMENT',
                      'SUBSTANCE_MISUSE', 'INTERVENTION_RECEIVED', 'INTERVENTION_OFFERED']
    oc2 = oc2.assign(**{col: pd.NA for col in other_oc2_cols})

    fake_dfs = {'Episodes': eps,
                'OC2': oc2,
                'metadata': metadata}

    error_defn, error_func = validate_190()

    result = error_func(fake_dfs)

    assert result == {'OC2': [0, 5]}


def test_validate_191():
    metadata = {'collection_start': '01/04/1980',
                'collection_end': '31/03/1981'}

    eps = pd.DataFrame([
        {'CHILD': '1', 'DECOM': '01/03/1980', 'DEC': '31/03/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},
        {'CHILD': '2', 'DECOM': '01/03/1980', 'DEC': '30/03/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},
        {'CHILD': '3333', 'DECOM': '01/03/1980', 'DEC': '01/01/1981', 'LS': 'V3', 'REC': 'X1', 'RNE': 'o'},  # False
        {'CHILD': '4', 'DECOM': '01/02/1970', 'DEC': pd.NA, 'LS': 'o', 'REC': '!!', 'RNE': 'o'},
        {'CHILD': '5', 'DECOM': '01/03/1979', 'DEC': '01/01/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},
        {'CHILD': '5', 'DECOM': '01/01/1981', 'DEC': pd.NA, 'LS': 'o', 'REC': pd.NA, 'RNE': 'o'},
        {'CHILD': '6666', 'DECOM': '01/03/1979', 'DEC': '01/01/1981', 'LS': 'o', 'REC': '!!', 'RNE': 'o'},  # !! - False
        {'CHILD': '6666', 'DECOM': '01/01/1981', 'DEC': pd.NA, 'LS': 'o', 'REC': pd.NA, 'RNE': 'o'},  # False
        {'CHILD': '7777', 'DECOM': '01/03/1979', 'DEC': '01/01/1981', 'LS': 'o', 'REC': 'X1', 'RNE': 'o'},  # False
        {'CHILD': '7777', 'DECOM': '01/01/1981', 'DEC': '01/07/1981', 'LS': 'o', 'REC': 'o', 'RNE': 'S'},  # !! - False
        {'CHILD': '8888', 'DECOM': '01/01/1981', 'DEC': '31/03/1999', 'LS': 'o', 'REC': 'o', 'RNE': 'S'},  # False
    ])

    oc2 = pd.DataFrame({
        'CHILD':
            ['9999999999', '1', '2', '3333',
             '99999999', '8888', '5'],
        'IMMUNISATIONS':
            ['OK', pd.NA, 'OK', pd.NA,
             pd.NA, 'OK', pd.NA],
    })
    other_oc2_cols = ['HEALTH_CHECK', 'CONVICTED', 'TEETH_CHECK', 'HEALTH_ASSESSMENT',
                      'SUBSTANCE_MISUSE', 'INTERVENTION_RECEIVED', 'INTERVENTION_OFFERED']
    oc2 = oc2.assign(**{col: 'Filled In!' for col in other_oc2_cols})

    fake_dfs = {'Episodes': eps,
                'OC2': oc2,
                'metadata': metadata}

    error_defn, error_func = validate_191()

    result = error_func(fake_dfs)

    assert result == {'OC2': [1, 6]}


def test_validate_516():
    fake_data = pd.DataFrame({
        'REC': ['E45', 'E46', pd.NA, 'E45',
                'E46', 'E45', 'E45', 'E2',
                'E2', 'E46', 'E46', 'E46'],
        'PLACE': ['U1', 'U2', 'U3', 'Z1',
                  'S1', 'R1', 'U4', 'K2',
                  'K2', 'T1', 'U6', 'xx'],
    })

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_516()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [3, 4, 5, 9, 11]}


def test_validate_511():
    fake_data = pd.DataFrame({
        'NB_ADOPTR': ['2', '2', pd.NA, 2,
                      '2', '1', 2, 1, 2],
        'SEX_ADOPTR': ['MM', 'FF', 'MM', 'M1', 'F1',
                       'F1', 'F1', 'F1', pd.NA],
    })

    fake_dfs = {'AD1': fake_data}

    error_defn, error_func = validate_511()

    result = error_func(fake_dfs)

    assert result == {'AD1': [3, 4, 6]}


def test_validate_524():
    fake_data = pd.DataFrame({
        'LS_ADOPTR': ['L12', 'L12', pd.NA, 'L12', 'L12', 'L4', 'L12'],
        'SEX_ADOPTR': ['MM', 'FF', 'MM', 'M1', 'MF', 'F1', 'xxxxx'],
    })

    fake_dfs = {'AD1': fake_data}

    error_defn, error_func = validate_524()

    result = error_func(fake_dfs)

    assert result == {'AD1': [3, 4, 6]}


def test_validate_441():
    fake_data = pd.DataFrame({
        'DOB': ['01/01/2004', '01/01/2006', '01/01/2007', '01/01/2008', '01/01/2010', '01/01/2012', '01/01/2014',
                '01/06/2014'],
        'REVIEW': ['31/12/2008', '01/01/2012', pd.NA, '01/01/2009', '01/01/2012', '01/01/2017', '01/01/2021',
                   '01/01/2015'],
        'REVIEW_CODE': ['PN1', 'PN2', 'PN3', 'PN4', 'PN5', 'PN6', 'PN7', 'PN0'],
    })

    fake_dfs = {'Reviews': fake_data}

    error_defn, error_func = validate_441()

    result = error_func(fake_dfs)

    assert result == {'Reviews': [3, 4]}


def test_validate_184():
    fake_data_header = pd.DataFrame({
        'CHILD': ['111', '112', '113', '114'],
        'DOB': ['01/10/2017', '31/05/2018', '10/03/2019', '19/08/2020'],
    })
    fake_data_placed = pd.DataFrame({
        'CHILD': ['111', '112', '113', '114'],
        'DATE_PLACED': ['01/10/2017', '10/02/2019', '10/02/2019', pd.NA],
    })

    fake_dfs = {'Header': fake_data_header, 'PlacedAdoption': fake_data_placed}

    error_defn, error_func = validate_184()

    result = error_func(fake_dfs)

    assert result == {'PlacedAdoption': [2]}


def test_validate_612():
    fake_data = pd.DataFrame({
        'SEX': [2, '2', '2', 2,
                2, 1, 1, 1, '2'],
        'MOTHER': ['0', '0', pd.NA, pd.NA,
                   1, 0, 1, pd.NA, pd.NA],
        'MC_DOB': ['19/02/2016', 'dd/mm/yyyy', '31/31/19', pd.NA,
                   '19/02/2019', pd.NA, '12/10/2010', '21/3rd/yYyYyY', '21/3rd/yYyYyY'],
    })

    fake_dfs = {'Header': fake_data}

    error_defn, error_func = validate_612()

    result = error_func(fake_dfs)

    assert result == {'Header': [0, 1, 2, 8]}


def test_validate_552():
    fake_placed_adoption = pd.DataFrame({
        'DATE_PLACED': ['08/03/2020', '22/06/2020', '13/10/2022', '24/10/2021', pd.NA, pd.NA, 'baddate/2021'],
        "CHILD": ['104', '105', '107', '108', '109', '110', '111'],
    })
    fake_episodes = pd.DataFrame({
        'DECOM': ['08/03/2020', '22/07/2020', '13/10/2021', '22/06/2020', '26/05/2018', pd.NA, '01/02/2013'],
        "CHILD": ['104', '105', '107', '108', '109', '110', '111'],
        "PLACE": ['A3', 'A4', 'A6', 'D5', 'A3', 'A5', 'A4']
    })

    fake_dfs = {"PlacedAdoption": fake_placed_adoption, "Episodes": fake_episodes}
    # get the error function
    error_defn, error_func = validate_552()
    result = error_func(fake_dfs)
    # check that result of function on provided data is as expected
    assert result == {"PlacedAdoption": [2], "Episodes": [2]}


def test_validate_551():
    fake_data_episodes = pd.DataFrame({
        'CHILD': ['0', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'],
        'PLACE': ['x', 'A3', 'A4', 'A5', 'A6', 'A3', 'A4', 'x', 'A3', 'A5'],
    })
    fake_data_placed_adoption = pd.DataFrame({
        'CHILD': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'],
        'DATE_PLACED': [pd.NA, pd.NA, pd.NA, pd.NA, '01/01/2020', '15/04/2020', pd.NA, '28th Jan 1930'],
    })

    fake_dfs = {'Episodes': fake_data_episodes, 'PlacedAdoption': fake_data_placed_adoption}

    error_defn, error_func = validate_551()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [1, 2, 3, 4, 9]}


def test_validate_557():
    test_episodes = pd.DataFrame([
        {'CHILD': '11', 'PLACE': 'A3', 'LS': 'x', 'REC': 'x'},  # 0: Fail! (missing vals in PA)
        {'CHILD': '202', 'PLACE': 'x', 'LS': 'D1', 'REC': 'x'},  # 1: PA filled in --ok
        {'CHILD': '3003', 'PLACE': 'A4', 'LS': 'D1', 'REC': 'E12'},  # 2: E12 --ok
        {'CHILD': '40004', 'PLACE': 'x', 'LS': 'E1', 'REC': 'E12'},  # 3: E12 --ok
        {'CHILD': '5005', 'PLACE': 'A5', 'LS': 'x', 'REC': 'x'},  # 4: Fail! (not in PA)
        {'CHILD': '606', 'PLACE': 'A6', 'LS': 'x', 'REC': 'x'},  # 5: Fail! (missing vals in PA)
        {'CHILD': '77', 'PLACE': 'x', 'LS': 'x', 'REC': 'x'},  # 6 --ok
        {'CHILD': '8', 'PLACE': 'A6', 'LS': 'x', 'REC': 'X1'},  # 5: --ok (REC is X1)
    ])

    test_placed = pd.DataFrame([
        {'CHILD': '11', 'DATE_PLACED_CEASED': pd.NA, 'REASON_PLACED_CEASED': pd.NA},  # 0: Fail!
        {'CHILD': '202', 'DATE_PLACED_CEASED': '01/02/2003', 'REASON_PLACED_CEASED': 'invalid dont matter'},  # 1
        {'CHILD': '3003', 'DATE_PLACED_CEASED': pd.NA, 'REASON_PLACED_CEASED': pd.NA},  # 2: E12 in EP --ok
        {'CHILD': '40004', 'DATE_PLACED_CEASED': pd.NA, 'REASON_PLACED_CEASED': pd.NA},  # 3: E12 in EP  --ok
        {'CHILD': '606', 'DATE_PLACED_CEASED': pd.NA, 'REASON_PLACED_CEASED': pd.NA},  # 4: Fail! (missing vals in PA)

    ])

    fake_dfs = {
        'Episodes': test_episodes,
        'PlacedAdoption': test_placed,
    }

    error_defn, error_func = validate_557()

    result = error_func(fake_dfs)

    assert result == {
        'PlacedAdoption': [0, 4],
        'Episodes': [0, 4, 5],
    }


def test_validate_207():
    fake_data = pd.DataFrame({
        'CHILD': ['101', '102', '103', '104', '105', '106', '108', '109', '110'],
        'MOTHER': ['1', 0, '1', pd.NA, pd.NA, '1', pd.NA, '0', '2'],
    })

    fake_data_prev = pd.DataFrame({
        'CHILD': ['101', '102', '103', '104', '105', '107', '108', '109', '110'],
        'MOTHER': ['1', 1, '0', 1, pd.NA, '1', '0', pd.NA, '1'],
    })

    fake_dfs = {'Header': fake_data, 'Header_last': fake_data_prev}

    error_defn, error_func = validate_207()

    result = error_func(fake_dfs)

    assert result == {'Header': [1, 3, 8]}


def test_validate_523():
    fake_placed_adoption = pd.DataFrame({
        "DATE_PLACED": ['08/03/2020', '22/06/2020', '13/10/2022', '24/10/2021',
                        pd.NA, pd.NA, '£1st/Februart', '11/11/2020'],
        "CHILD": [1, 2, 3, 4,
                  5, 6, 7, 10]
    })
    fake_ad1 = pd.DataFrame({
        "DATE_INT": ['08/03/2020', '22/07/2020', '13/10/2021', '22/06/2020',
                     '26/05/2018', pd.NA, '01/10/2020', '01/10/2020'],
        "CHILD": [1, 2, 3, 4,
                  5, 6, 7, 333]})

    fake_dfs = {"AD1": fake_ad1, "PlacedAdoption": fake_placed_adoption}

    # get the error function and run it on the fake data
    error_defn, error_func = validate_523()
    result = error_func(fake_dfs)
    assert result == {"AD1": [1, 2, 3], "PlacedAdoption": [1, 2, 3]}


def test_validate_3001():
    fake_data = pd.DataFrame({
        'CHILD': ['101', '102', '101', '102', '103', '102'],
        'ACCOM': ['Z1', 'Z2', 'T1', pd.NA, 'Z1', 'Z3'],
    })

    fake_data_child = pd.DataFrame({
        'CHILD': ['101', '102', '103'],
        'DOB': ['16/03/2004', '23/09/2003', '31/12/2006'],
    })

    metadata = {
        'collection_start': '01/04/2020',
        'collection_end': '31/03/2021'
    }

    fake_dfs = {'OC3': fake_data, 'Header': fake_data_child, 'metadata': metadata}

    error_defn, error_func = validate_3001()

    result = error_func(fake_dfs)

    assert result == {'OC3': [0, 1]}


def test_validate_389():
    fake_data = pd.DataFrame({
        'CHILD': ['101', '102', '101', '102', '103'],
        'REC': ['E7', 'E7', 'X1', pd.NA, 'E7'],
        'DEC': ['16/03/2021', '17/06/2020', '20/03/2020', pd.NA, '23/08/2020'],
    })

    fake_data_child = pd.DataFrame({
        'CHILD': ['101', '102', '103', '103'],
        'DOB': ['16/03/2005', '23/09/2002', '31/12/2014', '31/12/2014'],
    })

    fake_dfs = {'Episodes': fake_data, 'Header': fake_data_child}

    error_defn, error_func = validate_389()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [4]}


def test_validate_387():
    fake_data = pd.DataFrame({
        'CHILD': ['101', '102', '101', '102', '103', '104', '105'],
        'REC': ['E5', 'E6', 'X1', pd.NA, 'E6', 'E5', 'E6'],
        'DEC': ['16/03/2021', '17/06/2020', '20/03/2020', pd.NA, '23/08/2020', '19XX/33rd', pd.NA],
    })

    fake_data_child = pd.DataFrame({
        'CHILD': ['101', '102', '103', '104', '105', '105'],
        'DOB': ['16/03/2005', '23/09/2002', '31/12/2014', '31/12/2014', '01/01/2004', '01/01/2004'],
    })

    fake_metadata = {'collection_end': '31/03/2021'}

    fake_dfs = {'Episodes': fake_data, 'Header': fake_data_child, 'metadata': fake_metadata}

    error_defn, error_func = validate_387()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [4]}


# -------------------------------
# Tests for 452, 453, 503G & 503H all use these dataframes:

fake_eps__452_453_503G_503H_prev = pd.DataFrame([
    {'CHILD': '101', 'RNE': 'S', 'DECOM': '01/04/2020', 'DEC': '04/06/2020', 'PL_DISTANCE': 400, 'PL_LA': 'WAL'},
    {'CHILD': '101', 'RNE': 'P', 'DECOM': '04/06/2020', 'DEC': pd.NA, 'PL_DISTANCE': 400, 'PL_LA': 'WAL'},
    {'CHILD': '103', 'RNE': 'P', 'DECOM': '03/03/2020', 'DEC': '10/07/2020', 'PL_DISTANCE': 10, 'PL_LA': '816'},
    {'CHILD': '103', 'RNE': 'L', 'DECOM': '10/07/2020', 'DEC': '09/12/2020', 'PL_DISTANCE': 10, 'PL_LA': '816'},
    {'CHILD': '104', 'RNE': 'B', 'DECOM': '28/03/2020', 'DEC': pd.NA, 'PL_DISTANCE': 185, 'PL_LA': '356'},
    {'CHILD': '105', 'RNE': 'L', 'DECOM': '16/04/2020', 'DEC': pd.NA, 'PL_DISTANCE': '165', 'PL_LA': '112'},
    {'CHILD': '106', 'RNE': 'S', 'DECOM': '04/11/2020', 'DEC': pd.NA, 'PL_DISTANCE': '165', 'PL_LA': '112'},
])

fake_eps__452_453_503G_503H = pd.DataFrame([
    {'CHILD': '101', 'RNE': 'P', 'DECOM': '04/06/2020', 'DEC': '04/06/2021', 'PL_DISTANCE': 400, 'PL_LA': 'WAL'},
    {'CHILD': '101', 'RNE': 'P', 'DECOM': '04/06/2021', 'DEC': pd.NA, 'PL_DISTANCE': 400, 'PL_LA': 'WAL'},
    {'CHILD': '102', 'RNE': 'L', 'DECOM': '20/12/2020', 'DEC': '07/04/2021', 'PL_DISTANCE': 10, 'PL_LA': '816'},
    # Ignore all
    {'CHILD': '103', 'RNE': 'L', 'DECOM': '02/02/2021', 'DEC': pd.NA, 'PL_DISTANCE': 10, 'PL_LA': '816'},  # Ignore all
    {'CHILD': '104', 'RNE': 'B', 'DECOM': '28/03/2020', 'DEC': pd.NA, 'PL_DISTANCE': 999.9, 'PL_LA': 'CON'},  # Fail all
    {'CHILD': '105', 'RNE': 'L', 'DECOM': '16/04/2020', 'DEC': pd.NA, 'PL_DISTANCE': 165, 'PL_LA': 112},
    {'CHILD': '106', 'RNE': 'S', 'DECOM': '04/11/2020', 'DEC': pd.NA, 'PL_DISTANCE': pd.NA, 'PL_LA': pd.NA},
    # Fail 452 and 503G only
])

fake_dfs__452_453_503G_503H = {
    'Episodes': fake_eps__452_453_503G_503H,
    'Episodes_last': fake_eps__452_453_503G_503H_prev
}


def test_validate_452():
    error_defn, error_func = validate_452()
    result = error_func(fake_dfs__452_453_503G_503H)
    assert result == {'Episodes': [4, 6]}


def test_validate_503H():
    error_defn, error_func = validate_503H()

    result = error_func(fake_dfs__452_453_503G_503H)

    assert result == {'Episodes': [4, 6]}


def test_validate_453():
    error_defn, error_func = validate_453()

    result = error_func(fake_dfs__452_453_503G_503H)

    assert result == {'Episodes': [4]}


def test_validate_503G():
    error_defn, error_func = validate_503G()

    result = error_func(fake_dfs__452_453_503G_503H)

    assert result == {'Episodes': [4]}


# -------------------------------

def test_validate_386():
    fake_data = pd.DataFrame({
        'CHILD': ['101', '102', '101', '102', '103', '104'],
        'REC': ['E11', 'E12', 'X1', pd.NA, 'E11', 'E11'],
        'DEC': ['15/03/2021', '17/06/2020', '20/03/2020', pd.NA, '23/08/2020', pd.NA],
    })

    fake_data_child = pd.DataFrame({
        'CHILD': ['101', '102', '103', '104'],
        'DOB': ['16/03/2020', '23/09/2002', '31/12/2000', '01/02/2003'],
    })

    fake_dfs = {'Episodes': fake_data, 'Header': fake_data_child}

    error_defn, error_func = validate_386()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [4]}


def test_validate_363():
    test_eps = pd.DataFrame([
        {'CHILD': 101, 'DECOM': '01/01/2000', 'DEC': '01/01/2001', 'LS': 'L3'},  # 0 Fail!
        {'CHILD': 101, 'DECOM': '01/01/2001', 'DEC': '20/12/2001', 'LS': 'X'},  # 1
        {'CHILD': 101, 'DECOM': '20/12/2001', 'DEC': '12/01/2002', 'LS': 'L3'},  # 2 Fail!
        {'CHILD': 2002, 'DECOM': '01/01/2000', 'DEC': '03/01/2000', 'LS': 'L3'},  # 3 ^ Fa
        {'CHILD': 2002, 'DECOM': '03/01/2000', 'DEC': '09/01/2001', 'LS': 'L3'},  # 4 v il!
        {'CHILD': 2002, 'DECOM': '01/01/2002', 'DEC': '07/01/2002', 'LS': 'L3'},  # 5
        {'CHILD': 2002, 'DECOM': '10/01/2002', 'DEC': '11/01/2002', 'LS': 'X'},  # 6
        {'CHILD': 2002, 'DECOM': '11/01/2002', 'DEC': '17/01/2002', 'LS': 'L3'},  # 7
        {'CHILD': 30003, 'DECOM': '25/01/2002', 'DEC': '10/03/2001', 'LS': 'L3'},  # 8 (decom>dec)
        {'CHILD': 30003, 'DECOM': '25/01/2002', 'DEC': pd.NA, 'LS': 'L3'},  # 9 Fail!
        {'CHILD': 30003, 'DECOM': pd.NA, 'DEC': '25/01/2002', 'LS': 'L3'},  # 10 decom.isNA
        {'CHILD': 30003, 'DECOM': pd.NA, 'DEC': pd.NA, 'LS': 'L3'},  # 11
    ])

    test_meta = {'collection_end': '01/04/2002'}

    test_dfs = {
        'Episodes': test_eps,
        'metadata': test_meta
    }

    error_defn, error_func = validate_363()

    result = error_func(test_dfs)

    assert result == {'Episodes': [0, 2, 3, 4, 9]}


def test_validate_364():
    test_eps = pd.DataFrame([
        {'CHILD': 101, 'DECOM': '01/01/2000', 'DEC': '01/01/2001', 'LS': 'J2'},  # 0 Fail!
        {'CHILD': 101, 'DECOM': '01/01/2001', 'DEC': '20/12/2001', 'LS': 'X'},  # 1
        {'CHILD': 101, 'DECOM': '20/12/2001', 'DEC': '12/01/2002', 'LS': 'J2'},  # 2 Fail!
        {'CHILD': 2002, 'DECOM': '01/01/2000', 'DEC': '10/01/2000', 'LS': 'J2'},  # 3 ^ Fa
        {'CHILD': 2002, 'DECOM': '10/01/2000', 'DEC': '23/01/2001', 'LS': 'J2'},  # 4 v il!
        {'CHILD': 2002, 'DECOM': '01/01/2002', 'DEC': '10/01/2002', 'LS': 'J2'},  # 5
        {'CHILD': 2002, 'DECOM': '10/01/2002', 'DEC': '11/01/2002', 'LS': 'X'},  # 6
        {'CHILD': 2002, 'DECOM': '11/01/2002', 'DEC': '25/01/2002', 'LS': 'J2'},  # 7
        {'CHILD': 30003, 'DECOM': '25/01/2002', 'DEC': '10/03/2001', 'LS': 'J2'},  # 8 DEC < DECOM
        {'CHILD': 30003, 'DECOM': '25/01/2002', 'DEC': pd.NA, 'LS': 'J2'},  # 9 Fail!
        {'CHILD': 30003, 'DECOM': pd.NA, 'DEC': '25/01/2002', 'LS': 'J2'},  # 10 decom.isNA
        {'CHILD': 30003, 'DECOM': pd.NA, 'DEC': pd.NA, 'LS': 'J2'},  # 11
    ])

    test_meta = {'collection_end': '01/04/2002'}

    test_dfs = {
        'Episodes': test_eps,
        'metadata': test_meta
    }

    error_defn, error_func = validate_364()

    result = error_func(test_dfs)

    assert result == {'Episodes': [0, 2, 3, 4, 9]}


def test_validate_365():
    test_eps = pd.DataFrame([
        {'CHILD': 101, 'DECOM': '01/01/2000', 'DEC': '01/01/2001', 'LS': 'V3'},  # 0 Fail!
        {'CHILD': 101, 'DECOM': '01/01/2001', 'DEC': '20/12/2001', 'LS': 'X'},  # 1
        {'CHILD': 101, 'DECOM': '20/12/2001', 'DEC': '12/01/2002', 'LS': 'V3'},  # 2 Fail!
        {'CHILD': 2002, 'DECOM': '01/01/2000', 'DEC': '10/01/2000', 'LS': 'V3'},  # 3
        {'CHILD': 2002, 'DECOM': '10/01/2000', 'DEC': '23/01/2001', 'LS': 'X'},  # 4
        {'CHILD': 2002, 'DECOM': '01/01/2002', 'DEC': '18/01/2002', 'LS': 'V3'},  # 5 pass -17 days
        {'CHILD': 2002, 'DECOM': '01/02/2002', 'DEC': '19/02/2002', 'LS': 'V3'},  # 6 Fail! - 18 days
        {'CHILD': 2002, 'DECOM': '11/01/2002', 'DEC': '25/01/2002', 'LS': 'J2'},  # 7
        {'CHILD': 30003, 'DECOM': '25/01/2002', 'DEC': '10/03/2001', 'LS': 'J2'},
        # 8 pass - bigger problems: DEC < DECOM
        {'CHILD': 30003, 'DECOM': '25/01/2002', 'DEC': pd.NA, 'LS': 'V3'},  # 9 Fail! (DEC.isna --> collection_end )
        {'CHILD': 30003, 'DECOM': pd.NA, 'DEC': '25/01/2002', 'LS': 'V3'},  # 10 pass - bigger problems: no DECOM
        {'CHILD': 30003, 'DECOM': pd.NA, 'DEC': pd.NA, 'LS': 'V3'},  # 11 pass - bigger problems: no dates
    ])

    test_meta = {'collection_end': '01/04/2002'}

    test_dfs = {
        'Episodes': test_eps,
        'metadata': test_meta
    }

    error_defn, error_func = validate_365()

    result = error_func(test_dfs)

    assert result == {'Episodes': [0, 2, 6, 9]}


def test_validate_367():
    test_eps = pd.DataFrame([
        {'CHILD': 101, 'DECOM': '01/01/2000', 'DEC': '01/06/2000', 'LS': 'V3'},  # 0 decom-->col_start
        {'CHILD': 2002, 'DECOM': '01/01/2000', 'DEC': '01/05/2000', 'LS': 'V3'},  # 1 decom-->col_start
        {'CHILD': 30003, 'DECOM': '01/04/2000', 'DEC': '01/05/2000', 'LS': 'V3'},  # 2 ^ Fail!
        {'CHILD': 30003, 'DECOM': '01/05/2000', 'DEC': '01/07/2000', 'LS': 'xx'},  # 3 |
        {'CHILD': 30003, 'DECOM': '01/06/2000', 'DEC': '01/07/2000', 'LS': 'V3'},  # 4 | Fail!
        {'CHILD': 30003, 'DECOM': '01/07/2000', 'DEC': '01/08/2000', 'LS': 'V3'},  # 5 v Fail!
        {'CHILD': 400004, 'DECOM': '01/08/2000', 'DEC': '01/07/2000', 'LS': 'V3'},  # 6
        {'CHILD': 400004, 'DECOM': '01/08/2000', 'DEC': '01/11/2000', 'LS': 'V3'},  # 7 Fail!
        {'CHILD': 555, 'DECOM': '01/07/2000', 'DEC': pd.NA, 'LS': 'V3'},  # 8 Fail!
    ])

    test_meta = {'collection_start': '01/04/2000',
                 'collection_end': '01/04/2001'}

    test_dfs = {
        'Episodes': test_eps,
        'metadata': test_meta}

    error_defn, error_func = validate_367()

    result = error_func(test_dfs)

    assert result == {'Episodes': [2, 4, 5, 7, 8]}


def test_validate_440():
    fake_data = pd.DataFrame({
        'DOB': ['01/01/2004', '01/01/2006', '01/01/2007', '01/01/2008', '01/01/2010', '01/01/2012', '01/01/2014'],
        'REVIEW': ['31/12/2007', '01/01/2007', pd.NA, '01/01/2013', '01/01/2015', '01/01/2014', '01/01/2020'],
        'REVIEW_CODE': ['PN0', 'PN0', 'PN0', 'PN0', 'PN0', 'PN0', 'PN1'],
    })

    fake_dfs = {'Reviews': fake_data}

    error_defn, error_func = validate_440()

    result = error_func(fake_dfs)

    assert result == {'Reviews': [3, 4]}


def test_validate_445():
    fake_data = pd.DataFrame({
        'LS': ['D1', 'D1', 'D1', 'D1', 'D1', 'C1'],
        'DECOM': ['01/11/2005', '31/12/2005', pd.NA, '20/01/2006', '01/10/2012', '20/02/2005'],
    })

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_445()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [3, 4]}


def test_validate_446():
    fake_data = pd.DataFrame({
        'LS': ['E1', 'E1', 'E1', 'E1', 'E1', 'C1'],
        'DECOM': ['01/12/2005', '15/05/2012', pd.NA, '20/09/2004', '01/10/2005', '20/02/2005'],
    })

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_446()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [3, 4]}


def test_validate_208():
    fake_data_prev = pd.DataFrame({
        'CHILD': ['101', '102', '103', '104',
                  '105', '106', '108', '109',
                  '110', '111', '33333', '44444',
                  '1000'],
        'UPN': ['UN5', 'X888888888888', 'UN1', 'UN1',
                pd.NA, 'UN4', 'UN1', pd.NA,
                'a------------', 'UN2', 'UN5', 'H000000000000',
                pd.NA],
    })
    fake_data = pd.DataFrame({
        'CHILD': ['101', '102', '103', '104',
                  '105', '106', '108', '109',
                  '110', '111', '55555', '66666',
                  '1000'],
        'UPN': ['H801200001001', 'O------------', 'UN1', 'UN2',
                pd.NA, 'UN3', pd.NA, 'UN4',
                'A------------', 'H801200001111', 'UN5', 'X999999999999',
                'UN1'],
    })

    fake_dfs = {'Header': fake_data, 'Header_last': fake_data_prev}

    error_defn, error_func = validate_208()

    result = error_func(fake_dfs)

    assert result == {'Header': [1, 5, 6, 12]}


def test_validate_204():
    fake_data = pd.DataFrame({
        'CHILD': ['101', '102', '103', '104', '105', '106', '108', '109', '110'],
        'ETHNIC': ['WBRI', 'WBRI', 'nobt', 'AINS', pd.NA, 'BOTH', pd.NA, 'BCRB', 'MWBC'],
    })

    fake_data_prev = pd.DataFrame({
        'CHILD': ['101', '102', '103', '104', '105', '107', '108', '109', '110'],
        'ETHNIC': ['WBRI', 'NOBT', 'NOBT', "AINS", pd.NA, 'REFU', 'MOTH', pd.NA, 'MWBA'],
    })

    fake_dfs = {'Header': fake_data, 'Header_last': fake_data_prev}

    error_defn, error_func = validate_204()

    result = error_func(fake_dfs)

    assert result == {'Header': [1, 6, 7, 8]}


def test_validate_203():
    fake_data = pd.DataFrame({
        'CHILD': ['101', '102', '103', '104', '105', '106', '108', '109', '110'],
        'DOB': ['16/03/2020', '23/09/2016', '31/12/19', '31/02/2018', pd.NA, '10/08/2014', pd.NA, '20/01/2017',
                '31/06/2020'],
    })

    fake_data_prev = pd.DataFrame({
        'CHILD': ['101', '102', '103', '104', '105', '107', '108', '109', '110'],
        'DOB': ['16/03/2020', '22/09/2016', '31/12/2019', "31/02/2018", pd.NA, '11/11/2021', '04/06/2017', pd.NA,
                '30/06/2020'],
    })

    fake_dfs = {'Header': fake_data, 'Header_last': fake_data_prev}

    error_defn, error_func = validate_203()

    result = error_func(fake_dfs)

    assert result == {'Header': [1, 2, 6, 7, 8]}


def test_validate_530():
    fake_data = pd.DataFrame({
        'PLACE': ['P1', 'A3', 'K1', 'P1', 'P1', 'P1'],
        'PLACE_PROVIDER': ['PR4', 'PR3', 'PR4', 'PR4', 'PR5', 'PRO']
    })

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_530()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [0, 3]}


def test_validate_571():
    fake_data = pd.DataFrame({
        'MIS_START': ['08/03/2020', '22/06/2020', pd.NA, '13/10/2021', '10/24/2021'],
        'MIS_END': ['08/03/2020', pd.NA, '22/06/2020', '13/10/21', pd.NA],
    })

    metadata = {
        'collection_start': '01/04/2020',
        'collection_end': '31/03/2020'
    }

    fake_dfs = {'Missing': fake_data, 'metadata': metadata}

    error_defn, error_func = validate_571()

    result = error_func(fake_dfs)

    assert result == {'Missing': [0, 2]}


def test_validate_1005():
    fake_data = pd.DataFrame({
        'MIS_START': ['08/03/2020', '22/06/2020', pd.NA, '13/10/2021', '10/24/2021'],
        'MIS_END': ['08/03/2020', pd.NA, '22/06/2020', '13/10/21', pd.NA],
    })

    fake_dfs = {'Missing': fake_data}

    error_defn, error_func = validate_1005()

    result = error_func(fake_dfs)

    assert result == {'Missing': [3]}


def test_validate_1004():
    fake_data = pd.DataFrame({
        'MIS_START': ['08/03/2020', '22/06/2020', pd.NA, '13/10/2021', '10/24/2021'],
        'MIS_END': ['08/03/2020', pd.NA, '22/06/2020', '13/10/21', pd.NA],
    })

    fake_dfs = {'Missing': fake_data}

    error_defn, error_func = validate_1004()

    result = error_func(fake_dfs)

    assert result == {'Missing': [2, 4]}


def test_validate_202():
    fake_data = pd.DataFrame({
        'CHILD': ['101', '102', '103', '104', '105', '106', '108', '109', '110'],
        'SEX': ['1', 2, '1', '2', pd.NA, '1', pd.NA, '2', '3'],
    })

    fake_data_prev = pd.DataFrame({
        'CHILD': ['101', '102', '103', '104', '105', '107', '108', '109', '110'],
        'SEX': ['1', 1, '2', 2, pd.NA, '1', '2', pd.NA, '2'],
    })

    fake_dfs = {'Header': fake_data, 'Header_last': fake_data_prev}

    error_defn, error_func = validate_202()

    result = error_func(fake_dfs)

    assert result == {'Header': [1, 2, 6, 7, 8]}


def test_validate_621():
    fake_data = pd.DataFrame({
        'DOB': ['01/12/2021', '19/02/2016', '31/01/2019', '31/01/2019', '31/01/2019'],
        'MC_DOB': ['01/01/2021', '19/12/2016', '31/01/2019', pd.NA, '01/02/2019'],
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
        'CHILD': ['101', '102', '103', '104', '105'],
        'SEX': ['2', '1', '2', '2', '2'],
        'MOTHER': ['1', pd.NA, '0', pd.NA, pd.NA],
    })

    fake_data_episodes = pd.DataFrame({
        'CHILD': ['101', '102', '103', '104', '105'],
        'LS': ['C2', 'C2', 'c2', 'C1', 'v4']
    })

    fake_dfs = {'Header': fake_data, 'Episodes': fake_data_episodes}

    error_defn, error_func = validate_393()

    result = error_func(fake_dfs)

    assert result == {'Header': [3]}


def test_validate_NoE():
    fake_data = pd.DataFrame({
        'CHILD': ['101', '102', '103'],
        'DECOM': ['14/03/2021', '08/09/2021', '03/10/2020'],
    })

    fake_data_prev = pd.DataFrame({
        'CHILD': ['101', '102'],
        'DECOM': ['14/03/2021', '16/06/2019']
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
        'DECOM': ['14/03/2021', '16/06/2019', '03/10/2020', '07/09/2021'],
        'DEC': ['08/12/2020', '24/08/2021', pd.NA, '07/09/2021'],
    })

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_356()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [0]}


def test_validate_611():
    fake_data = pd.DataFrame({
        'MOTHER': [1, '1', pd.NA, pd.NA, 1],
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
        'PLACE_PROVIDER': ['PR0', 'PR1', '', pd.NA, '', pd.NA],
        'PLACE': ['U1', 'T0', 'U2', 'Z1', 'T1', pd.NA],
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


def test_validate_392c():
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

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_392c()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [1, 2, 3]}


def test_validate_213():
    fake_data = pd.DataFrame({
        'PLACE': ['T0', 'U6', 'U1', 'U4', 'P1', 'T2', 'T3', pd.NA],
        'PLACE_PROVIDER': [pd.NA, pd.NA, 'PR3', 'PR4', 'PR0', 'PR2', 'PR1', pd.NA],
    })

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_213()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [5, 6]}


def test_validate_168():
    fake_data = pd.DataFrame({
        'UPN': ['UN3', 'E07295962325C1556', 'UN5', 'UN7', 'UPN3sDSG', 'X06805040829A', '5035247309594', pd.NA,
                'L086819786126', 'K06014812931', 'J000947841350156', 'M0940709', 'I072272729588',
                'N075491517151', 'Z041674136429', 'E043016488226', 'S074885779408'],
    })

    fake_dfs = {'Header': fake_data}

    error_defn, error_func = validate_168()

    result = error_func(fake_dfs)

    assert result == {'Header': [1, 3, 4, 6, 9, 10, 11, 12, 16]}


def test_validate_388():
    fake_data = pd.DataFrame([
        {'CHILD': '111', 'DECOM': '01/06/2020', 'DEC': '04/06/2020', 'REC': 'X1'},  # 0  Fails Case 1
        {'CHILD': '111', 'DECOM': '05/06/2020', 'DEC': '06/06/2020', 'REC': 'X1'},  # 1
        {'CHILD': '111', 'DECOM': '06/06/2020', 'DEC': '08/06/2020', 'REC': 'X1'},  # 2
        {'CHILD': '111', 'DECOM': '08/06/2020', 'DEC': '05/06/2020', 'REC': 'X1'},  # 3  Fails Case 3
        {'CHILD': '222', 'DECOM': '05/06/2020', 'DEC': '06/06/2020', 'REC': pd.NA},  # 4
        {'CHILD': '333', 'DECOM': '06/06/2020', 'DEC': '07/06/2020', 'REC': 'E11'},  # 5  Fails Case 2
        {'CHILD': '333', 'DECOM': '07/06/2020', 'DEC': pd.NA, 'REC': pd.NA},  # 6
        {'CHILD': '444', 'DECOM': '08/06/2020', 'DEC': '09/06/2020', 'REC': 'X1'},  # 7
        {'CHILD': '444', 'DECOM': '09/06/2020', 'DEC': '10/06/2020', 'REC': 'E11'},  # 8
        {'CHILD': '444', 'DECOM': '15/06/2020', 'DEC': pd.NA, 'REC': pd.NA},  # 9
        {'CHILD': '555', 'DECOM': '11/06/2020', 'DEC': '12/06/2020', 'REC': 'X1'},  # 10  Fails Case 3
        {'CHILD': '6666', 'DECOM': '12/06/2020', 'DEC': '13/06/2020', 'REC': 'X1'},  # 11
        {'CHILD': '6666', 'DECOM': '13/06/2020', 'DEC': '14/06/2020', 'REC': 'X1'},  # 12
        {'CHILD': '6666', 'DECOM': '14/06/2020', 'DEC': '15/06/2020', 'REC': 'X1'},  # 13
        {'CHILD': '6666', 'DECOM': '15/06/2020', 'DEC': '16/06/2020', 'REC': 'X1'},  # 14  Fails Case 3
        {'CHILD': '77777', 'DECOM': '16/06/2020', 'DEC': '17/06/2020', 'REC': 'X1'},  # 15
        {'CHILD': '77777', 'DECOM': '17/06/2020', 'DEC': '18/06/2020', 'REC': 'X1'},  # 16
        {'CHILD': '77777', 'DECOM': '18/06/2020', 'DEC': pd.NA, 'REC': pd.NA},  # 17
        {'CHILD': '999', 'DECOM': '31/06/2020', 'DEC': pd.NA, 'REC': pd.NA},  # 18   Nonsense date, but should pass
        {'CHILD': '123', 'DECOM': pd.NA, 'DEC': pd.NA, 'REC': pd.NA},  # 19   Nonsense dates, but should pass
        {'CHILD': pd.NA, 'DECOM': pd.NA, 'DEC': pd.NA, 'REC': pd.NA},  # 20   Nonsense, but should pass
    ])

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_388()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [0, 3, 5, 10, 14]}


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
        'IN_TOUCH': [pd.NA, 'XXX', pd.NA, pd.NA, pd.NA],
        'ACTIV': [pd.NA, pd.NA, 'XXX', pd.NA, pd.NA],
        'ACCOM': [pd.NA, pd.NA, pd.NA, 'XXX', pd.NA],
    })
    fake_data_ad1 = pd.DataFrame({
        'CHILD': ['A', 'B', 'C', 'D', 'E'],
        'DATE_INT': [pd.NA, pd.NA, 'XXX', pd.NA, 'XXX'],
        'DATE_MATCH': [pd.NA, 'XXX', 'XXX', pd.NA, 'XXX'],
        'FOSTER_CARE': [pd.NA, pd.NA, 'XXX', pd.NA, 'XXX'],
        'NB_ADOPTR': [pd.NA, pd.NA, 'XXX', pd.NA, 'XXX'],
        'SEX_ADOPTR': [pd.NA, pd.NA, 'XXX', pd.NA, 'XXX'],
        'LS_ADOPTR': [pd.NA, pd.NA, 'XXX', 'XXX', 'XXX'],
    })

    fake_dfs = {'OC3': fake_data_oc3, 'AD1': fake_data_ad1}

    error_defn, error_func = validate_134()

    result = error_func(fake_dfs)

    assert result == {'AD1': [1, 2, 3]}


def test_validate_119():
    fake_data = pd.DataFrame({
        'DATE_PLACED_CEASED': ['22/11/2015', '08/05/2010', pd.NA, pd.NA],
        'REASON_PLACED_CEASED': ['XXX', pd.NA, '10/05/2009', pd.NA]
    })

    fake_dfs = {'PlacedAdoption': fake_data}

    error_defn, error_func = validate_119()

    result = error_func(fake_dfs)

    assert result == {'PlacedAdoption': [1, 2]}


def test_validate_159():
    fake_data = pd.DataFrame({
        'SUBSTANCE_MISUSE': ['1', '1', '1', '1', 1,
                             '1', pd.NA, pd.NA, 1, 0],
        'INTERVENTION_RECEIVED': ['1', '0', '0', pd.NA, 0,
                                  '1', '1', pd.NA, 0, 1],
        'INTERVENTION_OFFERED': [pd.NA, '0', pd.NA, pd.NA, pd.NA,
                                 '1', pd.NA, pd.NA, 0, 1],
    })

    fake_dfs = {'OC2': fake_data}

    error_defn, error_func = validate_159()

    result = error_func(fake_dfs)

    assert result == {'OC2': [2, 4]}


def test_validate_142():
    fake_data = pd.DataFrame([
        {'CHILD': '111', 'DECOM': '01/06/2020', 'DEC': '04/06/2020', 'REC': 'X1'},  # 0
        {'CHILD': '111', 'DECOM': '05/06/2020', 'DEC': '06/06/2020', 'REC': pd.NA},  # 1  Fails
        {'CHILD': '111', 'DECOM': '06/06/2020', 'DEC': '08/06/2020', 'REC': 'X1'},  # 2
        {'CHILD': '111', 'DECOM': '08/06/2020', 'DEC': '05/06/2020', 'REC': 'X1'},  # 3
        {'CHILD': '222', 'DECOM': '05/06/2020', 'DEC': '06/06/2020', 'REC': pd.NA},  # 4
        {'CHILD': '333', 'DECOM': '06/06/2020', 'DEC': pd.NA, 'REC': 'E11'},  # 5   Fails
        {'CHILD': '333', 'DECOM': '07/06/2020', 'DEC': pd.NA, 'REC': pd.NA},  # 6
        {'CHILD': '444', 'DECOM': '08/06/2020', 'DEC': '09/06/2020', 'REC': 'X1'},  # 7
        {'CHILD': '444', 'DECOM': '09/06/2020', 'DEC': '10/06/2020', 'REC': 'E11'},  # 8
        {'CHILD': '444', 'DECOM': '15/06/2020', 'DEC': pd.NA, 'REC': pd.NA},  # 9
        {'CHILD': '555', 'DECOM': '11/06/2020', 'DEC': '12/06/2020', 'REC': 'X1'},  # 10
        {'CHILD': '6666', 'DECOM': '12/06/2020', 'DEC': '13/06/2020', 'REC': 'X1'},  # 11
        {'CHILD': '6666', 'DECOM': '13/06/2020', 'DEC': '14/06/2020', 'REC': 'X1'},  # 12
        {'CHILD': '6666', 'DECOM': '14/06/2020', 'DEC': pd.NA, 'REC': 'X1'},  # 13  Fails
        {'CHILD': '6666', 'DECOM': '15/06/2020', 'DEC': '16/06/2020', 'REC': 'X1'},  # 14
        {'CHILD': '77777', 'DECOM': '16/06/2020', 'DEC': '17/06/2020', 'REC': 'X1'},  # 15
        {'CHILD': '77777', 'DECOM': '17/06/2020', 'DEC': '18/06/2020', 'REC': 'X1'},  # 16
        {'CHILD': '77777', 'DECOM': '18/06/2020', 'DEC': pd.NA, 'REC': 'X1'},  # 17
        {'CHILD': '999', 'DECOM': '31/06/2020', 'DEC': pd.NA, 'REC': pd.NA},  # 18   Nonsense date, but should pass
        {'CHILD': '123', 'DECOM': pd.NA, 'DEC': pd.NA, 'REC': pd.NA},  # 19   Nonsense dates, but should pass
        {'CHILD': pd.NA, 'DECOM': pd.NA, 'DEC': pd.NA, 'REC': pd.NA},  # 20   Nonsense, but should pass
    ])

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_142()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [1, 5, 13]}


def test_validate_148():
    fake_data = pd.DataFrame([
        {'CHILD': '111', 'DECOM': '01/06/2020', 'DEC': '04/06/2020', 'REC': pd.NA},  # 0  Fails
        {'CHILD': '111', 'DECOM': '05/06/2020', 'DEC': '06/06/2020', 'REC': 'X1'},  # 1
        {'CHILD': '111', 'DECOM': '06/06/2020', 'DEC': pd.NA, 'REC': 'X1'},  # 2   Fails
        {'CHILD': '111', 'DECOM': '08/06/2020', 'DEC': '05/06/2020', 'REC': 'X1'},  # 3
        {'CHILD': '222', 'DECOM': '05/06/2020', 'DEC': '06/06/2020', 'REC': pd.NA},  # 4   Fails
        {'CHILD': '333', 'DECOM': '06/06/2020', 'DEC': '07/06/2020', 'REC': 'E11'},  # 5
        {'CHILD': '333', 'DECOM': '07/06/2020', 'DEC': pd.NA, 'REC': pd.NA},  # 6
        {'CHILD': '444', 'DECOM': '08/06/2020', 'DEC': '09/06/2020', 'REC': 'X1'},  # 7
        {'CHILD': '444', 'DECOM': '09/06/2020', 'DEC': '10/06/2020', 'REC': 'E11'},  # 8
        {'CHILD': '444', 'DECOM': '15/06/2020', 'DEC': pd.NA, 'REC': pd.NA},  # 9
    ])

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_148()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [0, 2, 4]}


def test_validate_214():
    fake_data = pd.DataFrame([
        {'LS': 'V3', 'PL_POST': 'M2 3RT', 'URN': 'XXXXXX'},  # 0  Fail
        {'LS': 'U1', 'PL_POST': 'M2 3RT', 'URN': 'SC045099'},  # 1
        {'LS': 'U3', 'PL_POST': pd.NA, 'URN': 'SC045099'},  # 2
        {'LS': 'V4', 'PL_POST': 'M2 3RT', 'URN': pd.NA},  # 3  Fail
        {'LS': 'V4', 'PL_POST': pd.NA, 'URN': 'SC045099'},  # 4  Fail
        {'LS': 'T1', 'PL_POST': 'M2 3RT', 'URN': 'SC045100'},  # 5
        {'LS': 'U6', 'PL_POST': 'M2 3RT', 'URN': 'SC045101'},  # 6
        {'LS': 'V3', 'PL_POST': pd.NA, 'URN': pd.NA},  # 7
    ])

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_214()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [0, 3, 4]}


def test_validate_222():
    fake_data = pd.DataFrame([
        {'PLACE': 'H5', 'URN': 'XXXXXXX'},  # 0
        {'PLACE': 'U1', 'URN': 'Whatever'},  # 1
        {'PLACE': 'U2', 'URN': pd.NA},  # 2
        {'PLACE': 'T1', 'URN': pd.NA},  # 3
        {'PLACE': 'R1', 'URN': 'Whatever'},  # 4  Fail
        {'PLACE': 'T2', 'URN': 'Whatever'},  # 5  Fail
    ])

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_222()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [4, 5]}


def test_validate_366():
    fake_data = pd.DataFrame([
        {'LS': 'V3', 'RNE': 'S'},  # 0
        {'LS': 'V4', 'RNE': 'T'},  # 1
        {'LS': 'U1', 'RNE': pd.NA},  # 2
        {'LS': 'U2', 'RNE': pd.NA},  # 3
        {'LS': 'V3', 'RNE': 'U'},  # 4  Fail
        {'LS': 'V3', 'RNE': pd.NA},  # 5  Fail
    ])

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_366()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [4, 5]}


def test_validate_628():
    fake_data_hea = pd.DataFrame({
        'CHILD': ['0', '1', '2', '3', '4', '5', '6'],
        'MOTHER': [1, pd.NA, 0, 1, 0, 1, 1],  # 1 will pass as null
    })
    fake_data_epi = pd.DataFrame({
        'CHILD': ['a', '1', '3', '3', '3', '4', '5'],  # So 0, 2 and 6 are the ones not in episodes
    })
    fake_data_oc3 = pd.DataFrame([
        {'CHILD': '0', 'IN_TOUCH': 'Whatever', 'ACTIV': pd.NA, 'ACCOM': 'Whatever'},
        {'CHILD': '2', 'IN_TOUCH': pd.NA, 'ACTIV': pd.NA, 'ACCOM': pd.NA},  # All null values so 2 will pass
        {'CHILD': '6', 'IN_TOUCH': 'Whatever', 'ACTIV': pd.NA, 'ACCOM': pd.NA},
        {'CHILD': '5', 'IN_TOUCH': 'Whatever', 'ACTIV': pd.NA, 'ACCOM': pd.NA},
    ])
    fake_dfs = {'Header': fake_data_hea, 'Episodes': fake_data_epi, 'OC3': fake_data_oc3}

    error_defn, error_func = validate_628()

    result = error_func(fake_dfs)

    assert result == {'Header': [0, 6]}


def test_validate_182():
    fake_data = pd.DataFrame({
        'IMMUNISATIONS': [pd.NA, pd.NA, pd.NA, '1', pd.NA, '1', pd.NA, '1'],
        'TEETH_CHECK': [pd.NA, pd.NA, pd.NA, '1', pd.NA, '1', '1', '1'],
        'HEALTH_ASSESSMENT': [pd.NA, pd.NA, pd.NA, '1', pd.NA, '1', pd.NA, '1'],
        'SUBSTANCE_MISUSE': [pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, '1', '1', '1'],
        'CONVICTED': [pd.NA, '1', pd.NA, pd.NA, pd.NA, '1', '1', pd.NA],
        'HEALTH_CHECK': [pd.NA, pd.NA, '1', pd.NA, pd.NA, '1', '1', pd.NA],
        'INTERVENTION_RECEIVED': [pd.NA, pd.NA, pd.NA, '1', pd.NA, '1', '1', pd.NA],
        'INTERVENTION_OFFERED': [pd.NA, pd.NA, pd.NA, pd.NA, '1', '1', '1', pd.NA],
    })

    fake_dfs = {'OC2': fake_data}

    error_defn, error_func = validate_182()

    result = error_func(fake_dfs)
    assert result == {'OC2': [1, 2, 3, 4, 6]}


def test_validate_151():
    fake_data = pd.DataFrame({
        'DATE_INT': [pd.NA, '01/01/2021', '01/01/2021', pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, '01/01/2021'],
        'DATE_MATCH': [pd.NA, '01/01/2021', pd.NA, '01/01/2021', pd.NA, pd.NA, pd.NA, pd.NA, pd.NA],
        'FOSTER_CARE': [pd.NA, '01/01/2021', pd.NA, pd.NA, '01/01/2021', pd.NA, pd.NA, pd.NA, '01/01/2021'],
        'NB_ADOPTR': [pd.NA, '01/01/2021', pd.NA, pd.NA, pd.NA, '01/01/2021', pd.NA, pd.NA, pd.NA],
        'SEX_ADOPTR': [pd.NA, '01/01/2021', pd.NA, pd.NA, pd.NA, pd.NA, '01/01/2021', pd.NA, '01/01/2021'],
        'LS_ADOPTR': [pd.NA, '01/01/2021', pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, '01/01/2021', pd.NA],
    })

    fake_dfs = {'AD1': fake_data}

    error_defn, error_func = validate_151()

    result = error_func(fake_dfs)
    assert result == {'AD1': [2, 3, 4, 5, 6, 7, 8]}

def test_validate_169():
    fake_data = pd.DataFrame({
        'LS': ['C2', 'C2', 'C2', 'V3', 'V4'],
        'PL_LA': ['NIR', 'E03934134', pd.NA, pd.NA, pd.NA, ]
    })

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_169()

    assert error_func(fake_dfs) == {'Episodes': [2]}


def test_validate_179():
    fake_data = pd.DataFrame({
        'LS': ['C2', 'C2', 'C2', 'V3', 'V4'],
        'PL_LOCATION': ['IN', 'OUT', pd.NA, pd.NA, pd.NA, ]
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
        'DECOM': ['01/01/2000', '01/02/2000', '01/03/2000', '01/04/2000', '01/05/2000', '01/06/2000', '04/05/2000'],
        'DEC': ['01/01/2000', '01/03/2000', pd.NA, '01/04/2000', '03/05/2000', '01/06/2000', '01/05/2000'],
    })

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_355()

    assert error_func(fake_dfs) == {'Episodes': [0, 3, 5]}


def test_validate_586():
    fake_data = pd.DataFrame([
        {'DOB': '01/02/2020', 'MIS_START': pd.NA},  # 0
        {'DOB': '02/02/2020', 'MIS_START': '07/02/2020'},  # 1
        {'DOB': '04/02/2020', 'MIS_START': '03/02/2020'},  # 2  Fails
        {'DOB': '06/02/2020', 'MIS_START': pd.NA},  # 3
        {'DOB': '07/02/2020', 'MIS_START': '01/02/2020'},  # 4  Fails
        {'DOB': '08/02/2020', 'MIS_START': '13/02/2020'},  # 5
    ])

    fake_dfs = {'Missing': fake_data}

    error_defn, error_func = validate_586()

    assert error_func(fake_dfs) == {'Missing': [2, 4]}


def test_validate_630():
    fake_epi = pd.DataFrame({
        'CHILD': ['0', '1', '2', '3', '4', '5', '6', '7', '8'],
        'DECOM': ['01/04/2021', '01/04/2021', '01/04/2021', '01/04/2021', '31/03/2021', '01/04/2021', '01/04/2021',
                  '01/04/2021', '01/04/2021'],
        # 4 will now pass, it's before this year
        'RNE': ['T', 'S', 'S', 'P', 'S', 'S', 'S', 'S', 'S'],
    })
    fake_pre = pd.DataFrame({
        'CHILD': ['2', '4', '5', '6', '7', '8'],
        'PREV_PERM': ['Z1', 'P1', 'P1', 'Z1', pd.NA, 'P1'],
        'LA_PERM': [pd.NA, '352', pd.NA, pd.NA, pd.NA, '352'],
        'DATE_PERM': [pd.NA, pd.NA, '01/05/2000', pd.NA, pd.NA, '05/05/2020'],
    })
    metadata = {'collection_start': '01/04/2021'}

    fake_dfs = {'Episodes': fake_epi, 'PrevPerm': fake_pre, 'metadata': metadata}

    error_defn, error_func = validate_630()

    assert error_func(fake_dfs) == {'Episodes': [1, 5, 7]}


def test_validate_501():
    fake_data = pd.DataFrame([
        {'CHILD': '111', 'DECOM': '01/06/2020', 'DEC': '04/06/2020'},  # 0
        {'CHILD': '111', 'DECOM': '02/06/2020', 'DEC': '06/06/2020'},  # 1   Fails
        {'CHILD': '111', 'DECOM': '06/06/2020', 'DEC': pd.NA},  # 2
        {'CHILD': '111', 'DECOM': '08/06/2020', 'DEC': '09/06/2020'},  # 3
        {'CHILD': '222', 'DECOM': '10/06/2020', 'DEC': '11/06/2020'},  # 4
        {'CHILD': '333', 'DECOM': '04/06/2020', 'DEC': '07/06/2020'},  # 5
        {'CHILD': '333', 'DECOM': '05/06/2020', 'DEC': pd.NA},  # 6   Fails
        {'CHILD': '444', 'DECOM': '08/06/2020', 'DEC': '09/06/2020'},  # 7
        {'CHILD': '444', 'DECOM': '08/06/2020', 'DEC': '10/06/2020'},  # 8   Fails
        {'CHILD': '444', 'DECOM': '15/06/2020', 'DEC': pd.NA},  # 9
    ])

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_501()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [1, 6, 8]}


def test_validate_502():
    fake_epi = pd.DataFrame([
        {'CHILD': '111', 'DECOM': '01/06/2020'},  # 0  Min   Fails
        {'CHILD': '111', 'DECOM': '05/06/2020'},  # 1
        {'CHILD': '111', 'DECOM': '06/06/2020'},  # 2
        {'CHILD': '123', 'DECOM': '08/06/2020'},  # 3  Min
        {'CHILD': '222', 'DECOM': '05/06/2020'},  # 4   Min   Fails
        {'CHILD': '333', 'DECOM': '06/06/2020'},  # 5  Min
        {'CHILD': '333', 'DECOM': '07/06/2020'},  # 6
        {'CHILD': '444', 'DECOM': '08/06/2020'},  # 7  Min   Fails
        {'CHILD': '444', 'DECOM': '09/06/2020'},  # 8
        {'CHILD': '444', 'DECOM': '15/06/2020'},  # 9
        {'CHILD': '555', 'DECOM': '15/06/2020'},  # 10
    ])

    fake_epi_last = pd.DataFrame([
        {'CHILD': '111', 'DECOM': '05/06/2020', 'DEC': pd.NA},
        {'CHILD': '123', 'DECOM': '08/06/2020', 'DEC': pd.NA},
        {'CHILD': '222', 'DECOM': '09/06/2020', 'DEC': pd.NA},
        {'CHILD': '333', 'DECOM': '06/06/2020', 'DEC': '05/06/2020'},
        {'CHILD': '333', 'DECOM': '07/06/2020', 'DEC': '05/06/2020'},
        {'CHILD': '444', 'DECOM': '08/06/2020', 'DEC': '05/06/2020'},
        {'CHILD': '444', 'DECOM': '09/06/2020', 'DEC': '05/06/2020'},
        {'CHILD': '444', 'DECOM': '19/06/2020', 'DEC': pd.NA},
    ])

    fake_dfs = {'Episodes': fake_epi, 'Episodes_last': fake_epi_last}

    error_defn, error_func = validate_502()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [0, 4, 7]}


def test_validate_153():
    fake_data = pd.DataFrame({
        'IN_TOUCH': ['XXX', pd.NA, 'XXX', pd.NA, pd.NA, 'XXX'],
        'ACTIV': ['XXX', pd.NA, pd.NA, 'XXX', pd.NA, 'XXX'],
        'ACCOM': ['XXX', pd.NA, pd.NA, pd.NA, 'XXX', pd.NA],
    })

    fake_dfs = {'OC3': fake_data}

    error_defn, error_func = validate_153()

    result = error_func(fake_dfs)

    assert result == {'OC3': [2, 3, 4, 5]}


def test_validate_166():
    fake_data = pd.DataFrame({
        'REVIEW': ['01/01/2021', '19/02/2010', '38/04/2019', '01/01/19', pd.NA],
    })

    fake_dfs = {'Reviews': fake_data}

    error_defn, error_func = validate_166()

    result = error_func(fake_dfs)

    assert result == {'Reviews': [2, 3, 4]}


def test_validate_174():
    fake_data = pd.DataFrame({
        'SEX': ['1', '1', '2', '2', 1, 1],
        'MC_DOB': [pd.NA, '19/02/2010', pd.NA, '19/02/2010', pd.NA, '19/02/2010'],
    })

    fake_dfs = {'Header': fake_data}

    error_defn, error_func = validate_174()

    result = error_func(fake_dfs)

    assert result == {'Header': [1, 5]}


def test_validate_180():
    fake_data = pd.DataFrame({
        'SDQ_SCORE': ['10', 41, '58', 72,
                      '0', 40, 39.5, 20.0,
                      pd.NA, 'XX'],
    })

    fake_dfs = {'OC2': fake_data}

    error_defn, error_func = validate_180()

    result = error_func(fake_dfs)

    assert result == {'OC2': [1, 2, 3, 6, 9]}


def test_validate_181():
    fake_data = pd.DataFrame({
        'CONVICTED': [1, pd.NA, pd.NA, '2', '2'],
        'HEALTH_CHECK': [1, pd.NA, pd.NA, 2, '2'],
        'IMMUNISATIONS': [1, pd.NA, pd.NA, pd.NA, '2'],
        'TEETH_CHECK': ['1', pd.NA, '0', pd.NA, '2'],
        'HEALTH_ASSESSMENT': ['1', pd.NA, 1, pd.NA, '2'],
        'SUBSTANCE_MISUSE': [0, pd.NA, 0, '1', '2'],
        'INTERVENTION_RECEIVED': [0, pd.NA, '1', 1, '2'],
        'INTERVENTION_OFFERED': ['1', pd.NA, pd.NA, 0, '2'],
    })

    fake_dfs = {'OC2': fake_data}

    error_defn, error_func = validate_181()

    result = error_func(fake_dfs)

    assert result == {'OC2': [3, 4]}


def test_validate_192():
    fake_data = pd.DataFrame({
        'SUBSTANCE_MISUSE': [0, pd.NA, 0, '1', 1, '1'],
        'INTERVENTION_RECEIVED': [0, pd.NA, '1', 1, pd.NA, pd.NA],
    })

    fake_dfs = {'OC2': fake_data}

    error_defn, error_func = validate_192()

    result = error_func(fake_dfs)

    assert result == {'OC2': [4, 5]}


def test_validate_193():
    fake_data = pd.DataFrame({
        'SUBSTANCE_MISUSE': [0, pd.NA, 0, '1', pd.NA, pd.NA, 0],
        'INTERVENTION_RECEIVED': [0, pd.NA, '1', 1, '1', pd.NA, pd.NA],
        'INTERVENTION_OFFERED': [0, pd.NA, '1', 1, pd.NA, 0, pd.NA],
    })

    fake_dfs = {'OC2': fake_data}

    error_defn, error_func = validate_193()

    result = error_func(fake_dfs)

    assert result == {'OC2': [0, 2, 4, 5]}


def test_validate_197a():
    fake_data = pd.DataFrame({
        'SDQ_SCORE': [0, pd.NA, 10, '1', pd.NA],
        'SDQ_REASON': ['XXX', pd.NA, pd.NA, 'XXX', 'XXX'],
    })

    fake_dfs = {'OC2': fake_data}

    error_defn, error_func = validate_197a()

    result = error_func(fake_dfs)

    assert result == {'OC2': [0, 3]}


def test_validate_567():
    fake_mis = pd.DataFrame([
        {'MIS_START': '01/06/2020', 'MIS_END': '05/06/2020'},  # 0
        {'MIS_START': '02/06/2020', 'MIS_END': pd.NA},  # 1
        {'MIS_START': '03/06/2020', 'MIS_END': '01/06/2020'},  # 2 Fails
        {'MIS_START': '04/06/2020', 'MIS_END': '02/06/2020'},  # 3 Fails
        {'MIS_START': pd.NA, 'MIS_END': '05/06/2020'},  # 4
    ])

    fake_dfs = {'Missing': fake_mis}

    error_defn, error_func = validate_567()

    result = error_func(fake_dfs)

    assert result == {'Missing': [2, 3]}


def test_validate_304():
    fake_uasc = pd.DataFrame([
        {'DOB': '01/06/2000', 'DUC': '05/06/2019'},  # 0 Fails
        {'DOB': '02/06/2000', 'DUC': pd.NA},  # 1
        {'DOB': '03/06/2000', 'DUC': '01/06/2015'},  # 2
        {'DOB': '04/06/2000', 'DUC': '02/06/2020'},  # 3 Fails
        {'DOB': pd.NA, 'DUC': '05/06/2020'},  # 4
    ])

    fake_dfs = {'UASC': fake_uasc}

    error_defn, error_func = validate_304()

    result = error_func(fake_dfs)

    assert result == {'UASC': [0, 3]}


def test_validate_333():
    fake_adt = pd.DataFrame([
        {'DATE_INT': '01/06/2020', 'DATE_MATCH': '05/06/2020'},  # 0
        {'DATE_INT': '02/06/2020', 'DATE_MATCH': pd.NA},  # 1
        {'DATE_INT': '03/06/2020', 'DATE_MATCH': '01/06/2020'},  # 2  Fails
        {'DATE_INT': '04/06/2020', 'DATE_MATCH': '02/06/2020'},  # 3  Fails
        {'DATE_INT': pd.NA, 'DATE_MATCH': '05/06/2020'},  # 4  Fails
    ])

    fake_dfs = {'AD1': fake_adt}

    error_defn, error_func = validate_333()

    result = error_func(fake_dfs)

    assert result == {'AD1': [2, 3, 4]}


def test_validate_1011():
    fake_data_epi = pd.DataFrame([
        {'CHILD': '111', 'DECOM': '01/06/2020', 'REC': 'E3'},  # 0
        {'CHILD': '111', 'DECOM': '05/06/2020', 'REC': 'E11'},  # 1
        {'CHILD': '111', 'DECOM': '06/06/2020', 'REC': 'E3'},  # 2  Max E3
        {'CHILD': '123', 'DECOM': '08/06/2020', 'REC': 'X1'},  # 3
        {'CHILD': '222', 'DECOM': '05/06/2020', 'REC': 'E3'},  # 4   Max E3
        {'CHILD': '333', 'DECOM': '06/06/2020', 'REC': 'X1'},  # 5
        {'CHILD': '333', 'DECOM': '07/06/2020', 'REC': 'E3'},  # 6  Max E3
        {'CHILD': '444', 'DECOM': '08/06/2020', 'REC': 'E3'},  # 7
        {'CHILD': '444', 'DECOM': '09/06/2020', 'REC': 'E3'},  # 8
        {'CHILD': '444', 'DECOM': '15/06/2020', 'REC': 'X1'},  # 9
        {'CHILD': '555', 'DECOM': '15/06/2020', 'REC': 'E3'},  # 10  Max E3
        {'CHILD': '666', 'DECOM': '15/06/2020', 'REC': pd.NA},  # 11
    ])
    fake_data_oc3 = pd.DataFrame([
        {'CHILD': '111', 'IN_TOUCH': 'Whatever', 'ACTIV': pd.NA, 'ACCOM': 'Whatever'},  # 0 Fails
        {'CHILD': '222', 'IN_TOUCH': pd.NA, 'ACTIV': pd.NA, 'ACCOM': pd.NA},  # 1 All null values so will pass
        {'CHILD': '333', 'IN_TOUCH': 'Whatever', 'ACTIV': pd.NA, 'ACCOM': pd.NA},  # 2 Fails
        {'CHILD': '777', 'IN_TOUCH': 'Whatever', 'ACTIV': pd.NA, 'ACCOM': pd.NA},  # 3
        {'CHILD': '555', 'IN_TOUCH': 'Whatever', 'ACTIV': pd.NA, 'ACCOM': pd.NA},  # 4 Fails
    ])
    fake_dfs = {'OC3': fake_data_oc3, 'Episodes': fake_data_epi}

    error_defn, error_func = validate_1011()

    result = error_func(fake_dfs)

    assert result == {'OC3': [0, 2, 4]}


def test_validate_574():
    fake_mis = pd.DataFrame([
        {'CHILD': '111', 'MIS_START': '01/06/2020', 'MIS_END': '05/06/2020'},  # 0
        {'CHILD': '111', 'MIS_START': '04/06/2020', 'MIS_END': pd.NA},  # 1 Fails overlaps
        {'CHILD': '222', 'MIS_START': '03/06/2020', 'MIS_END': '04/06/2020'},  # 2
        {'CHILD': '222', 'MIS_START': '04/06/2020', 'MIS_END': pd.NA},  # 3
        {'CHILD': '222', 'MIS_START': '07/06/2020', 'MIS_END': '09/06/2020'},  # 4 Fails, previous end is null
        {'CHILD': '333', 'MIS_START': '02/06/2020', 'MIS_END': '04/06/2020'},  # 5
        {'CHILD': '333', 'MIS_START': '03/06/2020', 'MIS_END': '09/06/2020'},  # 6 Fails overlaps
        {'CHILD': '555', 'MIS_START': pd.NA, 'MIS_END': '05/06/2020'},  # 7
        {'CHILD': '555', 'MIS_START': pd.NA, 'MIS_END': '05/06/2020'},  # 8
    ])

    fake_dfs = {'Missing': fake_mis}

    error_defn, error_func = validate_574()

    result = error_func(fake_dfs)

    assert result == {'Missing': [1, 4, 6]}


def test_validate_564():
    fake_data = pd.DataFrame([
        {'MISSING': 'M', 'MIS_START': pd.NA},  # 0  Fails
        {'MISSING': 'A', 'MIS_START': '07/02/2020'},  # 1
        {'MISSING': 'A', 'MIS_START': '03/02/2020'},  # 2
        {'MISSING': pd.NA, 'MIS_START': pd.NA},  # 3
        {'MISSING': 'M', 'MIS_START': pd.NA},  # 4  Fails
        {'MISSING': 'A', 'MIS_START': '13/02/2020'},  # 5
    ])

    fake_dfs = {'Missing': fake_data}

    error_defn, error_func = validate_564()

    assert error_func(fake_dfs) == {'Missing': [0, 4]}


def test_validate_566():
    fake_data = pd.DataFrame([
        {'MISSING': 'M', 'MIS_END': pd.NA},  # 0
        {'MISSING': pd.NA, 'MIS_END': '07/02/2020'},  # 1  Fails
        {'MISSING': 'A', 'MIS_END': '03/02/2020'},  # 2
        {'MISSING': pd.NA, 'MIS_END': pd.NA},  # 3
        {'MISSING': 'M', 'MIS_END': '01/02/2020'},  # 4
        {'MISSING': pd.NA, 'MIS_END': '13/02/2020'},  # 5  Fails
    ])

    fake_dfs = {'Missing': fake_data}

    error_defn, error_func = validate_566()

    assert error_func(fake_dfs) == {'Missing': [1, 5]}


def test_validate_570():
    fake_data = pd.DataFrame({
        'MIS_START': ['08/04/2020', '22/06/2020', pd.NA, '13/10/2005', '10/05/2001'],
    })

    metadata = {'collection_end': '31/03/2020'}

    fake_dfs = {'Missing': fake_data, 'metadata': metadata}

    error_defn, error_func = validate_570()

    result = error_func(fake_dfs)

    assert result == {'Missing': [0, 1]}


def test_validate_531():
    fake_data = pd.DataFrame({
        'PLACE': ['P1', 'A3', 'K1', 'P1', 'P1', 'P1'],
        'PLACE_PROVIDER': ['PR5', 'PR3', 'PR4', 'PR4', 'PR5', 'PRO']
    })

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_531()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [0, 4]}


def test_validate_542():
    fake_data = pd.DataFrame({
        'DOB': ['08/03/2020', '22/06/2000', pd.NA, '13/10/2000', '10/01/2017'],
        'CONVICTED': [1, pd.NA, 1, 1, 1],  # 0 , 4
    })

    metadata = {'collection_end': '31/03/2020'}

    fake_dfs = {'OC2': fake_data, 'metadata': metadata}

    error_defn, error_func = validate_542()

    result = error_func(fake_dfs)

    assert result == {'OC2': [0, 4]}


def test_validate_620():
    fake_hea = pd.DataFrame([
        {'MOTHER': '1', 'DOB': pd.NA},  # 0
        {'MOTHER': '1', 'DOB': '07/02/2020'},  # 1  Fails
        {'MOTHER': '1', 'DOB': '03/02/2020'},  # 2  Fails
        {'MOTHER': pd.NA, 'DOB': pd.NA},  # 3
        {'MOTHER': '1', 'DOB': '18/01/1981'},  # 4  Passes old DOB
        {'MOTHER': '0', 'DOB': '13/02/2020'},  # 5
    ])

    metadata = {'collection_start': '01/04/2020'}

    fake_dfs = {'Header': fake_hea, 'metadata': metadata}

    error_defn, error_func = validate_620()

    result = error_func(fake_dfs)

    assert result == {'Header': [1, 2]}


def test_validate_431():
    fake_data = pd.DataFrame([
        {'CHILD': '111', 'RNE': 'S', 'DECOM': '01/06/2020', 'DEC': '04/06/2020'},  # 0
        {'CHILD': '111', 'RNE': 'S', 'DECOM': '05/06/2020', 'DEC': '06/06/2020'},  # 1
        {'CHILD': '111', 'RNE': 'T', 'DECOM': '06/06/2020', 'DEC': '08/06/2020'},  # 2
        {'CHILD': '111', 'RNE': 'S', 'DECOM': '08/06/2020', 'DEC': '05/06/2020'},  # 3  Fails
        {'CHILD': '222', 'RNE': 'S', 'DECOM': '05/06/2020', 'DEC': '06/06/2020'},  # 4
        {'CHILD': '333', 'RNE': 'S', 'DECOM': '06/06/2020', 'DEC': '07/06/2020'},  # 5
        {'CHILD': '333', 'RNE': 'S', 'DECOM': '10/06/2020', 'DEC': pd.NA},  # 6
        {'CHILD': '444', 'RNE': 'S', 'DECOM': '08/06/2020', 'DEC': '09/06/2020'},  # 7
        {'CHILD': '444', 'RNE': 'S', 'DECOM': '09/06/2020', 'DEC': '10/06/2020'},  # 8  Fails
        {'CHILD': '444', 'RNE': 'S', 'DECOM': '15/06/2020', 'DEC': pd.NA},  # 9
        {'CHILD': '555', 'RNE': 'S', 'DECOM': '11/06/2020', 'DEC': '12/06/2020'},  # 10
        {'CHILD': '6666', 'RNE': 'S', 'DECOM': '12/06/2020', 'DEC': '13/06/2020'},  # 11
        {'CHILD': '6666', 'RNE': 'S', 'DECOM': '13/06/2020', 'DEC': '14/06/2020'},  # 12 Fails
        {'CHILD': '6666', 'RNE': 'S', 'DECOM': '14/06/2020', 'DEC': '15/06/2020'},  # 13 Fails
    ])

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_431()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [3, 8, 12, 13]}


def test_validate_225():
    fake_data_epi = pd.DataFrame([
        {'CHILD': '111', 'DECOM': '01/06/2020', 'RNE': 'P', 'REC': 'X1', 'PLACE': 'U1',
         'REASON_PLACE_CHANGE': pd.NA},  # 0 Fails
        {'CHILD': '111', 'DECOM': '05/06/2020', 'RNE': 'P', 'REC': 'E11', 'PLACE': 'X1',
         'REASON_PLACE_CHANGE': pd.NA},  # 1
        {'CHILD': '111', 'DECOM': '06/06/2020', 'RNE': 'B', 'REC': 'E3', 'PLACE': 'X1',
         'REASON_PLACE_CHANGE': pd.NA},  # 2
        {'CHILD': '123', 'DECOM': '08/06/2020', 'RNE': 'P', 'REC': 'X1', 'PLACE': 'U1',
         'REASON_PLACE_CHANGE': pd.NA},  # 3 Fails
        {'CHILD': '123', 'DECOM': '10/06/2020', 'RNE': 'P', 'REC': 'E3', 'PLACE': 'X1',
         'REASON_PLACE_CHANGE': pd.NA},  # 4
        {'CHILD': '333', 'DECOM': '06/06/2020', 'RNE': 'T', 'REC': 'X1', 'PLACE': 'U1',
         'REASON_PLACE_CHANGE': pd.NA},  # 5
        {'CHILD': '333', 'DECOM': '07/06/2020', 'RNE': 'L', 'REC': 'X1', 'PLACE': 'X1',
         'REASON_PLACE_CHANGE': 'CHANGE'},  # 6 Passes as RPC not null
        {'CHILD': '333', 'DECOM': '08/06/2020', 'RNE': 'P', 'REC': 'E3', 'PLACE': 'U1',
         'REASON_PLACE_CHANGE': pd.NA},  # 7
        {'CHILD': '444', 'DECOM': '09/06/2020', 'RNE': 'U', 'REC': 'X1', 'PLACE': 'T1',
         'REASON_PLACE_CHANGE': pd.NA},  # 8
        {'CHILD': '444', 'DECOM': '15/06/2020', 'RNE': 'P', 'REC': 'X1', 'PLACE': 'X1',
         'REASON_PLACE_CHANGE': pd.NA},  # 9 Passes next place T3
        {'CHILD': '444', 'DECOM': '16/06/2020', 'RNE': 'P', 'REC': 'E3', 'PLACE': 'T3',
         'REASON_PLACE_CHANGE': pd.NA},  # 10
        {'CHILD': '666', 'DECOM': '17/06/2020', 'RNE': 'P', 'REC': pd.NA, 'PLACE': 'T4',
         'REASON_PLACE_CHANGE': pd.NA},  # 11
    ])

    fake_dfs = {'Episodes': fake_data_epi}

    error_defn, error_func = validate_225()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [0, 3]}


def test_validate_353():
    fake_data = pd.DataFrame([
        {'DECOM': pd.NA},  # 0
        {'DECOM': '02/06/1980'},  # 1   Fails
        {'DECOM': '06/06/1890'},  # 2   Fails
        {'DECOM': '08/06/2020'},  # 3
    ])

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_353()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [1, 2]}


def test_validate_528():
    fake_data = pd.DataFrame({
        'PLACE': ['P1', 'A3', 'K1', 'P1', 'P1', 'R2'],
        'PLACE_PROVIDER': ['PR2', 'PR3', 'PR2', 'PR4', 'PR5', 'PR2']
    })

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_528()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [0, 5]}


def test_validate_527():
    fake_data = pd.DataFrame({
        'PLACE': ['P1', 'A3', 'K1', 'R2', 'P1', 'X1'],
        'PLACE_PROVIDER': ['PR1', 'PR3', 'PR4', 'PR1', 'PR1', 'PR1']
    })

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_527()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [0, 3, 4]}


def test_validate_359():
    fake_hea = pd.DataFrame([
        {'CHILD': '111', 'DOB': '01/06/2020'},
        {'CHILD': '222', 'DOB': '05/06/2000'},
        {'CHILD': '333', 'DOB': '05/06/2000'},
        {'CHILD': '444', 'DOB': '06/06/2000'},
        {'CHILD': '555', 'DOB': '06/06/2019'},
    ])

    fake_epi = pd.DataFrame([
        {'CHILD': '111', 'DEC': '01/06/2020', 'LS': 'R1', 'PLACE': 'R2'},  # 0 DOB 01/06/2020
        {'CHILD': '222', 'DEC': pd.NA, 'LS': 'V2', 'PLACE': 'K2'},
        # 1 DOB 05/06/2000 Passes older than 18, but has V2 K2
        {'CHILD': '333', 'DEC': pd.NA, 'LS': 'V2', 'PLACE': 'K1'},  # 2 DOB 05/06/2000 Fails
        {'CHILD': '444', 'DEC': pd.NA, 'LS': 'R1', 'PLACE': 'R2'},  # 3 DOB 06/06/2000 Fails
        {'CHILD': '555', 'DEC': pd.NA, 'LS': 'R1', 'PLACE': 'R2'},  # 4 DOB 06/06/2019 Passes, Too young
    ])

    metadata = {'collection_end': '31/03/2021'}

    fake_dfs = {'Header': fake_hea, 'Episodes': fake_epi, 'metadata': metadata}

    error_defn, error_func = validate_359()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [2, 3]}


def test_validate_562():
    fake_epi = pd.DataFrame([
        {'CHILD': '111', 'DECOM': '15/03/2021'},  # 0 Min pre year start
        {'CHILD': '111', 'DECOM': '05/06/2021'},  # 1
        {'CHILD': '222', 'DECOM': '13/03/2021'},  # 2 Min pre year start
        {'CHILD': '222', 'DECOM': '08/06/2021'},  # 3
        {'CHILD': '222', 'DECOM': '05/06/2021'},  # 4
        {'CHILD': '333', 'DECOM': '01/01/2021'},  # 5 Min pre year start
        {'CHILD': '444', 'DECOM': '01/05/2021'},  # 6
    ])
    fake_last = pd.DataFrame([
        {'CHILD': '111', 'DECOM': '01/06/2020'},  # 0
        {'CHILD': '111', 'DECOM': '05/06/2020'},  # 1
        {'CHILD': '111', 'DECOM': '15/03/2021'},  # 2 Max matches next year
        {'CHILD': '222', 'DECOM': '01/02/2021'},  # 3
        {'CHILD': '222', 'DECOM': '11/03/2021'},  # 4 Max doesn't match - fail
        {'CHILD': '333', 'DECOM': '06/06/2020'},  # 5 Max doesn't match - fail
    ])
    metadata = {'collection_start': '01/04/2021'}

    fake_dfs = {'Episodes': fake_epi, 'Episodes_last': fake_last, 'metadata': metadata}

    error_defn, error_func = validate_562()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [2, 5]}


def test_validate_354():
    fake_data = pd.DataFrame({'DECOM': ['01/01/2021', '19/02/2010', '38/04/2019', '01/01/2022',
                                        '01/04/2021', '01/05/2021', pd.NA, '3rd Dec 1873'], })

    metadata = {'collection_end': '01/04/2021'}

    fake_dfs = {'Episodes': fake_data, 'metadata': metadata}

    error_defn, error_func = validate_354()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [3, 5]}


def test_validate_385():
    fake_data = pd.DataFrame({
        'DEC': ['14/03/2021', '08/09/2021', '03/10/2020', '04/04/2021', pd.NA, 'Tuesday 33st'],
    })

    metadata = {
        'collection_end': '01/04/2021'
    }

    fake_dfs = {'Episodes': fake_data, 'metadata': metadata}

    error_defn, error_func = validate_385()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [1, 3]}


def test_validate_408():
    fake_data = pd.DataFrame([
        {'PLACE': 'A5', 'LS': 'S'},  # 0   Fail
        {'PLACE': 'V4', 'LS': 'T'},  # 1
        {'PLACE': 'A6', 'LS': 'E1'},  # 2
        {'PLACE': 'U2', 'LS': pd.NA},  # 3
        {'PLACE': 'A6', 'LS': 'U'},  # 4  Fail
        {'PLACE': 'A5', 'LS': pd.NA},  # 5  Fail
    ])

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_408()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [0, 4, 5]}


def test_validate_380():
    fake_data = pd.DataFrame({
        'RNE': ['S', 'L', 'P', 'B', 'P', pd.NA],
        'PLACE': ['U1', 'T0', 'U2', 'Z1', 'T1', pd.NA],
    })

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_380()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [1]}


def test_validate_381():
    fake_data = pd.DataFrame({
        'REC': ['X1', 'PR1', 'X1', pd.NA, 'X1', pd.NA],
        'PLACE': ['T3', 'T0', 'U2', 'T2', 'T1', pd.NA],
    })

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_381()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [1]}


def test_validate_504():
    fake_data = pd.DataFrame([
        {'CHILD': '111', 'DECOM': '01/06/2020', 'DEC': '04/06/2020', 'REC': 'X1', 'CIN': 'N1'},  # 0
        {'CHILD': '111', 'DECOM': '04/06/2020', 'DEC': '06/06/2020', 'REC': 'X1', 'CIN': 'N2'},  # 1   Fails
        {'CHILD': '111', 'DECOM': '06/06/2020', 'DEC': pd.NA, 'REC': 'X1', 'CIN': 'N3'},  # 2   Fails
        {'CHILD': '111', 'DECOM': '08/06/2020', 'DEC': '09/06/2020', 'REC': 'X1', 'CIN': 'N2'},  # 3
        {'CHILD': '222', 'DECOM': '10/06/2020', 'DEC': '11/06/2020', 'REC': 'X1', 'CIN': 'N3'},  # 4
        {'CHILD': '333', 'DECOM': '04/06/2020', 'DEC': '07/06/2020', 'REC': 'X1', 'CIN': 'N4'},  # 5
        {'CHILD': '333', 'DECOM': '07/06/2020', 'DEC': pd.NA, 'REC': 'X1', 'CIN': 'N1'},  # 6   Fails
        {'CHILD': '444', 'DECOM': '08/06/2020', 'DEC': '09/06/2020', 'REC': 'X1', 'CIN': 'N2'},  # 7
        {'CHILD': '444', 'DECOM': '08/06/2020', 'DEC': '10/06/2020', 'REC': 'X1', 'CIN': 'N3'},  # 8
        {'CHILD': '444', 'DECOM': '10/06/2020', 'DEC': pd.NA, 'REC': 'X1', 'CIN': 'N4'},  # 9   Fails
    ])

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_504()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [1, 2, 6, 9]}


def test_validate_503A():
    fake_epi = pd.DataFrame([
        {'CHILD': '111', 'DECOM': '01/06/2020', 'RNE': 'L'},  # 0  Min, Fails
        {'CHILD': '111', 'DECOM': '05/06/2020', 'RNE': 'L'},  # 1
        {'CHILD': '111', 'DECOM': '06/06/2020', 'RNE': 'L'},  # 2
        {'CHILD': '123', 'DECOM': '08/06/2020', 'RNE': 'L'},  # 3  Min, Fails
        {'CHILD': '222', 'DECOM': '05/06/2020', 'RNE': 'L'},  # 4  Min
        {'CHILD': '333', 'DECOM': '06/06/2020', 'RNE': 'L'},  # 5  Min, Fails
        {'CHILD': '333', 'DECOM': '07/06/2020', 'RNE': 'L'},  # 6
        {'CHILD': '444', 'DECOM': '08/06/2020', 'RNE': 'L'},  # 7  Min

    ])

    fake_epi_last = pd.DataFrame([
        {'CHILD': '111', 'DECOM': '01/06/2020', 'RNE': 'S'},  # Max Different RNE
        {'CHILD': '123', 'DECOM': '08/06/2020', 'RNE': 'P'},  # Max Different RNE
        {'CHILD': '222', 'DECOM': '05/06/2020', 'RNE': 'L'},  # Max Same
        {'CHILD': '333', 'DECOM': '06/06/2020', 'RNE': 'R'},  # Max Different RNE
        {'CHILD': '444', 'DECOM': '08/06/2020', 'RNE': 'L'},
        {'CHILD': '444', 'DECOM': '09/06/2020', 'RNE': 'L'},
        {'CHILD': '444', 'DECOM': '19/06/2020', 'RNE': 'L'},  # Max different date so passes
    ])

    fake_dfs = {'Episodes': fake_epi, 'Episodes_last': fake_epi_last}

    error_defn, error_func = validate_503A()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [0, 3, 5]}


def test_validate_503B():
    fake_epi = pd.DataFrame([
        {'CHILD': '111', 'DECOM': '01/06/2020', 'LS': 'L'},  # 0  Min
        {'CHILD': '111', 'DECOM': '05/06/2020', 'LS': 'L'},  # 1
        {'CHILD': '111', 'DECOM': '06/06/2020', 'LS': 'L'},  # 2
        {'CHILD': '123', 'DECOM': '08/06/2020', 'LS': 'L'},  # 3  Min, Fails
        {'CHILD': '222', 'DECOM': '05/06/2020', 'LS': 'L'},  # 4  Min
        {'CHILD': '333', 'DECOM': '06/06/2020', 'LS': 'L'},  # 5  Min, Fails
        {'CHILD': '333', 'DECOM': '07/06/2020', 'LS': 'L'},  # 6
        {'CHILD': '444', 'DECOM': '08/06/2020', 'LS': 'L'},  # 7  Min

    ])

    fake_epi_last = pd.DataFrame([
        {'CHILD': '111', 'DECOM': '01/06/2020', 'LS': 'L'},  # Max
        {'CHILD': '123', 'DECOM': '08/06/2020', 'LS': 'E1'},  # Max
        {'CHILD': '222', 'DECOM': '05/06/2020', 'LS': 'L'},  # Max
        {'CHILD': '333', 'DECOM': '06/06/2020', 'LS': 'R'},  # Max
        {'CHILD': '444', 'DECOM': '08/06/2020', 'LS': 'L'},
        {'CHILD': '444', 'DECOM': '09/06/2020', 'LS': 'L'},
        {'CHILD': '444', 'DECOM': '19/06/2020', 'LS': 'L'},  # Max
    ])

    fake_dfs = {'Episodes': fake_epi, 'Episodes_last': fake_epi_last}

    error_defn, error_func = validate_503B()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [3, 5]}


def test_validate_503C():
    fake_epi = pd.DataFrame([
        {'CHILD': '111', 'DECOM': '01/06/2020', 'CIN': 'N1'},  # 0  Fails
        {'CHILD': '111', 'DECOM': '05/06/2020', 'CIN': 'N2'},  # 1
        {'CHILD': '111', 'DECOM': '06/06/2020', 'CIN': 'N3'},  # 2
        {'CHILD': '123', 'DECOM': '08/06/2020', 'CIN': 'N4'},  # 3
        {'CHILD': '222', 'DECOM': '05/06/2020', 'CIN': 'N5'},  # 4  Fails
        {'CHILD': '333', 'DECOM': '06/06/2020', 'CIN': 'N6'},  # 5  Fails
        {'CHILD': '333', 'DECOM': '07/06/2020', 'CIN': 'N7'},  # 6
        {'CHILD': '444', 'DECOM': '08/06/2020', 'CIN': 'N3'},  # 7

    ])

    fake_epi_last = pd.DataFrame([
        {'CHILD': '111', 'DECOM': '01/06/2020', 'CIN': pd.NA},  # Max
        {'CHILD': '123', 'DECOM': '08/06/2020', 'CIN': 'N4'},  # Max
        {'CHILD': '222', 'DECOM': '05/06/2020', 'CIN': 'L'},  # Max
        {'CHILD': '333', 'DECOM': '06/06/2020', 'CIN': pd.NA},  # Max
        {'CHILD': '444', 'DECOM': '08/06/2020', 'CIN': 'L'},
        {'CHILD': '444', 'DECOM': '09/06/2020', 'CIN': 'L'},
        {'CHILD': '444', 'DECOM': '19/06/2020', 'CIN': 'L'},  # Max
    ])

    fake_dfs = {'Episodes': fake_epi, 'Episodes_last': fake_epi_last}

    error_defn, error_func = validate_503C()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [0, 4, 5]}


def test_validate_503D():
    fake_epi = pd.DataFrame([
        {'CHILD': '111', 'DECOM': '01/06/2020', 'PLACE': 'T1'},  # 0  Fails
        {'CHILD': '111', 'DECOM': '05/06/2020', 'PLACE': 'T2'},  # 1
        {'CHILD': '111', 'DECOM': '06/06/2020', 'PLACE': 'T3'},  # 2
        {'CHILD': '123', 'DECOM': '08/06/2020', 'PLACE': 'T4'},  # 3  Fails
        {'CHILD': '222', 'DECOM': '05/06/2020', 'PLACE': 'T5'},  # 4  Fails
        {'CHILD': '333', 'DECOM': '06/06/2020', 'PLACE': 'T6'},  # 5  Fails
        {'CHILD': '333', 'DECOM': '07/06/2020', 'PLACE': 'T7'},  # 6
        {'CHILD': '444', 'DECOM': '08/06/2020', 'PLACE': 'T3'},  # 7

    ])

    fake_epi_last = pd.DataFrame([
        {'CHILD': '111', 'DECOM': '01/06/2020', 'PLACE': pd.NA},  # Max
        {'CHILD': '123', 'DECOM': '08/06/2020', 'PLACE': 'N4'},  # Max
        {'CHILD': '222', 'DECOM': '05/06/2020', 'PLACE': 'L'},  # Max
        {'CHILD': '333', 'DECOM': '06/06/2020', 'PLACE': pd.NA},  # Max
        {'CHILD': '444', 'DECOM': '08/06/2020', 'PLACE': 'L'},
        {'CHILD': '444', 'DECOM': '09/06/2020', 'PLACE': 'L'},
        {'CHILD': '444', 'DECOM': '19/06/2020', 'PLACE': 'L'},  # Max
    ])

    fake_dfs = {'Episodes': fake_epi, 'Episodes_last': fake_epi_last}

    error_defn, error_func = validate_503D()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [0, 3, 4, 5]}


def test_validate_503E():
    fake_epi = pd.DataFrame([
        {'CHILD': '111', 'DECOM': '01/06/2020', 'PLACE_PROVIDER': 'PR1'},  # 0  Fails
        {'CHILD': '111', 'DECOM': '05/06/2020', 'PLACE_PROVIDER': 'PR2'},  # 1
        {'CHILD': '111', 'DECOM': '06/06/2020', 'PLACE_PROVIDER': 'PR3'},  # 2
        {'CHILD': '123', 'DECOM': '08/06/2020', 'PLACE_PROVIDER': 'PR4'},  # 3
        {'CHILD': '222', 'DECOM': '05/06/2020', 'PLACE_PROVIDER': 'PR5'},  # 4  Fails
        {'CHILD': '333', 'DECOM': '06/06/2020', 'PLACE_PROVIDER': 'PR0'},  # 5  Fails
        {'CHILD': '333', 'DECOM': '07/06/2020', 'PLACE_PROVIDER': 'PR1'},  # 6
        {'CHILD': '444', 'DECOM': '08/06/2020', 'PLACE_PROVIDER': 'PR3'},  # 7

    ])

    fake_epi_last = pd.DataFrame([
        {'CHILD': '111', 'DECOM': '01/06/2020', 'PLACE_PROVIDER': pd.NA},  # Max
        {'CHILD': '123', 'DECOM': '08/06/2020', 'PLACE_PROVIDER': 'PR4'},  # Max
        {'CHILD': '222', 'DECOM': '05/06/2020', 'PLACE_PROVIDER': 'PR2'},  # Max
        {'CHILD': '333', 'DECOM': '06/06/2020', 'PLACE_PROVIDER': pd.NA},  # Max
        {'CHILD': '444', 'DECOM': '08/06/2020', 'PLACE_PROVIDER': 'PR1'},
        {'CHILD': '444', 'DECOM': '09/06/2020', 'PLACE_PROVIDER': 'PR0'},
        {'CHILD': '444', 'DECOM': '19/06/2020', 'PLACE_PROVIDER': 'PR2'},  # Max
    ])

    fake_dfs = {'Episodes': fake_epi, 'Episodes_last': fake_epi_last}

    error_defn, error_func = validate_503E()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [0, 4, 5]}


def test_validate_503F():
    fake_epi = pd.DataFrame([
        {'CHILD': '111', 'DECOM': '01/06/2020', 'URN': 'SC055123'},  # 0  Fails
        {'CHILD': '111', 'DECOM': '05/06/2020', 'URN': 'SC055123'},  # 1
        {'CHILD': '111', 'DECOM': '06/06/2020', 'URN': 'SC055123'},  # 2
        {'CHILD': '123', 'DECOM': '08/06/2020', 'URN': 'SC055123'},  # 3
        {'CHILD': '222', 'DECOM': '05/06/2020', 'URN': 'SC055123'},  # 4
        {'CHILD': '333', 'DECOM': '06/06/2020', 'URN': 'SC055123'},  # 5  Fails
        {'CHILD': '333', 'DECOM': '07/06/2020', 'URN': 'SC055123'},  # 6
        {'CHILD': '444', 'DECOM': '08/06/2020', 'URN': 'SC055123'},  # 7

    ])

    fake_epi_last = pd.DataFrame([
        {'CHILD': '111', 'DECOM': '01/06/2020', 'URN': pd.NA},  # Max
        {'CHILD': '123', 'DECOM': '08/06/2020', 'URN': 'SC055123'},  # Max
        {'CHILD': '222', 'DECOM': '05/06/2020', 'URN': 'SC055123'},  # Max
        {'CHILD': '333', 'DECOM': '06/06/2020', 'URN': pd.NA},  # Max
        {'CHILD': '444', 'DECOM': '08/06/2020', 'URN': 'SC055123'},
        {'CHILD': '444', 'DECOM': '09/06/2020', 'URN': 'SC055123'},
        {'CHILD': '444', 'DECOM': '19/06/2020', 'URN': 'SC055123'},  # Max
    ])

    fake_dfs = {'Episodes': fake_epi, 'Episodes_last': fake_epi_last}

    error_defn, error_func = validate_503F()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [0, 5]}


def test_validate_503J():
    fake_epi = pd.DataFrame([
        {'CHILD': '111', 'DECOM': '01/06/2020', 'PL_LOCATION': 'IN'},  # 0  Fails
        {'CHILD': '111', 'DECOM': '05/06/2020', 'PL_LOCATION': 'IN'},  # 1
        {'CHILD': '111', 'DECOM': '06/06/2020', 'PL_LOCATION': 'IN'},  # 2
        {'CHILD': '123', 'DECOM': '08/06/2020', 'PL_LOCATION': 'OUT'},  # 3
        {'CHILD': '222', 'DECOM': '05/06/2020', 'PL_LOCATION': 'IN'},  # 4  Fails
        {'CHILD': '333', 'DECOM': '06/06/2020', 'PL_LOCATION': 'OUT'},  # 5  Fails
        {'CHILD': '333', 'DECOM': '07/06/2020', 'PL_LOCATION': 'IN'},  # 6
        {'CHILD': '444', 'DECOM': '08/06/2020', 'PL_LOCATION': 'OUT'},  # 7

    ])

    fake_epi_last = pd.DataFrame([
        {'CHILD': '111', 'DECOM': '01/06/2020', 'PL_LOCATION': pd.NA},  # Max
        {'CHILD': '123', 'DECOM': '08/06/2020', 'PL_LOCATION': 'OUT'},  # Max
        {'CHILD': '222', 'DECOM': '05/06/2020', 'PL_LOCATION': 'OUT'},  # Max
        {'CHILD': '333', 'DECOM': '06/06/2020', 'PL_LOCATION': pd.NA},  # Max
        {'CHILD': '444', 'DECOM': '08/06/2020', 'PL_LOCATION': 'IN'},
        {'CHILD': '444', 'DECOM': '09/06/2020', 'PL_LOCATION': 'OUT'},
        {'CHILD': '444', 'DECOM': '19/06/2020', 'PL_LOCATION': 'OUT'},  # Max
    ])

    fake_dfs = {'Episodes': fake_epi, 'Episodes_last': fake_epi_last}

    error_defn, error_func = validate_503J()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [0, 4, 5]}


def test_validate_370():
    fake_epi = pd.DataFrame({
        'CHILD': ['111', '222', '333', '444', '555', '666'],
        'DECOM': ['01/01/2020', '01/02/2020', '02/03/2020', '15/01/1980', '15/03/2015', '14/03/2015'],
        'PLACE': ['E1', 'P2', 'P2', 'P2', 'P2', 'P2'],  # 15bd    #day before 15bd
        'DEC': ['13/02/2020', '14/03/2020', '14/04/2020', '27/04/2010', '26/04/2004', '25/04/2014'],
    })
    fake_hea = pd.DataFrame({
        'CHILD': ['111', '222', '333', '444', '555', '666'],
        'DOB': ['01/01/1998', '01/02/2000', '02/03/2015', '15/01/2010', '15/03/2000', '15/03/2000'],
    })
    fake_dfs = {'Episodes': fake_epi, 'Header': fake_hea}

    error_defn, error_func = validate_370()

    assert error_func(fake_dfs) == {'Episodes': [2, 3, 5]}


def test_validate_371():
    fake_epi = pd.DataFrame({
        'CHILD': ['111', '222', '333', '444', '555', '666'],
        'DECOM': ['01/01/2020', '01/02/2020', '02/03/2020', '15/01/1980', '15/03/2014', '14/03/2014'],
        'PLACE': ['H5', 'P2', 'P2', 'H5', 'H5', 'H5'],  # 14bd    #day before 14bd
        'DEC': ['13/02/2020', '14/03/2020', '14/04/2020', '27/04/2010', '26/04/2004', '25/04/2014'],
    })
    fake_hea = pd.DataFrame({
        'CHILD': ['111', '222', '333', '444', '555', '666'],
        'DOB': ['01/01/1998', '01/02/2000', '02/03/2015', '15/01/2010', '15/03/2000', '15/03/2000'],
    })
    fake_dfs = {'Episodes': fake_epi, 'Header': fake_hea}

    error_defn, error_func = validate_371()

    assert error_func(fake_dfs) == {'Episodes': [3, 5]}


def test_validate_372():
    fake_epi = pd.DataFrame({
        'CHILD': ['111', '222', '333', '444', '555', '666'],
        'DECOM': ['01/01/2020', '01/02/2020', '02/03/2020', '15/03/2010', '15/01/1980', '14/03/2010'],
        'PLACE': ['R5', 'R5', 'P2', 'R5', 'R5', 'R5'],  # day before 10bd
        'DEC': ['13/02/2020', '14/03/2020', '14/04/2020', '27/04/2010', '26/04/2004', '25/04/2014'],
    })
    fake_hea = pd.DataFrame({
        'CHILD': ['111', '222', '333', '444', '555', '666'],
        'DOB': ['01/01/1998', '01/02/2000', '02/03/2015', '15/01/2010', '15/03/2000', '15/03/2000'],
    })
    fake_dfs = {'Episodes': fake_epi, 'Header': fake_hea}

    error_defn, error_func = validate_372()

    assert error_func(fake_dfs) == {'Episodes': [3, 4, 5]}


def test_validate_373():
    fake_epi = pd.DataFrame({
        'CHILD': ['111', '222', '333', '444', '555', '666'],
        'DECOM': ['01/01/2020', '01/02/2020', '02/03/2020', '15/03/2010', '15/03/2004', '14/03/2004'],
        'PLACE': ['S1', 'S1', 'P2', 'S1', 'S1', 'S1'],  # day before 4bd
        'DEC': ['13/02/2020', '14/03/2020', '14/04/2020', '27/04/2010', '26/04/2004', '25/04/2014'],

    })
    fake_hea = pd.DataFrame({
        'CHILD': ['111', '222', '333', '444', '555', '666'],
        'DOB': ['01/01/1998', '01/02/2000', '02/03/2015', '15/01/2010', '15/03/2000', '15/03/2000'],
    })
    fake_dfs = {'Episodes': fake_epi, 'Header': fake_hea}

    error_defn, error_func = validate_373()

    assert error_func(fake_dfs) == {'Episodes': [3, 5]}


def test_validate_374():
    fake_epi = pd.DataFrame({
        'CHILD': ['111', '222', '333', '444', '555', '666', '777'],
        'DECOM': ['01/01/2020', '01/02/2020', '02/03/2020', '15/03/2010', pd.NA, '15/03/2004', '14/03/2014'],
        'PLACE': ['P3', 'P3', 'P3', 'P3', 'P3', 'P3', 'P3'],  # day before 14bd
        'DEC': ['13/02/2020', '14/03/2020', '14/04/2020', pd.NA, '27/04/2010', '26/04/2004', '25/04/2014'],
    })
    fake_hea = pd.DataFrame({
        'CHILD': ['111', '222', '333', '444', '555', '666', '777'],
        'DOB': ['01/01/1998', '01/02/2000', '02/03/2015', '15/01/2010', '15/03/2000', '15/03/2000', '15/03/2000'],
    })
    fake_dfs = {'Episodes': fake_epi, 'Header': fake_hea}

    error_defn, error_func = validate_374()

    assert error_func(fake_dfs) == {'Episodes': [2, 5, 6]}


def test_validate_375():
    fake_epi = pd.DataFrame({
        'CHILD': ['111', '222', '333', '444', '555', '666'],
        'DECOM': ['01/01/2020', '01/02/2020', '02/03/2020', '15/03/2010', '15/03/2004', '14/03/2014'],
        'DEC': ['13/02/2020', '14/03/2020', '14/04/2020', '27/04/2010', '26/04/2004', '25/04/2014'],
        'PLACE': ['T1', 'T1', 'T1', 'T1', 'T1', 'P2'],
    })
    fake_hea = pd.DataFrame({
        'CHILD': ['111', '222', '333', '444', '555', '666'],
        'DOB': ['01/01/1998', '01/02/2000', '02/03/2015', '15/01/2010', '15/03/2000', '15/03/2000'],
    })
    fake_dfs = {'Episodes': fake_epi, 'Header': fake_hea}

    error_defn, error_func = validate_375()

    assert error_func(fake_dfs) == {'Episodes': [0, 2, 3]}


def test_validate_376():
    fake_epi = pd.DataFrame({
        'CHILD': ['111', '222', '333', '444', '555', '666', '777'],
        'DECOM': ['01/01/2020', '01/02/2020', '02/03/2020', '15/03/2010', '15/03/2004', '14/03/2014', pd.NA],
        'DEC': ['22/01/2020', '23/02/2020', '24/03/2020', '06/04/2010', '05/04/2004', '04/04/2014', pd.NA],
        'PLACE': ['T3', 'T3', 'T3', 'T3', 'T3', 'P2', 'T3'],
    })
    fake_hea = pd.DataFrame({
        'CHILD': ['111', '222', '333', '444', '555', '666'],
        'DOB': ['01/01/1998', '01/02/2000', '02/03/2015', '15/01/2010', '15/03/2000', '15/03/2000'],
    })
    fake_dfs = {'Episodes': fake_epi, 'Header': fake_hea}

    error_defn, error_func = validate_376()

    assert error_func(fake_dfs) == {'Episodes': [1, 2, 3]}


def test_validate_379():
    fake_epi = pd.DataFrame({
        'CHILD': ['111', '222', '333', '444', '555', '666'],
        'DECOM': ['01/01/2020', '01/02/2020', '02/03/2020', '15/03/2010', '15/03/2004', '14/03/2014'],
        'DEC': ['08/01/2020', '09/02/2020', '09/03/2020', '25/03/2010', '22/03/2004', '25/03/2014'],
        'PLACE': ['T4', 'T4', 'T4', 'T4', 'T4', 'P2'],
    })
    fake_hea = pd.DataFrame({
        'CHILD': ['111', '222', '333', '444', '555', '666'],
        'DOB': ['08/01/2020', '08/02/2020', '09/03/2020', '22/03/2010', '22/03/2004', '21/03/2014'],
    })
    fake_dfs = {'Episodes': fake_epi, 'Header': fake_hea}

    error_defn, error_func = validate_379()

    assert error_func(fake_dfs) == {'Episodes': [1, 3]}


def test_validate_526():
    fake_data = pd.DataFrame({
        'PLACE': ['E1', 'P0', 'T1', 'T3', 'P1', 'Z1', 'P0'],
        'PLACE_PROVIDER': ['PR1', 'PR2', pd.NA, 'PR0', pd.NA, pd.NA, pd.NA],
    })

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_526()

    assert error_func(fake_dfs) == {'Episodes': [4, 6]}


def test_validate_550():
    fake_data = pd.DataFrame({
        'PLACE': ['P1', 'P0', 'T1', 'T3', 'T1', 'P1', 'P0'],
        'PLACE_PROVIDER': ['PR0', 'PR2', 'PR4', 'PR0', pd.NA, 'PR0', 'PR0'],
    })

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_550()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [3, 6]}


def test_validate_529():
    fake_data = pd.DataFrame({
        'PLACE_PROVIDER': ['PR0', 'PR1', 'PR3', 'PR3', pd.NA, 'PR3'],
        'PLACE': ['U1', 'U2', 'U3', 'T1', pd.NA, 'A3'],
    })

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_529()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [2, 5]}


def test_validate_383():
    fake_data = pd.DataFrame([
        {'CHILD': '111', 'RNE': 'S', 'DECOM': '01/06/2020', 'PLACE': 'S1'},  # 0
        {'CHILD': '111', 'RNE': 'S', 'DECOM': '05/06/2020', 'PLACE': 'T1'},  # 1 Middle Fails as next RNE not P
        {'CHILD': '111', 'RNE': 'T', 'DECOM': '06/06/2020', 'PLACE': 'S1'},  # 2
        {'CHILD': '222', 'RNE': 'S', 'DECOM': '05/06/2020', 'PLACE': 'T1'},  # 3
        {'CHILD': '333', 'RNE': 'S', 'DECOM': '06/06/2020', 'PLACE': 'S1'},  # 4
        {'CHILD': '333', 'RNE': 'S', 'DECOM': '10/06/2020', 'PLACE': 'T1'},  # 5 Middle Fails as pre PL not next PL
        {'CHILD': '333', 'RNE': 'P', 'DECOM': '12/06/2020', 'PLACE': 'S2'},  # 6
        {'CHILD': '444', 'RNE': 'S', 'DECOM': '08/06/2020', 'PLACE': 'T1'},  # 7
        {'CHILD': '444', 'RNE': 'S', 'DECOM': '09/06/2020', 'PLACE': 'P4'},  # 8  Middle Passes not a T code
        {'CHILD': '444', 'RNE': 'S', 'DECOM': '15/06/2020', 'PLACE': 'T1'},  # 9
        {'CHILD': '6666', 'RNE': 'S', 'DECOM': '12/06/2020', 'PLACE': 'T1'},  # 10
        {'CHILD': '6666', 'RNE': 'S', 'DECOM': '13/06/2020', 'PLACE': 'T1'},  # 11 Middle Passes
        {'CHILD': '6666', 'RNE': 'P', 'DECOM': '14/06/2020', 'PLACE': 'T1'},  # 12
    ])

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_383()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [1, 5]}


def test_validate_377():
    fake_data = pd.DataFrame([
        {'CHILD': '111', 'RNE': 'P', 'DECOM': '01/06/2020', 'PLACE': 'T3'},  # 0 ^
        {'CHILD': '111', 'RNE': 'P', 'DECOM': '05/06/2020', 'PLACE': 'P3'},  # 1
        {'CHILD': '111', 'RNE': 'T', 'DECOM': '06/06/2020', 'PLACE': 'T3'},  # 2
        {'CHILD': '111', 'RNE': 'B', 'DECOM': '08/06/2020', 'PLACE': 'T3'},  # 3 v
        {'CHILD': '222', 'RNE': 'B', 'DECOM': '05/06/2020', 'PLACE': 'T3'},  # 4 -
        {'CHILD': '333', 'RNE': 'B', 'DECOM': '06/06/2020', 'PLACE': 'T3'},  # 5 ^
        {'CHILD': '333', 'RNE': 'U', 'DECOM': '10/06/2020', 'PLACE': 'T3'},  # 6 v
        {'CHILD': '444', 'RNE': 'B', 'DECOM': '07/06/2020', 'PLACE': 'T3'},  # 7 ^
        {'CHILD': '444', 'RNE': 'B', 'DECOM': '08/06/2020', 'PLACE': 'oo'},  # 8
        {'CHILD': '444', 'RNE': 'T', 'DECOM': '09/06/2020', 'PLACE': 'T3'},  # 9
        {'CHILD': '444', 'RNE': 'B', 'DECOM': '15/06/2020', 'PLACE': 'T3'},  # 10 v
        {'CHILD': '6666', 'RNE': 'P', 'DECOM': '11/06/2020', 'PLACE': 'oo'},  # 11 ^
        {'CHILD': '6666', 'RNE': 'P', 'DECOM': '12/06/2020', 'PLACE': 'T3'},  # 12
        {'CHILD': '6666', 'RNE': 'P', 'DECOM': '13/06/2020', 'PLACE': 'T3'},  # 13
        {'CHILD': '6666', 'RNE': 'P', 'DECOM': '14/06/2020', 'PLACE': 'T3'},  # 14 v
    ])

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_377()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [0, 2, 3, 7, 9, 10, 12, 13, 14]}


def test_validate_303():
    fake_data_uasc = pd.DataFrame({
        'CHILD': [0, 1, 2, 3, 4, 5, ],
        'DUC': [pd.NA, '04/04/2021', '01/06/2020', pd.NA, '10/04/2020', '01/03/2021']
    })
    fake_data_header = pd.DataFrame({
        'CHILD': [0, 1, 2, 3, 4, 5, ],
        'UASC': [0, 1, 0, '1', '0', 1]
    })

    fake_dfs = {'UASC': fake_data_uasc, 'Header': fake_data_header}

    error_defn, error_func = validate_303()

    result = error_func(fake_dfs)

    assert result == {'UASC': [2, 4], 'Header': [2, 4]}


def test_validate_576():
    fake_mis_l = pd.DataFrame([
        {'CHILD': '111', 'MIS_START': '07/02/2020', 'MIS_END': '07/02/2020'},  # 0
        {'CHILD': '222', 'MIS_START': '07/02/2020', 'MIS_END': pd.NA},  # 1
        {'CHILD': '333', 'MIS_START': '03/02/2020', 'MIS_END': '07/02/2020'},  # 2
        {'CHILD': '444', 'MIS_START': '07/02/2020', 'MIS_END': pd.NA},  # 3
        {'CHILD': '555', 'MIS_START': '01/02/2020', 'MIS_END': pd.NA},  # 4
        {'CHILD': '666', 'MIS_START': '13/02/2020', 'MIS_END': '07/02/2020'},  # 5
    ])
    fake_mis = pd.DataFrame([
        {'CHILD': '111', 'MIS_START': '07/02/2020'},  # 0
        {'CHILD': '222', 'MIS_START': '08/02/2020'},  # 1 Fails
        {'CHILD': '333', 'MIS_START': '03/02/2020'},  # 2
        {'CHILD': '444', 'MIS_START': pd.NA},  # 3 Fails
        {'CHILD': '555', 'MIS_START': '01/02/2020'},  # 4
        {'CHILD': '666', 'MIS_START': '13/02/2020'},  # 5
    ])
    fake_dfs = {'Missing_last': fake_mis_l, 'Missing': fake_mis}

    error_defn, error_func = validate_576()

    assert error_func(fake_dfs) == {'Missing': [1, 3]}


def test_validate_553():
    fake_epi = pd.DataFrame([
        {'CHILD': '111', 'LS': 'E1', 'DEC': '01/06/2020', 'PLACE': 'T3'},  # 0
        {'CHILD': '222', 'LS': 'E1', 'DEC': '05/06/2020', 'PLACE': 'P3'},  # 1
        {'CHILD': '333', 'LS': 'T1', 'DEC': '06/06/2020', 'PLACE': 'T3'},  # 2
        {'CHILD': '444', 'LS': 'E1', 'DEC': pd.NA, 'PLACE': 'T3'},  # 3 Err not in sho
        {'CHILD': '555', 'LS': 'E1', 'DEC': pd.NA, 'PLACE': 'T3'},  # 3 Err not in sho
        {'CHILD': '777', 'LS': 'E1', 'DEC': pd.NA, 'PLACE': 'T3'},  # 4
    ])
    fake_sho = pd.DataFrame([
        {'CHILD': '111', 'DATE_PLACED': '01/06/2020', 'DATE_PLACED_CEASED': '01/06/2020',  # 0
         'REASON_PLACED_CEASED': 'A'},
        {'CHILD': '222', 'DATE_PLACED': '01/06/2020', 'DATE_PLACED_CEASED': '01/06/2020',  # 1
         'REASON_PLACED_CEASED': pd.NA},
        {'CHILD': '333', 'DATE_PLACED': '01/06/2020', 'DATE_PLACED_CEASED': '01/06/2020',  # 2
         'REASON_PLACED_CEASED': 'A'},
        {'CHILD': '123', 'DATE_PLACED': '01/06/2020', 'DATE_PLACED_CEASED': '01/06/2020',  # 3
         'REASON_PLACED_CEASED': 'A'},
        {'CHILD': '555', 'DATE_PLACED': '01/06/2020', 'DATE_PLACED_CEASED': pd.NA,  # 4 err ceased null
         'REASON_PLACED_CEASED': 'A'},
        {'CHILD': '777', 'DATE_PLACED': pd.NA, 'DATE_PLACED_CEASED': '01/06/2020',  # 5 err ceased null
         'REASON_PLACED_CEASED': pd.NA},
    ])
    fake_dfs = {'Episodes': fake_epi, 'PlacedAdoption': fake_sho}

    error_defn, error_func = validate_553()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [3], 'PlacedAdoption': [4, 5]}


def test_validate_555():
    fake_epi = pd.DataFrame([
        {'CHILD': '111', 'LS': 'E1', 'DEC': '01/06/2020', 'PLACE': 'T3'},  # 0
        {'CHILD': '222', 'LS': 'D1', 'DEC': '05/06/2020', 'PLACE': 'P3'},  # 1
        {'CHILD': '333', 'LS': 'D1', 'DEC': '06/06/2020', 'PLACE': 'T3'},  # 2
        {'CHILD': '444', 'LS': 'D1', 'DEC': pd.NA, 'PLACE': 'T3'},  # 3 Err not in sho
        {'CHILD': '555', 'LS': 'D1', 'DEC': pd.NA, 'PLACE': 'T3'},  # 4 Err not in sho
        {'CHILD': '666', 'LS': 'D1', 'DEC': pd.NA, 'PLACE': 'T3'},  # 5
    ])
    fake_sho = pd.DataFrame([
        {'CHILD': '111', 'DATE_PLACED': '01/06/2020', 'DATE_PLACED_CEASED': '01/06/2020',  # 0
         'REASON_PLACED_CEASED': 'A'},
        {'CHILD': '222', 'DATE_PLACED': '01/06/2020', 'DATE_PLACED_CEASED': '01/06/2020',  # 1
         'REASON_PLACED_CEASED': 'A'},
        {'CHILD': '333', 'DATE_PLACED': '01/06/2020', 'DATE_PLACED_CEASED': '01/06/2020',  # 2
         'REASON_PLACED_CEASED': 'A'},
        {'CHILD': '666', 'DATE_PLACED': '01/06/2020', 'DATE_PLACED_CEASED': pd.NA,  # 3 err ceased not null
         'REASON_PLACED_CEASED': 'A'},
        {'CHILD': '123', 'DATE_PLACED': '01/06/2020', 'DATE_PLACED_CEASED': '01/06/2020',  # 4
         'REASON_PLACED_CEASED': 'A'},
        {'CHILD': '984', 'DATE_PLACED': pd.NA, 'DATE_PLACED_CEASED': '01/06/2020',  # 5
         'REASON_PLACED_CEASED': 'A'},
    ])
    fake_dfs = {'Episodes': fake_epi, 'PlacedAdoption': fake_sho}

    error_defn, error_func = validate_555()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [3, 4], 'PlacedAdoption': [3]}


def test_validate_382():
    fake_data = pd.DataFrame([
        {'PLACE': 'T0', 'LS': 'V3'},  # 0
        {'PLACE': 'R4', 'LS': 'V3'},  # 1
        {'PLACE': 'T1', 'LS': 'X3'},  # 2
        {'PLACE': 'T2', 'LS': 'V4'},  # 3
        {'PLACE': 'T3', 'LS': 'V4'},  # 4
    ])

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_382()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [0, 3, 4]}


def test_validate_602():
    fake_epi = pd.DataFrame({
        'CHILD': ['111', '222', '333', '444', '555', '666', '888'],
        'DEC': ['08/06/2020', '09/07/2020', '09/08/2020', '25/03/2021', '22/03/2020', '25/04/2021', pd.NA],
        'REC': ['E11', 'oo', 'T4', 'E11', 'oo', pd.NA, 'E11'],
    })
    fake_ad1 = pd.DataFrame({
        'CHILD': ['111', '123', '222', '333', '345', '444', '555', '666', '777'],
        'DATE_INT': [pd.NA, 'xx', pd.NA, pd.NA, 'xx', 'oo', pd.NA, 'xx', 'xx']
    })

    other_than_DATE_INT = ['DATE_MATCH', 'FOSTER_CARE', 'NB_ADOPTR', 'SEX_ADOPTR', 'LS_ADOPTR']

    for c in other_than_DATE_INT:
        fake_ad1[c] = pd.NA

    metadata = {'collection_start': '01/04/2020', 'collection_end': '31/03/2021'}

    fake_dfs = {'Episodes': fake_epi, 'AD1': fake_ad1, 'metadata': metadata}

    error_defn, error_func = validate_602()

    assert error_func(fake_dfs) == {'AD1': [1, 4, 7, 8]}


def test_validate_580():
    fake_epi = pd.DataFrame([
        {'CHILD': '111', 'DEC': '01/06/2020', 'REC': 'E7'},  # 0 fails
        {'CHILD': '123', 'DEC': '08/06/2020', 'REC': 'E7'},  # 1 fails
        {'CHILD': '222', 'DEC': '05/06/2020', 'REC': 'E8'},  # 2
        {'CHILD': '333', 'DEC': '06/06/2020', 'REC': 'E5'},  # 3 fails
        {'CHILD': '444', 'DEC': '07/06/2020', 'REC': 'E8'},  # 4
        {'CHILD': '555', 'DEC': '19/06/2020', 'REC': 'E4'},  # 5 fails
        {'CHILD': '777', 'DEC': '19/06/2020', 'REC': 'E4'},  # 6 fails
    ])

    fake_mis = pd.DataFrame([
        {'CHILD': '111', 'MISSING': 'M', 'MIS_END': '01/06/2020', 'DOB': '01/06/2002'},  #
        {'CHILD': '123', 'MISSING': 'M', 'MIS_END': '08/06/2020', 'DOB': '08/06/2002'},  #
        {'CHILD': '222', 'MISSING': 'M', 'MIS_END': '05/06/2020', 'DOB': '05/06/2002'},  #
        {'CHILD': '333', 'MISSING': 'M', 'MIS_END': '06/06/2020', 'DOB': '06/06/2002'},  #
        {'CHILD': '444', 'MISSING': 'M', 'MIS_END': '08/06/2020', 'DOB': '08/06/2002'},  #
        {'CHILD': '444', 'MISSING': 'M', 'MIS_END': '09/06/2020', 'DOB': '09/06/2002'},  #
        {'CHILD': '555', 'MISSING': 'M', 'MIS_END': '19/06/2020', 'DOB': '19/06/2002'},  #
        {'CHILD': '777', 'MISSING': 'A', 'MIS_END': '19/06/2020', 'DOB': '19/06/2002'},  #
    ])

    fake_dfs = {'Episodes': fake_epi, 'Missing': fake_mis}

    error_defn, error_func = validate_580()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [0, 1, 3, 5, 6]}


def test_validate_575():
    fake_epi = pd.DataFrame([
        {'CHILD': '111', 'DECOM': '01/06/2020', 'DEC': '10/06/2020'},  # 0
        {'CHILD': '123', 'DECOM': '08/06/2020', 'DEC': '10/06/2020'},  # 1
        {'CHILD': '222', 'DECOM': '05/06/2020', 'DEC': '10/06/2020'},  # 2
        {'CHILD': '333', 'DECOM': '06/06/2020', 'DEC': pd.NA},  # 3
        {'CHILD': '333', 'DECOM': '07/06/2020', 'DEC': '10/06/2020'},  # 4
        {'CHILD': '444', 'DECOM': '08/06/2020', 'DEC': '10/06/2020'},  # 5
        {'CHILD': '444', 'DECOM': '08/06/2020', 'DEC': pd.NA},  # 6

    ])

    fake_mis = pd.DataFrame([
        {'CHILD': '111', 'MIS_START': '01/06/2020', 'MIS_END': '05/06/2020'},  # 0
        {'CHILD': '123', 'MIS_START': '08/06/2020', 'MIS_END': pd.NA},  # 1 Fail
        {'CHILD': '222', 'MIS_START': '05/06/2020', 'MIS_END': '05/06/2020'},  # 2
        {'CHILD': '333', 'MIS_START': '06/06/2020', 'MIS_END': pd.NA},  # 3
        {'CHILD': '444', 'MIS_START': '08/06/2020', 'MIS_END': '05/06/2020'},  # 4
        {'CHILD': '444', 'MIS_START': '09/06/2020', 'MIS_END': pd.NA},  # 5 Fail
        {'CHILD': '444', 'MIS_START': '19/06/2020', 'MIS_END': '05/06/2020'},  # 6
    ])

    fake_dfs = {'Episodes': fake_epi, 'Missing': fake_mis}

    error_defn, error_func = validate_575()

    result = error_func(fake_dfs)

    assert result == {'Missing': [1, 5]}


def test_validate_1012():
    fake_epi = pd.DataFrame({'CHILD': ['111', '222', '333', '444', '555', '555', '666', '666'], })
    fake_ado = pd.DataFrame({'CHILD': ['777', '222', '333', '444', '555', '666'], })  # err at 0
    fake_mis = pd.DataFrame({'CHILD': ['111', '888', '333', '444', '555', '666'], })  # err at 1
    fake_rev = pd.DataFrame({'CHILD': ['111', '222', '999', '444', '555', '666'], })  # err at 2
    fake_ad1 = pd.DataFrame({'CHILD': ['111', '222', '333', '1010', '555', '666'], })  # err at 3
    fake_pre = pd.DataFrame({'CHILD': ['111', '222', '333', '444', '1111', '666'], })  # err at 4
    fake_oc2 = pd.DataFrame({'CHILD': ['111', '222', '333', '444', '555', '1212'], })  # err at 5

    fake_dfs = {'Episodes': fake_epi, 'PlacedAdoption': fake_ado, 'Missing': fake_mis, 'Reviews': fake_rev,
                'AD1': fake_ad1, 'PrevPerm': fake_pre, 'OC2': fake_oc2}

    fake_dfs_partial = {'Episodes': fake_epi,
                        'AD1': fake_ad1, 'PrevPerm': fake_pre, 'OC2': fake_oc2}

    error_defn, error_func = validate_1012()

    assert error_func(fake_dfs) == {'PlacedAdoption': [0], 'Missing': [1],
                                    'Reviews': [2], 'AD1': [3], 'PrevPerm': [4], 'OC2': [5]}

    assert error_func(fake_dfs_partial) == {'AD1': [3], 'PrevPerm': [4], 'OC2': [5]}


def test_validate_432():
    fake_data = pd.DataFrame([
        {'CHILD': '111', 'RNE': 'P', 'DECOM': '01/06/2020', 'REC': 'E2'},  # 0
        {'CHILD': '111', 'RNE': 'P', 'DECOM': '05/06/2020', 'REC': 'E3'},  # 1
        {'CHILD': '111', 'RNE': 'T', 'DECOM': '06/06/2020', 'REC': 'E3'},  # 2
        {'CHILD': '111', 'RNE': 'S', 'DECOM': '08/06/2020', 'REC': pd.NA},  # 3
        {'CHILD': '222', 'RNE': 'S', 'DECOM': '05/06/2020', 'REC': 'E3'},  # 4
        {'CHILD': '333', 'RNE': 'B', 'DECOM': '06/06/2020', 'REC': 'E3'},  # 5
        {'CHILD': '333', 'RNE': 'U', 'DECOM': '10/06/2020', 'REC': pd.NA},  # 6
        {'CHILD': '444', 'RNE': 'S', 'DECOM': '07/06/2020', 'REC': 'E3'},  # 7
        {'CHILD': '444', 'RNE': 'S', 'DECOM': '08/06/2020', 'REC': 'E3'},  # 8
        {'CHILD': '444', 'RNE': 'T', 'DECOM': '09/06/2020', 'REC': 'E3'},  # 9
        {'CHILD': '444', 'RNE': 'S', 'DECOM': '15/06/2020', 'REC': 'E3'},  # 10
    ])

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_432()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [1, 2, 6, 9]}


def test_validate_331():
    fake_adt = pd.DataFrame({
        'CHILD': ['111', '222', '333', '444',
                  '555', '66'],
        'DATE_MATCH': ['01/01/2020', '02/06/2020', '11/11/2020', pd.NA,
                       '01/02/2020', '04/06/2020']
    })
    fake_eps = pd.DataFrame({
        'CHILD': ['111', '222', '333', '444',
                  '555', '555', '555',
                  '66', '66', '66', '66'],
        'DECOM': ['01/01/2020', '01/06/2020', '12/12/2020', '01/02/2020',
                  '01/01/2020', '01/02/2020', '05/06/2020',
                  '01/01/2020', '01/02/2020', '05/06/2020', '06/07/2020'],
        'REC': ['E12', 'E11', 'E12', 'E11',
                'xX', 'E11', 'E12',
                'Xx', 'oO', 'E11', 'Oo']
    })

    fake_dfs = {'AD1': fake_adt, 'Episodes': fake_eps}

    error_defn, error_func = validate_331()

    result = error_func(fake_dfs)

    assert result == {'AD1': [1],
                      'Episodes': [1]}


def test_validate_362():
    fake_data = pd.DataFrame([
        {'CHILD': '111', 'DECOM': '01/06/2020', 'DEC': '04/06/2020', 'LS': 'L2'},  # 0  CHANGE |a
        {'CHILD': '111', 'DECOM': '04/06/2020', 'DEC': '05/06/2020', 'LS': 'L2'},  # 1         |a Passes as <=21
        {'CHILD': '111', 'DECOM': '06/07/2020', 'DEC': '07/07/2020', 'LS': 'E2'},  # 2
        {'CHILD': '111', 'DECOM': '08/09/2020', 'DEC': '09/10/2020', 'LS': 'L2'},  # 3  CHANGE |b  Fail
        {'CHILD': '111', 'DECOM': '09/10/2020', 'DEC': '12/11/2020', 'LS': 'L2'},  # 4         |b  Fail
        {'CHILD': '333', 'DECOM': '06/06/2020', 'DEC': '10/06/2020', 'LS': 'L2'},  # 5  CHANGE |c  Fail
        {'CHILD': '333', 'DECOM': '10/06/2020', 'DEC': '12/10/2020', 'LS': 'L2'},  # 6         |c  Fail
        {'CHILD': '444', 'DECOM': '07/06/2020', 'DEC': '08/07/2020', 'LS': 'L2'},  # 7  CHANGE |d  Fail
        {'CHILD': '444', 'DECOM': '08/08/2020', 'DEC': '09/08/2020', 'LS': 'E4'},  # 8
        {'CHILD': '444', 'DECOM': '09/08/2020', 'DEC': '15/08/2020', 'LS': 'L2'},  # 9  CHANGE |e  Fail
        {'CHILD': '444', 'DECOM': '15/08/2020', 'DEC': pd.NA, 'LS': 'L2'},  # 10        |e  Fail
        {'CHILD': '555', 'DECOM': '15/03/2021', 'DEC': pd.NA, 'LS': 'L2'},  # 11 CHANGE |f  Passes as <=21
    ])
    metadata = {'collection_end': '31/03/2021'}

    fake_dfs = {'Episodes': fake_data, 'metadata': metadata}

    error_defn, error_func = validate_362()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [3, 4, 5, 6, 7, 9, 10]}


def test_validate_361():
    fake_data = pd.DataFrame([
        {'CHILD': '111', 'DECOM': '01/06/2020', 'DEC': '04/06/2020', 'LS': 'L1'},  # 0  CHANGE |a
        {'CHILD': '111', 'DECOM': '04/06/2020', 'DEC': '05/06/2020', 'LS': 'L1'},  # 1         |a
        {'CHILD': '111', 'DECOM': '06/07/2020', 'DEC': '07/07/2020', 'LS': 'E2'},  # 2
        {'CHILD': '111', 'DECOM': '08/09/2020', 'DEC': '10/09/2020', 'LS': 'L1'},  # 3  CHANGE |b Passes as <=3
        {'CHILD': '111', 'DECOM': '09/10/2020', 'DEC': '12/11/2020', 'LS': 'E3'},  # 4
        {'CHILD': '333', 'DECOM': '06/06/2020', 'DEC': '10/06/2020', 'LS': 'L1'},  # 5  CHANGE |c  Fail
        {'CHILD': '333', 'DECOM': '10/06/2020', 'DEC': '12/10/2020', 'LS': 'L1'},  # 6         |c  Fail
        {'CHILD': '444', 'DECOM': '07/06/2020', 'DEC': '08/07/2020', 'LS': 'L1'},  # 7  CHANGE |d  Fail
        {'CHILD': '444', 'DECOM': '08/08/2020', 'DEC': '09/08/2020', 'LS': 'E4'},  # 8
        {'CHILD': '444', 'DECOM': '09/08/2020', 'DEC': '15/08/2020', 'LS': 'L1'},  # 9  CHANGE |e  Fail
        {'CHILD': '444', 'DECOM': '15/08/2020', 'DEC': pd.NA, 'LS': 'L1'},  # 10        |e  Fail
        {'CHILD': '555', 'DECOM': '15/03/2021', 'DEC': pd.NA, 'LS': 'L1'},  # 11 CHANGE |f  Fail
    ])
    metadata = {'collection_end': '31/03/2021'}

    fake_dfs = {'Episodes': fake_data, 'metadata': metadata}

    error_defn, error_func = validate_361()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [0, 1, 5, 6, 7, 9, 10, 11]}


def test_validate_435():
    fake_data = pd.DataFrame([
        {'CHILD': '111', 'DECOM': '01/06/2020', 'RNE': 'P', 'LS': 'L1', 'PL_POST': 'XX1',
         'URN': 'SC112', 'PLACE': 'R1', 'PLACE_PROVIDER': 'PR1'},  # 0
        {'CHILD': '111', 'DECOM': '03/06/2020', 'RNE': 'P', 'LS': 'L1', 'PL_POST': 'XX3',
         'URN': 'SC112', 'PLACE': 'R1', 'PLACE_PROVIDER': 'PR1'},  # 1
        {'CHILD': '111', 'DECOM': '04/06/2020', 'RNE': 'P', 'LS': 'L1', 'PL_POST': 'XX3',
         'URN': 'SC112', 'PLACE': 'R1', 'PLACE_PROVIDER': 'PR1'},  # 2 Fail all the same
        {'CHILD': '111', 'DECOM': '05/06/2020', 'RNE': 'P', 'LS': 'L1', 'PL_POST': 'XX1',
         'URN': 'SC112', 'PLACE': 'R1', 'PLACE_PROVIDER': 'PR1'},  # 3
        {'CHILD': '222', 'DECOM': '07/06/2020', 'RNE': 'P', 'LS': 'L1', 'PL_POST': 'XX1',
         'URN': 'SC112', 'PLACE': 'R1', 'PLACE_PROVIDER': 'PR4'},  # 4
        {'CHILD': '222', 'DECOM': '08/06/2020', 'RNE': 'P', 'LS': 'L1', 'PL_POST': 'XX1',
         'URN': 'SC112', 'PLACE': 'R1', 'PLACE_PROVIDER': 'PR1'},  # 5
        {'CHILD': '222', 'DECOM': '09/06/2020', 'RNE': 'P', 'LS': 'L3', 'PL_POST': 'XX1',
         'URN': 'SC112', 'PLACE': 'R1', 'PLACE_PROVIDER': 'PR1'},  # 6 Fail dif LS
    ])

    fake_dfs = {'Episodes': fake_data}

    error_defn, error_func = validate_435()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [2, 6]}


def test_validate_624():
    hdr = pd.DataFrame([
        {'CHILD': '111', 'MC_DOB': '01/06/2020'},  # 0
        {'CHILD': '222', 'MC_DOB': '04/06/2020'},  # 1
        {'CHILD': '333', 'MC_DOB': pd.NA},  # 2
        {'CHILD': '444', 'MC_DOB': '08/09/2020'},  # 3
        {'CHILD': '555', 'MC_DOB': pd.NA},  # 4
        {'CHILD': '66', 'MC_DOB': '01/02/2020'},  # 5

    ])
    hdr_last = pd.DataFrame([
        {'CHILD': '111', 'MC_DOB': '01/06/2020'},  # 0
        {'CHILD': '222', 'MC_DOB': '04/06/2020'},  # 1
        {'CHILD': '333', 'MC_DOB': '01/06/2019'},  # 2
        {'CHILD': '444', 'MC_DOB': '10/09/2020'},  # 3
        {'CHILD': '555', 'MC_DOB': pd.NA},  # 4
        {'CHILD': '66', 'MC_DOB': pd.NA},  # 5
    ])
    fake_dfs = {'Header': hdr, 'Header_last': hdr_last}

    error_defn, error_func = validate_624()

    result = error_func(fake_dfs)

    assert result == {'Header': [2, 3]}


def test_validate_626():
    header = pd.DataFrame([
        {'CHILD': '111', 'MOTHER': 1, 'MC_DOB': pd.NA},  # 0
        {'CHILD': '222', 'MOTHER': '1', 'MC_DOB': '04/01/2020'},  # 1 Fail
        {'CHILD': '333', 'MOTHER': 0, 'MC_DOB': pd.NA},  # 2
        {'CHILD': '444', 'MOTHER': 1.0, 'MC_DOB': '01/04/2020'},  # 3
    ])
    header_last = pd.DataFrame([
        {'CHILD': '111', 'MOTHER': '1'},  # 0
        {'CHILD': '222', 'MOTHER': 0.0},  # 1
        {'CHILD': '333', 'MOTHER': '1'},  # 2
        {'CHILD': '444', 'MOTHER': '0'},  # 3
    ])
    metadata = {'collection_start': '01/04/2020'}

    fake_dfs = {'Header': header, 'Header_last': header_last, 'metadata': metadata}

    error_defn, error_func = validate_626()

    result = error_func(fake_dfs)

    assert result == {'Header': [1]}


def test_validate_104():
    fake_uasc = pd.DataFrame({
        'DUC': ['01/03/2019', '19/02/2020', '03/04/2019', '01/01/2019', pd.NA, 'INNVLAID/DATE/2077'],
    })

    metadata = {'collection_start': '01/04/2019'}

    fake_dfs = {'UASC': fake_uasc, 'metadata': metadata}

    error_defn, error_func = validate_104()

    result = error_func(fake_dfs)
    assert result == {'UASC': [0, 3, 5]}


def test_validate_392B():
    fake_episodes = pd.DataFrame([
        {'CHILD': '111', 'LS': 'L1', 'HOME_POST': 'XX1', 'PL_POST': 'XX1'},  # 0
        {'CHILD': '222', 'LS': 'L1', 'HOME_POST': 'XX1', 'PL_POST': pd.NA},  # 1
        {'CHILD': '222', 'LS': 'V3', 'HOME_POST': pd.NA, 'PL_POST': 'XX1'},  # 2
        {'CHILD': '333', 'LS': 'L1', 'HOME_POST': 'XX1', 'PL_POST': pd.NA},  # 3
        {'CHILD': '333', 'LS': 'V4', 'HOME_POST': 'XX1', 'PL_POST': 'XX1'},  # 4
        {'CHILD': '345', 'LS': 'L1', 'HOME_POST': 'XX1', 'PL_POST': pd.NA},  # 5
        {'CHILD': '444', 'LS': 'L1', 'HOME_POST': 'XX1', 'PL_POST': 'XX1'},  # 6
        {'CHILD': '444', 'LS': 'V3', 'HOME_POST': pd.NA, 'PL_POST': pd.NA},  # 7
    ])

    fake_header = pd.DataFrame([
        {'CHILD': '111', 'UASC': '1'},  # 0
        {'CHILD': '222', 'UASC': '0'},  # 2
        {'CHILD': '333', 'UASC': '0'},  # 4
        {'CHILD': '345', 'UASC': '0'},  # 5
        {'CHILD': '444', 'UASC': '0'},  # 6
    ])
    fake_header_last = pd.DataFrame([
        {'CHILD': '111', 'UASC': '0'},  # 0
        {'CHILD': '222', 'UASC': '0'},  # 2
        {'CHILD': '333', 'UASC': '0'},  # 4
        {'CHILD': '345', 'UASC': '0'},  # 5
        {'CHILD': '444', 'UASC': '1'},  # 6
    ])

    fake_dfs = {'Episodes': fake_episodes, 'Header': fake_header, 'Header_last':fake_header_last}

    error_defn, error_func = validate_392B()

    result = error_func(fake_dfs)

    assert result == {'Episodes': [1, 3, 5]}

    uasc_last = pd.DataFrame([
        {'CHILD': '222', 'DUC': '01/01/1990', 'ETC': pd.NA},
        {'CHILD': '345', 'DUC': pd.NA, 'ETC': pd.NA},
    ])

    fake_dfs = {'Episodes': fake_episodes, 'UASC_last': uasc_last}

    result = error_func(fake_dfs)

    assert result == {'Episodes': [3, 5]}

