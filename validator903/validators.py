import pandas as pd

from .datastore import merge_postcodes
from .types import ErrorDefinition
from .utils import add_col_to_tables_CONTINUOUSLY_LOOKED_AFTER as add_CLA_column  # Check 'Episodes' present before use!

def validate_391():
  error = ErrorDefinition(
    code = '391',
    description = 'Young person was not 17, 18, 19, 20 or 21 during the current collection year. ',
    affected_fields = ['DOB','IN_TOUCH', 'ACTIV', 'ACCOM']
  )
  def _validate(dfs):
    if 'OC3' not in dfs:
      return {}
    else:
      oc3 = dfs['OC3']
      collection_end = dfs['metadata']['collection_end']

      # convert dates to datetime format
      oc3['DOB'] = pd.to_datetime(oc3['DOB'], format='%d/%m/%Y', errors='coerce')
      collection_end = pd.to_datetime(collection_end, format='%d/%m/%Y', errors='coerce')

      # If <DOB> < 17 years prior to <COLLECTION_END_DATE> then <IN_TOUCH>, <ACTIV> and <ACCOM> should not be provided
      check_age = (oc3['DOB'] + pd.offsets.DateOffset(years=17) > collection_end)
      mask = check_age & (oc3['IN_TOUCH'].notna()|oc3['ACTIV'].notna()|oc3['ACCOM'].notna())
      # Then raise an error if either IN_TOUCH, ACTIV, or ACCOM have been provided too

      # error locations
      oc3_error_locs = oc3.index[mask]

      return {'OC3':oc3_error_locs.tolist()}
  return error, _validate

def validate_632():
  error = ErrorDefinition(
    code = '632',
    description = 'Date of previous permanence order not a valid value. NOTE: This rule may result in false negatives where the period of care started before the current collection year',
    affected_fields = ['DATE_PERM', 'DECOM'],
  )
  def _validate(dfs):
    if 'Episodes' not in dfs or 'PrevPerm' not in dfs:
      return {}
    else:

      # function to check that date is of the right format
      def valid_date(dte):
          try:
            lst = dte.split('/')
          except AttributeError:
            return pd.NaT
          # Preceding block checks for the scenario where the value passed in is nan/naT

          # date should have three elements
          if (len(lst) != 3):
              return pd.NaT

          z_list = ['ZZ', 'ZZ', 'ZZZZ']
          # We set the date to the latest possible value to avoid false positives
          offset_list = [pd.DateOffset(months=1, days=-1),
                        pd.DateOffset(years=1, days=-1),
                        None]
          # that is, go to the next month/year and take the day before that
          already_found_non_zeds = False
          date_bits = []

          for i, zeds, offset in zip(lst, z_list, offset_list):
              if i == zeds:
                  # I'm assuming it is invalid to have a date like '01/ZZ/ZZZZ'
                  if already_found_non_zeds:
                      return pd.NaT
                  # Replace day & month zeds with '01' so we can check if the resulting date is valid
                  # and set the offset so we can compare the latest corresponding date
                  elif i == 'ZZ':
                      i = '01'
                      offset_to_use = offset
              else:
                  already_found_non_zeds = True
              date_bits.append(i)

          as_datetime = pd.to_datetime('/'.join(date_bits),
                                      format='%d/%m/%Y', errors='coerce')
          try:
              as_datetime += offset_to_use
          except NameError:  # offset_to_use only defined if needed
              pass
          return as_datetime

      episodes = dfs['Episodes']
      prevperm = dfs['PrevPerm']

      # convert dates from strings to appropriate format.
      episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
      prevperm['DATE_PERM_dt'] = prevperm['DATE_PERM'].apply(valid_date)

      # select first episodes
      first_eps_idxs = episodes.groupby('CHILD')['DECOM'].idxmin()
      first_eps = episodes[episodes.index.isin(first_eps_idxs)]

      # prepare to merge
      first_eps.reset_index(inplace=True)
      prevperm.reset_index(inplace=True)
      merged = first_eps.merge(prevperm, on='CHILD', how='left', suffixes=['_eps', '_prev'])

      # If provided <DATE_PERM> should be prior to <DECOM> and in a valid format and contain a valid date Format should be DD/MM/YYYY or one or more elements of the date can be replaced by ZZ if part of the date element is not known.
      mask = (merged['DATE_PERM_dt'] >= merged['DECOM']) | (merged['DATE_PERM'].notna()
                                                            & merged['DATE_PERM_dt'].isna()
                                                            & (merged['DATE_PERM'] != 'ZZ/ZZ/ZZZZ')
                                                            )

      # error locations
      prev_error_locs = merged.loc[mask, 'index_prev']
      eps_error_locs = merged.loc[mask, 'index_eps']

      return {'Episodes':eps_error_locs.tolist(), 'PrevPerm':prev_error_locs.unique().tolist()}

  return error, _validate

def validate_165():
  error = ErrorDefinition(
    code = '165',
    description = 'Data entry for mother status is invalid.',
    affected_fields = ['MOTHER', 'SEX', 'ACTIV', 'ACCOM', 'IN_TOUCH', 'DECOM']
  )
  def _validate(dfs):
    if 'Header' not in dfs or 'Episodes' not in dfs or 'OC3' not in dfs:
      return {}
    else:
      header = dfs['Header']
      episodes = dfs['Episodes']
      oc3 = dfs['OC3']
      collection_start = dfs['metadata']['collection_start']
      collection_end = dfs['metadata']['collection_end']
      valid_values = ['0','1']

      # prepare to merge
      oc3.reset_index(inplace=True)
      header.reset_index(inplace=True)
      episodes.reset_index(inplace=True)

      collection_start = pd.to_datetime(collection_start, format='%d/%m/%Y', errors='coerce')
      collection_end = pd.to_datetime(collection_end, format='%d/%m/%Y', errors='coerce')
      episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')

      episodes['EPS'] = (episodes['DECOM']>=collection_start) & (episodes['DECOM']<=collection_end)
      episodes['EPS_COUNT'] = episodes.groupby('CHILD')['EPS'].transform('sum')

      merged = episodes.merge(header, on='CHILD', how='left', suffixes=['_eps', '_er']).merge(oc3, on='CHILD', how='left')

      # Raise error if provided <MOTHER> is not a valid value.
      value_validity = merged['MOTHER'].notna() & (~merged['MOTHER'].isin(valid_values))
      # If not provided
      female = (merged['SEX']=='1')
      eps_in_year = (merged['EPS_COUNT']>0)
      none_provided = (merged['ACTIV'].isna()& merged['ACCOM'].isna()& merged['IN_TOUCH'].isna())
      # If provided <MOTHER> must be a valid value. If not provided <MOTHER> then either <GENDER> is male or no episode record for current year and any of <IN_TOUCH>, <ACTIV> or <ACCOM> have been provided
      mask = value_validity | (merged['MOTHER'].isna() & (female & (eps_in_year | none_provided)))
      # That is, if value not provided and child is a female with eps in current year or no values of IN_TOUCH, ACTIV and ACCOM, then raise error.
      error_locs_eps = merged.loc[mask, 'index_eps']
      error_locs_header = merged.loc[mask, 'index_er']
      error_locs_oc3 = merged.loc[mask, 'index']

      return {'Header':error_locs_header.dropna().unique().tolist(),
              'OC3':error_locs_oc3.dropna().unique().tolist()}
  return error, _validate

def validate_1014():
    error = ErrorDefinition(
        code='1014',
        description='UASC information is not required for care leavers',
        affected_fields=['ACTIV', 'ACCOM', 'IN_TOUCH', 'DUC']
    )

    def _validate(dfs):
        if 'UASC' not in dfs or 'Episodes' not in dfs or 'OC3' not in dfs:
            return {}
        else:
            uasc = dfs['UASC']
            episodes = dfs['Episodes']
            oc3 = dfs['OC3']
            collection_start = dfs['metadata']['collection_start']
            collection_end = dfs['metadata']['collection_end']

            # prepare to merge
            oc3.reset_index(inplace=True)
            uasc.reset_index(inplace=True)
            episodes.reset_index(inplace=True)

            collection_start = pd.to_datetime(collection_start, format='%d/%m/%Y', errors='coerce')
            collection_end = pd.to_datetime(collection_end, format='%d/%m/%Y', errors='coerce')
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
            episodes['DEC'] = pd.to_datetime(episodes['DEC'], format='%d/%m/%Y', errors='coerce')

            date_check = (
                    ((episodes['DEC'] >= collection_start) & (episodes['DECOM'] <= collection_end))
                    | ((episodes['DECOM'] <= collection_end) & episodes['DEC'].isna())
            )
            episodes['EPS'] = date_check
            episodes['EPS_COUNT'] = episodes.groupby('CHILD')['EPS'].transform('sum')

            # inner merge to take only episodes of children which are also found on the uasc table
            merged = episodes.merge(uasc, on='CHILD', how='inner', suffixes=['_eps', '_sc']).merge(oc3, on='CHILD',
                                                                                                   how='left')
            # adding suffixes with the secondary merge here does not go so well yet.

            some_provided = (merged['ACTIV'].notna() | merged['ACCOM'].notna() | merged['IN_TOUCH'].notna())

            mask = (merged['EPS_COUNT'] == 0) & some_provided

            error_locs_uasc = merged.loc[mask, 'index_sc']
            error_locs_oc3 = merged.loc[mask, 'index']

            return {'UASC': error_locs_uasc.unique().tolist(), 'OC3': error_locs_oc3.unique().tolist()}

    return error, _validate


# !# not sure what this rule is actually supposed to be getting at - description is confusing
def validate_197B():
    error = ErrorDefinition(
        code='197B',
        description="SDQ score or reason for no SDQ should be reported for 4- or 17-year-olds.",
        affected_fields=['SDQ_REASON', 'DOB'],
    )

    def _validate(dfs):
        if 'OC2' not in dfs or 'Episodes' not in dfs:
            return {}
        oc2 = add_CLA_column(dfs, 'OC2')

        start = pd.to_datetime(dfs['metadata']['collection_start'], format='%d/%m/%Y', errors='coerce')
        endo = pd.to_datetime(dfs['metadata']['collection_end'], format='%d/%m/%Y', errors='coerce')
        oc2['DOB'] = pd.to_datetime(oc2['DOB'], format='%d/%m/%Y', errors='coerce')

        ERRRR = (
                (
                        (oc2['DOB'] + pd.DateOffset(years=4) == start)  # ???
                        | (oc2['DOB'] + pd.DateOffset(years=17) == start)
                )
                & oc2['CONTINUOUSLY_LOOKED_AFTER']
                & oc2['SDQ_SCORE'].isna()
                & oc2['SDQ_REASON'].isna()
        )

        return {'OC2': oc2[ERRRR].index.to_list()}

    return error, _validate


def validate_157():
    error = ErrorDefinition(
        code='157',
        description="Child is aged 4 years or over at the beginning of the year or 16 years or under at the end of the "
                    "year and Strengths and Difficulties Questionnaire (SDQ) 1 has been recorded as the reason for no "
                    "Strengths and Difficulties Questionnaire (SDQ) score.",
        affected_fields=['SDQ_REASON', 'DOB'],
    )

    def _validate(dfs):
        if 'OC2' not in dfs or 'Episodes' not in dfs:
            return {}
        oc2 = add_CLA_column(dfs, 'OC2')

        start = pd.to_datetime(dfs['metadata']['collection_start'], format='%d/%m/%Y', errors='coerce')
        endo = pd.to_datetime(dfs['metadata']['collection_end'], format='%d/%m/%Y', errors='coerce')
        oc2['DOB'] = pd.to_datetime(oc2['DOB'], format='%d/%m/%Y', errors='coerce')

        ERRRR = (
                oc2['CONTINUOUSLY_LOOKED_AFTER']
                & (oc2['DOB'] + pd.DateOffset(years=4) <= start)
                & (oc2['DOB'] + pd.DateOffset(years=16) >= endo)
                & oc2['SDQ_SCORE'].isna()
                & (oc2['SDQ_REASON'] == 'SDQ1')
        )

        return {'OC2': oc2[ERRRR].index.to_list()}

    return error, _validate


def validate_357():
    error = ErrorDefinition(
        code='357',
        description='If this is the first episode ever for this child, reason for new episode must be S.  '
                    'Check whether there is an episode immediately preceding this one, which has been left out.  '
                    'If not the reason for new episode code must be amended to S.',
        affected_fields=['RNE'],
    )

    # !# Potential false negatives for first episodes before the current collection year?
    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        eps = dfs['Episodes']
        collection_start = pd.to_datetime(dfs['metadata']['collection_start'], format='%d/%m/%Y', errors='coerce')
        eps['DECOM'] = pd.to_datetime(eps['DECOM'], format='%d/%m/%Y', errors='coerce')

        eps = eps.loc[eps['DECOM'].notnull()]

        first_eps = (eps
                     .loc[eps.groupby('CHILD')['DECOM'].idxmin()]
                     .loc[eps['DECOM'] >= collection_start])

        errs = first_eps[first_eps['RNE'] != 'S'].index.to_list()

        return {'Episodes': errs}

    return error, _validate


def validate_117():
    error = ErrorDefinition(
        code='117',
        description='Date of decision that a child should/should no longer be placed for adoption is beyond the current collection year or after the child ceased to be looked after.',
        affected_fields=['DATE_PLACED_CEASED', 'DATE_PLACED', 'DEC', 'REC', 'DECOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'PlacedAdoption' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            placed_adoption = dfs['PlacedAdoption']
            collection_end = dfs['metadata']['collection_end']

            # datetime
            placed_adoption['DATE_PLACED_CEASED'] = pd.to_datetime(placed_adoption['DATE_PLACED_CEASED'],
                                                                   format='%d/%m/%Y', errors='coerce')
            placed_adoption['DATE_PLACED'] = pd.to_datetime(placed_adoption['DATE_PLACED'], format='%d/%m/%Y',
                                                            errors='coerce')
            collection_end = pd.to_datetime(collection_end, format='%d/%m/%Y', errors='coerce')
            episodes['DEC'] = pd.to_datetime(episodes['DEC'], format='%d/%m/%Y', errors='coerce')
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')

            # Drop nans and continuing episodes
            episodes = episodes.dropna(subset=['DECOM'])
            episodes = episodes[episodes['REC'] != 'X1']

            episodes = episodes.loc[episodes.groupby('CHILD')['DECOM'].idxmax()]

            # prepare to merge
            placed_adoption.reset_index(inplace=True)
            episodes.reset_index(inplace=True)

            p4a_cols = ['DATE_PLACED', 'DATE_PLACED_CEASED']

            # latest episodes
            merged = episodes.merge(placed_adoption, on='CHILD', how='left', suffixes=['_eps', '_pa'])
            mask = (
                    (merged['DATE_PLACED'] > collection_end)
                    | (merged['DATE_PLACED'] > merged['DEC'])
                    | (merged['DATE_PLACED_CEASED'] > collection_end)
                    | (merged['DATE_PLACED_CEASED'] > merged['DEC'])
            )
            # If provided <DATE_PLACED> and/or <DATE_PLACED_CEASED> must not be > <COLLECTION_END_DATE> or <DEC> of latest episode where <REC> not = 'X1'
            pa_error_locs = merged.loc[mask, 'index_pa']
            eps_error_locs = merged.loc[mask, 'index_eps']
            return {'Episodes': eps_error_locs.tolist(), 'PlacedAdoption': pa_error_locs.unique().tolist()}

    return error, _validate


def validate_118():
    error = ErrorDefinition(
        code='118',
        description='Date of decision that a child should no longer be placed for adoption is before the current collection year or before the date the child started to be looked after.',
        affected_fields=['DECOM', 'DECOM', 'LS']
    )

    def _validate(dfs):
        if ('PlacedAdoption' not in dfs) or ('Episodes' not in dfs):
            return {}
        else:
            placed_adoption = dfs['PlacedAdoption']
            episodes = dfs['Episodes']
            collection_start = dfs['metadata']['collection_start']
            code_list = ['V3', 'V4']

            # datetime
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
            placed_adoption['DATE_PLACED_CEASED'] = pd.to_datetime(placed_adoption['DATE_PLACED_CEASED'],
                                                                   format='%d/%m/%Y', errors='coerce')
            collection_start = pd.to_datetime(collection_start, format='%d/%m/%Y', errors='coerce')

            # <DECOM> of the earliest episode with an <LS> not = 'V3' or 'V4'
            filter_by_ls = episodes[~(episodes['LS'].isin(code_list))]
            earliest_episode_idxs = filter_by_ls.groupby('CHILD')['DECOM'].idxmin()
            earliest_episodes = episodes[episodes.index.isin(earliest_episode_idxs)]

            # prepare to merge
            placed_adoption.reset_index(inplace=True)
            earliest_episodes.reset_index(inplace=True)

            # merge
            merged = earliest_episodes.merge(placed_adoption, on='CHILD', how='left', suffixes=['_eps', '_pa'])

            # drop rows where DATE_PLACED_CEASED is not provided
            merged = merged.dropna(subset=['DATE_PLACED_CEASED'])
            # If provided <DATE_PLACED_CEASED> must not be prior to <COLLECTION_START_DATE> or <DECOM> of the earliest episode with an <LS> not = 'V3' or 'V4'
            mask = (merged['DATE_PLACED_CEASED'] < merged['DECOM']) | (merged['DATE_PLACED_CEASED'] < collection_start)
            # error locations
            pa_error_locs = merged.loc[mask, 'index_pa']
            eps_error_locs = merged.loc[mask, 'index_eps']
            return {'Episodes': eps_error_locs.tolist(), 'PlacedAdoption': pa_error_locs.unique().tolist()}

    return error, _validate


def validate_352():
    error = ErrorDefinition(
        code='352',
        description='Child who started to be looked after was aged 18 or over.',
        affected_fields=['DECOM', 'RNE'],
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}
        if 'Episodes' not in dfs:
            return {}
        else:
            header = dfs['Header']
            episodes = dfs['Episodes']

            header['DOB'] = pd.to_datetime(header['DOB'], format='%d/%m/%Y', errors='coerce')
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
            header['DOB18'] = header['DOB'] + pd.DateOffset(years=18)

            episodes_merged = episodes.reset_index().merge(header, how='left', on=['CHILD'], suffixes=('', '_header'),
                                                           indicator=True).set_index('index')

            care_start = episodes_merged['RNE'].str.upper().astype(str).isin(['S'])
            started_over_18 = episodes_merged['DOB18'] <= episodes_merged['DECOM']

            error_mask = care_start & started_over_18

            error_locations = episodes_merged.index[error_mask].unique()

            return {'Episodes': error_locations.to_list()}

    return error, _validate


def validate_209():
    error = ErrorDefinition(
        code='209',
        description='Child looked after is of school age and should not have an unknown Unique Pupil Number (UPN) code of UN1.',
        affected_fields=['UPN', 'DOB']
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}
        else:
            header = dfs['Header']
            collection_start = dfs['metadata']['collection_start']
            # convert to datetime
            header['DOB'] = pd.to_datetime(header['DOB'], format='%d/%m/%Y', errors='coerce')
            collection_start = pd.to_datetime(collection_start, format='%d/%m/%Y', errors='coerce')
            yr = collection_start.year - 1
            reference_date = pd.to_datetime('31/08/' + str(yr), format='%d/%m/%Y', errors='coerce')
            # If <DOB> >= 4 years prior to 31/08/YYYY then <UPN> should not be 'UN1' Note: YYYY in this instance refers to the year prior to the collection start (for collection year 2019-2020, it would be looking at the 31/08/2018).
            mask = (reference_date >= (header['DOB'] + pd.offsets.DateOffset(years=4))) & (header['UPN'] == 'UN1')
            # error locations
            error_locs_header = header.index[mask]
            return {'Header': error_locs_header.tolist()}

    return error, _validate


def validate_198():
    error = ErrorDefinition(
        code='198',
        description="Child has not been looked after continuously for at least 12 months at 31 March but a reason "
                    "for no Strengths and Difficulties (SDQ) score has been completed. ",
        affected_fields=['SDQ_REASON'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'OC2' not in dfs:
            return {}

        oc2 = add_CLA_column(dfs, 'OC2')

        error_mask = oc2['SDQ_REASON'].notna() & ~oc2['CONTINUOUSLY_LOOKED_AFTER']

        error_locs = oc2.index[error_mask].to_list()

        return {'OC2': error_locs}

    return error, _validate


def validate_185():
    error = ErrorDefinition(
        code='185',
        description="Child has not been looked after continuously for at least 12 months at " +
                    "31 March but a Strengths and Difficulties (SDQ) score has been completed.",
        affected_fields=['SDQ_SCORE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'OC2' not in dfs:
            return {}

        oc2 = add_CLA_column(dfs, 'OC2')

        error_mask = oc2['SDQ_SCORE'].notna() & ~oc2['CONTINUOUSLY_LOOKED_AFTER']

        error_locs = oc2.index[error_mask].to_list()

        return {'OC2': error_locs}

    return error, _validate


def validate_186():
    error = ErrorDefinition(
        code='186',
        description="Children aged 4 or over at the start of the year and children aged under 17 at the " +
                    "end of the year and who have been looked after for at least 12 months continuously " +
                    "should have a Strengths and Difficulties (SDQ) score completed.",
        affected_fields=['SDQ_SCORE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'OC2' not in dfs:
            return {}

        oc2 = dfs['OC2']

        collection_start_str = dfs['metadata']['collection_start']
        collection_end_str = dfs['metadata']['collection_end']

        collection_start = pd.to_datetime(collection_start_str, format='%d/%m/%Y', errors='coerce')
        collection_end = pd.to_datetime(collection_end_str, format='%d/%m/%Y', errors='coerce')
        oc2['DOB_dt'] = pd.to_datetime(oc2['DOB'], format='%d/%m/%Y', errors='coerce')

        oc2 = add_CLA_column(dfs, 'OC2')

        oc2['4th_bday'] = oc2['DOB_dt'] + pd.DateOffset(years=4)
        oc2['17th_bday'] = oc2['DOB_dt'] + pd.DateOffset(years=17)
        error_mask = (
                (oc2['4th_bday'] <= collection_start)
                & (oc2['17th_bday'] > collection_end)
                & oc2['CONTINUOUSLY_LOOKED_AFTER']
                & oc2['SDQ_SCORE'].isna()
        )

        oc2_errors = oc2.loc[error_mask].index.to_list()

        return {'OC2': oc2_errors}

    return error, _validate


def validate_187():
    error = ErrorDefinition(
        code='187',
        description="Child cannot be looked after continuously for 12 months at " +
                    "31 March (OC2) and have any of adoption or care leavers returns completed.",
        affected_fields=['DATE_INT', 'DATE_MATCH', 'FOSTER_CARE', 'NB_ADOPTR', 'SEX_ADOPTR', 'LS_ADOPTR',  # OC3
                         'IN_TOUCH', 'ACTIV', 'ACCOM'],  # AD1
    )

    def _validate(dfs):
        if (
                'OC3' not in dfs
                or 'AD1' not in dfs
                or 'Episodes' not in dfs
        ):
            return {}

        # add 'CONTINUOUSLY_LOOKED_AFTER' column
        ad1, oc3 = add_CLA_column(dfs, ['AD1', 'OC3'])

        # OC3
        should_be_blank = ['IN_TOUCH', 'ACTIV', 'ACCOM']
        oc3_mask = oc3['CONTINUOUSLY_LOOKED_AFTER'] & oc3[should_be_blank].notna().any(axis=1)
        oc3_error_locs = oc3[oc3_mask].index.to_list()

        # AD1
        should_be_blank = ['DATE_INT', 'DATE_MATCH', 'FOSTER_CARE', 'NB_ADOPTR', 'SEX_ADOPTR', 'LS_ADOPTR']
        ad1_mask = ad1['CONTINUOUSLY_LOOKED_AFTER'] & ad1[should_be_blank].notna().any(axis=1)
        ad1_error_locs = ad1[ad1_mask].index.to_list()

        return {'AD1': ad1_error_locs,
                'OC3': oc3_error_locs}

    return error, _validate


def validate_188():
    error = ErrorDefinition(
        code='188',
        description="Child is aged under 4 years at the end of the year, "
                    "but a Strengths and Difficulties (SDQ) score or a reason "
                    "for no SDQ score has been completed. ",
        affected_fields=['SDQ_SCORE', 'SDQ_REASON'],
    )

    def _validate(dfs):
        if 'OC2' not in dfs:
            return {}

        oc2 = dfs['OC2']

        collection_end_str = dfs['metadata']['collection_end']

        collection_end = pd.to_datetime(collection_end_str, format='%d/%m/%Y', errors='coerce')
        oc2['DOB_dt'] = pd.to_datetime(oc2['DOB'], format='%d/%m/%Y', errors='coerce')

        oc2['4th_bday'] = oc2['DOB_dt'] + pd.DateOffset(years=4)
        error_mask = (
                (oc2['4th_bday'] > collection_end)
                & oc2[['SDQ_SCORE', 'SDQ_REASON']].notna().any(axis=1)
        )

        oc2_errors = oc2.loc[error_mask].index.to_list()

        return {'OC2': oc2_errors}

    return error, _validate


def validate_190():
    error = ErrorDefinition(
        code='190',
        description="Child has not been looked after continuously for at least 12 months at 31 March but one or more "
                    "data items relating to children looked after for 12 months have been completed.",
        affected_fields=['CONVICTED', 'HEALTH_CHECK', 'IMMUNISATIONS', 'TEETH_CHECK', 'HEALTH_ASSESSMENT',
                         'SUBSTANCE_MISUSE', 'INTERVENTION_RECEIVED', 'INTERVENTION_OFFERED']
        ,  # AD1
    )

    def _validate(dfs):
        if (
                'OC2' not in dfs
                or 'Episodes' not in dfs
        ):
            return {}

        # add 'CONTINUOUSLY_LOOKED_AFTER' column
        oc2 = add_CLA_column(dfs, 'OC2')

        should_be_blank = ['CONVICTED', 'HEALTH_CHECK', 'IMMUNISATIONS', 'TEETH_CHECK', 'HEALTH_ASSESSMENT',
                           'SUBSTANCE_MISUSE', 'INTERVENTION_RECEIVED', 'INTERVENTION_OFFERED']

        mask = ~oc2['CONTINUOUSLY_LOOKED_AFTER'] & oc2[should_be_blank].notna().any(axis=1)
        error_locs = oc2[mask].index.to_list()

        return {'OC2': error_locs}

    return error, _validate


def validate_191():
    error = ErrorDefinition(
        code='191',
        description="Child has been looked after continuously for at least 12 months at 31 March but one or more "
                    "data items relating to children looked after for 12 months have been left blank.",
        affected_fields=['IMMUNISATIONS', 'TEETH_CHECK', 'HEALTH_ASSESSMENT', 'SUBSTANCE_MISUSE'],  # OC2
    )

    def _validate(dfs):
        if (
                'OC2' not in dfs
                or 'Episodes' not in dfs
        ):
            return {}

        # add 'CONTINUOUSLY_LOOKED_AFTER' column
        oc2 = add_CLA_column(dfs, 'OC2')

        should_be_present = ['IMMUNISATIONS', 'TEETH_CHECK', 'HEALTH_ASSESSMENT', 'SUBSTANCE_MISUSE']

        mask = oc2['CONTINUOUSLY_LOOKED_AFTER'] & oc2[should_be_present].isna().any(axis=1)
        error_locs = oc2[mask].index.to_list()

        return {'OC2': error_locs}

    return error, _validate


def validate_607():
    error = ErrorDefinition(
        code='607',
        description='Child ceased to be looked after in the year, but mother field has not been completed.',
        affected_fields=['DEC', 'REC', 'MOTHER', 'LS', 'SEX']
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'Episodes' not in dfs:
            return {}
        else:
            header = dfs['Header']
            episodes = dfs['Episodes']
            collection_start = dfs['metadata']['collection_start']
            collection_end = dfs['metadata']['collection_end']
            code_list = ['V3', 'V4']

            # convert to datetiime format
            episodes['DEC'] = pd.to_datetime(episodes['DEC'], format='%d/%m/%Y', errors='coerce')
            collection_start = pd.to_datetime(collection_start, format='%d/%m/%Y', errors='coerce')
            collection_end = pd.to_datetime(collection_end, format='%d/%m/%Y', errors='coerce')

            # prepare to merge
            episodes.reset_index(inplace=True)
            header.reset_index(inplace=True)

            merged = episodes.merge(header, on='CHILD', how='left', suffixes=['_eps', '_er'])

            # CEASED_TO_BE_LOOKED_AFTER = DEC is not null and REC is filled but not equal to X1
            CEASED_TO_BE_LOOKED_AFTER = merged['DEC'].notna() & ((merged['REC'] != 'X1') & merged['REC'].notna())
            # and <LS> not = ‘V3’ or ‘V4’
            check_LS = ~(merged['LS'].isin(code_list))
            # and <DEC> is in <CURRENT_COLLECTION_YEAR
            check_DEC = (collection_start <= merged['DEC']) & (merged['DEC'] <= collection_end)
            # Where <CEASED_TO_BE_LOOKED_AFTER> = ‘Y’, and <LS> not = ‘V3’ or ‘V4’ and <DEC> is in <CURRENT_COLLECTION_YEAR> and <SEX> = ‘2’ then <MOTHER> should be provided.
            mask = CEASED_TO_BE_LOOKED_AFTER & check_LS & check_DEC & (merged['SEX'] == '2') & (merged['MOTHER'].isna())
            header_error_locs = merged.loc[mask, 'index_er']
            eps_error_locs = merged.loc[mask, 'index_eps']
            return {'Episodes': eps_error_locs.tolist(), 'Header': header_error_locs.unique().tolist()}

    return error, _validate


def validate_210():
    error = ErrorDefinition(
        code='210',
        description='Children looked after for more than a week at 31 March should not have an unknown Unique Pupil Number (UPN) code of UN4.',
        affected_fields=['UPN', 'DECOM']
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'Episodes' not in dfs:
            return {}
        else:
            header = dfs['Header']
            episodes = dfs['Episodes']
            collection_end = dfs['metadata']['collection_end']
            # convert to datetime
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
            collection_end = pd.to_datetime(collection_end, format='%d/%m/%Y', errors='coerce')
            yr = collection_end.year
            reference_date = ref_date = pd.to_datetime('24/03/' + str(yr), format='%d/%m/%Y', errors='coerce')
            # prepare to merge
            episodes.reset_index(inplace=True)
            header.reset_index(inplace=True)
            # the logical way is to merge left on UPN but that will be a one to many merge and may not go as well as a many to one merge that we've been doing.
            merged = episodes.merge(header, on='CHILD', how='left', suffixes=['_eps', '_er'])
            # If <UPN> = 'UN4' then no episode <DECOM> must be >` = 24/03/YYYY Note: YYYY refers to the current collection year.
            mask = (merged['UPN'] == 'UN4') & (merged['DECOM'] >= reference_date)
            # error locations
            error_locs_header = merged.loc[mask, 'index_er']
            error_locs_eps = merged.loc[mask, 'index_eps']
            return {'Episodes': error_locs_eps.tolist(), 'Header': error_locs_header.unique().tolist()}

    return error, _validate


def validate_625():
  error = ErrorDefinition(
    code ='625',
    description = 'Date of birth of the first child is beyond the end of this reporting year or the date the child ceased to be looked after.',
    affected_fields = ['MC_DOB', 'DEC']
  )
  def _validate(dfs):
    if 'Episodes' not in dfs or 'Header' not in dfs:
      return {}
    else:
      episodes = dfs['Episodes']
      header = dfs['Header']
      collection_end = dfs['metadata']['collection_end']

      # datetime conversion
      collection_end = pd.to_datetime(collection_end, format='%d/%m/%Y', errors='coerce')
      header['MC_DOB'] = pd.to_datetime(header['MC_DOB'], format='%d/%m/%Y', errors='coerce')
      episodes['DEC'] = pd.to_datetime(episodes['DEC'], format='%d/%m/%Y', errors='coerce')
      # prepare to merge
      header.reset_index(inplace=True)
      episodes.reset_index(inplace=True)
      # latest episodes
      eps_last_indices = episodes.groupby('CHILD')['DEC'].idxmax()
      latest_episodes = episodes[episodes.index.isin(eps_last_indices)]
      merged = latest_episodes.merge(header, on='CHILD', how='left', suffixes=['_eps','_er'])
      # If provided <MC_DOB> must not be > <COLLECTION_END> or <DEC> of latest episode
      mask = (merged['MC_DOB']>collection_end) | (merged['MC_DOB']>merged['DEC'])
      header_error_locs = merged.loc[mask, 'index_er']
      eps_error_locs = merged.loc[mask, 'index_eps']
      return {'Header':header_error_locs.unique().tolist(), 'Episodes':eps_error_locs.tolist()}
  return error, _validate

def validate_1010():
    error = ErrorDefinition(
        code='1010',
        description='This child has no episodes loaded for current year even though there was an open episode of '
                    + 'care at the end of the previous year, and care leaver data has been entered.',
        affected_fields=['IN_TOUCH', 'ACTIV', 'ACCOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'Episodes_last' not in dfs or 'OC3' not in dfs:
            return {}

        else:
            episodes = dfs['Episodes']
            episodes_last = dfs['Episodes_last']
            oc3 = dfs['OC3']

            # convert DECOM to datetime, drop missing/invalid sort by CHILD then DECOM,
            episodes_last['DECOM'] = pd.to_datetime(episodes_last['DECOM'], format='%d/%m/%Y', errors='coerce')
            episodes_last = episodes_last.dropna(subset=['DECOM']).sort_values(['CHILD', 'DECOM'], ascending=True)

            # Keep only the final episode for each child (ie where the following row has a different CHILD value)
            episodes_last = episodes_last[
                episodes_last['CHILD'].shift(-1) != episodes_last['CHILD']
                ]
            # Keep only the final episodes that were still open
            episodes_last = episodes_last[episodes_last['DEC'].isna()]

            # The remaining children ought to have episode data in the current year if they are in OC3
            has_current_episodes = oc3['CHILD'].isin(episodes['CHILD'])
            has_open_episode_last = oc3['CHILD'].isin(episodes_last['CHILD'])

            error_mask = ~has_current_episodes & has_open_episode_last

            validation_error_locations = oc3.index[error_mask]

            return {'OC3': validation_error_locations.tolist()}

    return error, _validate


def validate_525():
    error = ErrorDefinition(
        code='525',
        description='A child for whom the decision to be placed for adoption has been reversed cannot be adopted during the year.',
        affected_fields=['DATE_PLACED_CEASED', 'DATE_INT', 'DATE_MATCH', 'FOSTER_CARE', 'NB_ADOPTR', 'SEX_ADOPTR',
                         'LS_ADOPTR']
    )

    def _validate(dfs):
        if 'PlacedAdoption' not in dfs or 'AD1' not in dfs:
            return {}
        else:
            placed_adoption = dfs['PlacedAdoption']
            ad1 = dfs['AD1']
            # prepare to merge
            placed_adoption.reset_index(inplace=True)
            ad1.reset_index(inplace=True)

            merged = placed_adoption.merge(ad1, on='CHILD', how='left', suffixes=['_placed', '_ad1'])
            # If <DATE_PLACED_CEASED> not Null, then <DATE_INT>; <DATE_MATCH>; <FOSTER_CARE>; <NB_ADOPTR>; <SEX_ADOPTR>; and <LS_ADOPTR> should not be provided
            mask = merged['DATE_PLACED_CEASED'].notna() & (
                    merged['DATE_INT'].notna() | merged['DATE_MATCH'].notna() | merged['FOSTER_CARE'].notna() |
                    merged['NB_ADOPTR'].notna() | merged['SEX_ADOPTR'].notna() | merged['LS_ADOPTR'].notna())
            # error locations
            pa_error_locs = merged.loc[mask, 'index_placed']
            ad_error_locs = merged.loc[mask, 'index_ad1']
            # return result
            return {'PlacedAdoption': pa_error_locs.tolist(), 'AD1': ad_error_locs.tolist()}

    return error, _validate


def validate_335():
    error = ErrorDefinition(
        code='335',
        description='The current foster value (0) suggests that child is not adopted by current foster carer, but last placement is A2, A3, or A5. Or the current foster value (1) suggests that child is adopted by current foster carer, but last placement is A1, A4 or A6.',
        affected_fields=['PLACE', 'FOSTER_CARE']
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'AD1' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            ad1 = dfs['AD1']

            # prepare to merge
            episodes.reset_index(inplace=True)
            ad1.reset_index(inplace=True)
            merged = episodes.merge(ad1, on='CHILD', how='left', suffixes=['_eps', '_ad1'])

            # Where <PL> = 'A2', 'A3' or 'A5' and <DEC> = 'E1', 'E11', 'E12' <FOSTER_CARE> should not be '0'; Where <PL> = ‘A1’, ‘A4’ or ‘A6’ and <REC> = ‘E1’, ‘E11’, ‘E12’ <FOSTER_CARE> should not be ‘1’.
            mask = (
                    merged['REC'].isin(['E1', 'E11', 'E12']) & (
                    (merged['PLACE'].isin(['A2', 'A3', 'A5']) & (merged['FOSTER_CARE'].astype(str) == '0'))
                    | (merged['PLACE'].isin(['A1', 'A4', 'A6']) & (merged['FOSTER_CARE'].astype(str) == '1'))
            )
            )
            eps_error_locs = merged.loc[mask, 'index_eps']
            ad1_error_locs = merged.loc[mask, 'index_ad1']

            # use .unique since join is many to one
            return {'Episodes': eps_error_locs.tolist(), 'AD1': ad1_error_locs.unique().tolist()}

    return error, _validate


def validate_215():
    error = ErrorDefinition(
        code='215',
        description='Child has care leaver information but one or more data items relating to children looked after for 12 months have been completed.',
        affected_fields=['IN_TOUCH', 'ACTIV', 'ACCOM', 'CONVICTED', 'HEALTH_CHECK', 'IMMUNISATIONS', 'TEETH_CHECK',
                         'HEALTH_ASSESSMENT', 'SUBSTANCE_MISUSE', 'INTERVENTION_RECEIVED', 'INTERVENTION_OFFERED']
    )

    def _validate(dfs):
        if 'OC3' not in dfs or 'OC2' not in dfs:
            return {}
        else:
            oc3 = dfs['OC3']
            oc2 = dfs['OC2']
            # prepare to merge
            oc3.reset_index(inplace=True)
            oc2.reset_index(inplace=True)
            merged = oc3.merge(oc2, on='CHILD', how='left', suffixes=['_3', '_2'])
            # If any of <IN_TOUCH>, <ACTIV> or <ACCOM> have been provided then <CONVICTED>; <HEALTH_CHECK>; <IMMUNISATIONS>; <TEETH_CHECK>; <HEALTH_ASSESSMENT>; <SUBSTANCE MISUSE>; <INTERVENTION_RECEIVED>; <INTERVENTION_OFFERED>; should not be provided
            mask = (merged['IN_TOUCH'].notna() | merged['ACTIV'].notna() | merged['ACCOM'].notna()) & (
                    merged['CONVICTED'].notna() | merged['HEALTH_CHECK'].notna() | merged['IMMUNISATIONS'].notna() |
                    merged['TEETH_CHECK'].notna() | merged['HEALTH_ASSESSMENT'].notna() | merged[
                        'SUBSTANCE_MISUSE'].notna() | merged['INTERVENTION_RECEIVED'].notna() | merged[
                        'INTERVENTION_OFFERED'].notna())

            # error locations
            oc3_error_locs = merged.loc[mask, 'index_3']
            oc2_error_locs = merged.loc[mask, 'index_2']
            return {'OC3': oc3_error_locs.tolist(), 'OC2': oc2_error_locs.tolist()}

    return error, _validate


def validate_399():
    error = ErrorDefinition(
        code='399',
        description='Mother field, review field or participation field are completed but '
                    + 'child is looked after under legal status V3 or V4.',
        affected_fields=['MOTHER', 'LS', 'REVIEW', 'REVIEW_CODE']
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'Header' not in dfs or 'Reviews' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            header = dfs['Header']
            reviews = dfs['Reviews']

            code_list = ['V3', 'V4']

            # prepare to merge
            episodes['index_eps'] = episodes.index
            header['index_hdr'] = header.index
            reviews['index_revs'] = reviews.index

            # merge
            merged = (episodes.merge(header, on='CHILD', how='left')
                      .merge(reviews, on='CHILD', how='left'))

            # If <LS> = 'V3' or 'V4' then <MOTHER>, <REVIEW> and <REVIEW_CODE> should not be provided
            mask = merged['LS'].isin(code_list) & (
                    merged['MOTHER'].notna() | merged['REVIEW'].notna() | merged['REVIEW_CODE'].notna())

            # Error locations
            eps_errors = merged.loc[mask, 'index_eps']
            header_errors = merged.loc[mask, 'index_hdr'].unique()
            revs_errors = merged.loc[mask, 'index_revs'].unique()

            return {'Episodes': eps_errors.tolist(),
                    'Header': header_errors.tolist(),
                    'Reviews': revs_errors.tolist()}

    return error, _validate


def validate_189():
    error = ErrorDefinition(
        code='189',
        description='Child is aged 17 years or over at the beginning of the year, but an Strengths and Difficulties '
                    + '(SDQ) score or a reason for no Strengths and Difficulties (SDQ) score has been completed.',
        affected_fields=['DOB', 'SDQ_SCORE', 'SDQ_REASON']
    )

    def _validate(dfs):
        if 'OC2' not in dfs:
            return {}
        else:
            oc2 = dfs['OC2']
            collection_start = dfs['metadata']['collection_start']

            # datetime format allows appropriate comparison between dates
            oc2['DOB'] = pd.to_datetime(oc2['DOB'], format='%d/%m/%Y', errors='coerce')
            collection_start = pd.to_datetime(collection_start, format='%d/%m/%Y', errors='coerce')

            # If <DOB> >17 years prior to <COLLECTION_START_DATE> then <SDQ_SCORE> and <SDQ_REASON> should not be provided
            mask = ((oc2['DOB'] + pd.offsets.DateOffset(years=17)) <= collection_start) & (
                    oc2['SDQ_REASON'].notna() | oc2['SDQ_SCORE'].notna())
            # That is, raise error if collection_start > DOB + 17years
            oc_error_locs = oc2.index[mask]
            return {'OC2': oc_error_locs.tolist()}

    return error, _validate


def validate_226():
    error = ErrorDefinition(
        code='226',
        description='Reason for placement change is not required.',
        affected_fields=['REASON_PLACE_CHANGE', 'PLACE']
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']

            code_list = ['T0', 'T1', 'T2', 'T3', 'T4']

            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')

            # create column to see previous REASON_PLACE_CHANGE
            episodes = episodes.sort_values(['CHILD', 'DECOM'])
            episodes['PREVIOUS_REASON'] = episodes.groupby('CHILD')['REASON_PLACE_CHANGE'].shift(1)
            # If <PL> = 'T0'; 'T1'; 'T2'; 'T3' or 'T4' then <REASON_PLACE_CHANGE> should be null in current episode and current episode - 1
            mask = episodes['PLACE'].isin(code_list) & (
                    episodes['REASON_PLACE_CHANGE'].notna() | episodes['PREVIOUS_REASON'].notna())

            # error locations
            error_locs = episodes.index[mask]
        return {'Episodes': error_locs.tolist()}

    return error, _validate


def validate_358():
    error = ErrorDefinition(
        code='358',
        description='Child with this legal status should not be under 10.',
        affected_fields=['DECOM', 'DOB', 'LS']
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'Header' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            header = dfs['Header']
            code_list = ['J1', 'J2', 'J3']

            # convert dates to datetime format
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
            header['DOB'] = pd.to_datetime(header['DOB'], format='%d/%m/%Y', errors='coerce')
            # prepare to merge
            episodes.reset_index(inplace=True)
            header.reset_index(inplace=True)
            merged = episodes.merge(header, on='CHILD', how='left', suffixes=['_eps', '_er'])

            # Where <LS> = ‘J1’ or ‘J2’ or ‘J3’ then <DOB> should <= to 10 years prior to <DECOM>
            mask = merged['LS'].isin(code_list) & (merged['DOB'] + pd.offsets.DateOffset(years=10) >= merged['DECOM'])
            # That is, raise error if DECOM <= DOB + 10years

            # error locations
            header_error_locs = merged.loc[mask, 'index_er']
            episode_error_locs = merged.loc[mask, 'index_eps']
            # one to many join implies use .unique on the 'one'
            return {'Episodes': episode_error_locs.tolist(), 'Header': header_error_locs.unique().tolist()}

    return error, _validate


def validate_407():
    error = ErrorDefinition(
        code='407',
        description='Reason episode ceased is Special Guardianship Order, but child has reached age 18.',
        affected_fields=['DEC', 'DOB', 'REC']
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'Header' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            header = dfs['Header']
            code_list = ['E45', 'E46', 'E47', 'E48']

            # convert dates to datetime format
            episodes['DEC'] = pd.to_datetime(episodes['DEC'], format='%d/%m/%Y', errors='coerce')
            header['DOB'] = pd.to_datetime(header['DOB'], format='%d/%m/%Y', errors='coerce')
            # prepare to merge
            episodes.reset_index(inplace=True)
            header.reset_index(inplace=True)
            merged = episodes.merge(header, on='CHILD', how='left', suffixes=['_eps', '_er'])

            # If <REC> = ‘E45’ or ‘E46’ or ‘E47’ or ‘E48’ then <DOB> must be < 18 years prior to <DEC>
            mask = merged['REC'].isin(code_list) & (merged['DOB'] + pd.offsets.DateOffset(years=18) < merged['DEC'])
            # That is, raise error if DEC > DOB + 10years

            # error locations
            header_error_locs = merged.loc[mask, 'index_er']
            episode_error_locs = merged.loc[mask, 'index_eps']
            # one to many join implies use .unique on the 'one'
            return {'Episodes': episode_error_locs.tolist(), 'Header': header_error_locs.unique().tolist()}

    return error, _validate


def validate_1007():
    error = ErrorDefinition(
        code='1007',
        description='Care leaver information is not required for 17- or 18-year olds who are still looked after.',
        affected_fields=['DEC', 'REC', 'DOB', 'IN_TOUCH', 'ACTIV', 'ACCOM']
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'OC3' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            oc3 = dfs['OC3']
            collection_end = dfs['metadata']['collection_end']

            # convert dates to datetime format
            oc3['DOB'] = pd.to_datetime(oc3['DOB'], format='%d/%m/%Y', errors='coerce')
            collection_end = pd.to_datetime(collection_end, format='%d/%m/%Y', errors='coerce')

            # prepare to merge
            episodes.reset_index(inplace=True)
            oc3.reset_index(inplace=True)
            merged = episodes.merge(oc3, on='CHILD', how='left', suffixes=['_eps', '_oc3'])

            # If <DOB> < 19 and >= to 17 years prior to <COLLECTION_END_DATE> and current episode <DEC> and or <REC> not provided then <IN_TOUCH>, <ACTIV> and <ACCOM> should not be provided
            check_age = (merged['DOB'] + pd.offsets.DateOffset(years=17) <= collection_end) & (
                    merged['DOB'] + pd.offsets.DateOffset(years=19) > collection_end)
            # That is, check that 17<=age<19
            check_dec_rec = merged['REC'].isna() | merged['DEC'].isna()
            # if either DEC or REC are absent
            mask = check_age & check_dec_rec & (
                    merged['IN_TOUCH'].notna() | merged['ACTIV'].notna() | merged['ACCOM'].notna())
            # Then raise an error if either IN_TOUCH, ACTIV, or ACCOM have been provided too

            # error locations
            oc3_error_locs = merged.loc[mask, 'index_oc3']
            episode_error_locs = merged.loc[mask, 'index_eps']
            # one to many join implies use .unique on the 'one'
            return {'Episodes': episode_error_locs.tolist(), 'OC3': oc3_error_locs.unique().tolist()}

    return error, _validate


def validate_442():
    error = ErrorDefinition(
        code='442',
        description='Unique Pupil Number (UPN) field is not completed.',
        affected_fields=['UPN']
    )

    def _validate(dfs):
        if ('Episodes' not in dfs) or ('Header' not in dfs):
            return {}
        else:
            episodes = dfs['Episodes']
            header = dfs['Header']

            episodes.reset_index(inplace=True)
            header.reset_index(inplace=True)

            code_list = ['V3', 'V4']

            # merge left on episodes to get all children for which episodes have been recorded even if they do not exist on the header.
            merged = episodes.merge(header, on=['CHILD'], how='left', suffixes=['_eps', '_er'])
            # Where any episode present, with an <LS> not = 'V3' or 'V4' then <UPN> must be provided
            mask = (~merged['LS'].isin(code_list)) & merged['UPN'].isna()
            episode_error_locs = merged.loc[mask, 'index_eps']
            header_error_locs = merged.loc[mask, 'index_er']

            return {'Episodes': episode_error_locs.tolist(),
                    # Select unique values since many episodes are joined to one header
                    # and multiple errors will be raised for the same index.
                    'Header': header_error_locs.dropna().unique().tolist()}

    return error, _validate


def validate_344():
    error = ErrorDefinition(
        code='344',
        description='The record shows the young person has died or returned home to live with parent(s) or someone with parental responsibility for a continuous period of 6 months or more, but activity and/or accommodation on leaving care have been completed.',
        affected_fields=['IN_TOUCH', 'ACTIV', 'ACCOM']
    )

    def _validate(dfs):
        if 'OC3' not in dfs:
            return {}
        else:
            oc3 = dfs['OC3']
            # If <IN_TOUCH> = 'DIED' or 'RHOM' then <ACTIV> and <ACCOM> should not be provided
            mask = ((oc3['IN_TOUCH'] == 'DIED') | (oc3['IN_TOUCH'] == 'RHOM')) & (
                    oc3['ACTIV'].notna() | oc3['ACCOM'].notna())
            error_locations = oc3.index[mask]
            return {'OC3': error_locations.to_list()}

    return error, _validate


def validate_345():
    error = ErrorDefinition(
        code='345',
        description='The data collection record shows the local authority is in touch with this young person, but activity and/or accommodation data items are zero.',
        affected_fields=['IN_TOUCH', 'ACTIV', 'ACCOM']
    )

    def _validate(dfs):
        if 'OC3' not in dfs:
            return {}
        else:
            oc3 = dfs['OC3']
            # If <IN_TOUCH> = 'Yes' then <ACTIV> and <ACCOM> must be provided
            mask = (oc3['IN_TOUCH'] == 'YES') & (oc3['ACTIV'].isna() | oc3['ACCOM'].isna())
            error_locations = oc3.index[mask]
            return {'OC3': error_locations.to_list()}

    return error, _validate


def validate_384():
    error = ErrorDefinition(
        code='384',
        description='A child receiving respite care cannot be in a long-term foster placement ',
        affected_fields=['PLACE', 'LS']
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            # Where <LS> = 'V3' or 'V4' then <PL> must not be 'U1' or 'U4'
            mask = ((episodes['LS'] == 'V3') | (episodes['LS'] == 'V4')) & (
                    (episodes['PLACE'] == 'U1') | (episodes['PLACE'] == 'U4'))
            error_locations = episodes.index[mask]
            return {'Episodes': error_locations.to_list()}

    return error, _validate


def validate_390():
    error = ErrorDefinition(
        code='390',
        description='Reason episode ceased is adopted but child has not been previously placed for adoption.',
        affected_fields=['PLACE', 'REC']
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            # If <REC> = 'E11' or 'E12' then <PL> must be one of 'A3', 'A4', 'A5' or 'A6'
            mask = ((episodes['REC'] == 'E11') | (episodes['REC'] == 'E12')) & ~(
                    (episodes['PLACE'] == 'A3') | (episodes['PLACE'] == 'A4') | (episodes['PLACE'] == 'A5') | (
                    episodes['PLACE'] == 'A6'))
            error_locations = episodes.index[mask]
            return {'Episodes': error_locations.to_list()}

    return error, _validate


def validate_378():
    error = ErrorDefinition(
        code='378',
        description='A child who is placed with parent(s) cannot be looked after under a single period of accommodation under Section 20 of the Children Act 1989.',
        affected_fields=['PLACE', 'LS']
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            # the & sign supercedes the ==, so brackets are necessary here
            mask = (episodes['PLACE'] == 'P1') & (episodes['LS'] == 'V2')
            error_locations = episodes.index[mask]
            return {'Episodes': error_locations.to_list()}

    return error, _validate


def validate_398():
    error = ErrorDefinition(
        code='398',
        description='Distance field completed but child looked after under legal status V3 or V4.',
        affected_fields=['LS', 'HOME_POST', 'PL_POST']
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            mask = ((episodes['LS'] == 'V3') | (episodes['LS'] == 'V4')) & (
                    episodes['HOME_POST'].notna() | episodes['PL_POST'].notna())
            error_locations = episodes.index[mask]
            return {'Episodes': error_locations.to_list()}

    return error, _validate


def validate_451():
    error = ErrorDefinition(
        code='451',
        description='Child is still freed for adoption, but freeing orders could not be applied for since 30 December 2005.',
        affected_fields=['DEC', 'REC', 'LS']
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            mask = episodes['DEC'].isna() & episodes['REC'].isna() & (episodes['LS'] == 'D1')
            error_locations = episodes.index[mask]
            return {'Episodes': error_locations.to_list()}

    return error, _validate


def validate_519():
    error = ErrorDefinition(
        code='519',
        description='Data entered on the legal status of adopters shows civil partnership couple, but data entered on genders of adopters does not show it as a couple.',
        affected_fields=['LS_ADOPTR', 'SEX_ADOPTR']
    )

    def _validate(dfs):
        if 'AD1' not in dfs:
            return {}
        else:
            ad1 = dfs['AD1']
            mask = (ad1['LS_ADOPTR'] == 'L2') & (
                        (ad1['SEX_ADOPTR'] != 'MM') & (ad1['SEX_ADOPTR'] != 'FF') & (ad1['SEX_ADOPTR'] != 'MF'))
            error_locations = ad1.index[mask]
            return {'AD1': error_locations.to_list()}

    return error, _validate


def validate_520():
    error = ErrorDefinition(
        code='520',
        description='Data entry on the legal status of adopters shows different gender married couple but data entry on genders of adopters shows it as a same gender couple.',
        affected_fields=['LS_ADOPTR', 'SEX_ADOPTR']
    )

    def _validate(dfs):
        if 'AD1' not in dfs:
            return {}
        else:
            ad1 = dfs['AD1']
            # check condition
            mask = (ad1['LS_ADOPTR'] == 'L11') & (ad1['SEX_ADOPTR'] != 'MF')
            error_locations = ad1.index[mask]
            return {'AD1': error_locations.to_list()}

    return error, _validate


def validate_522():
    error = ErrorDefinition(
        code='522',
        description='Date of decision that the child should be placed for adoption must be on or before the date that a child should no longer be placed for adoption.',
        affected_fields=['DATE_PLACED', 'DATE_PLACED_CEASED']
    )

    def _validate(dfs):
        if 'PlacedAdoption' not in dfs:
            return {}
        else:
            placed_adoption = dfs['PlacedAdoption']
            # Convert to datetimes
            placed_adoption['DATE_PLACED_CEASED'] = pd.to_datetime(placed_adoption['DATE_PLACED_CEASED'],
                                                                   format='%d/%m/%Y', errors='coerce')
            placed_adoption['DATE_PLACED'] = pd.to_datetime(placed_adoption['DATE_PLACED'], format='%d/%m/%Y',
                                                            errors='coerce')
            # Boolean mask
            mask = placed_adoption['DATE_PLACED_CEASED'] < placed_adoption['DATE_PLACED']

            error_locations = placed_adoption.index[mask]
            return {'PlacedAdoption': error_locations.to_list()}

    return error, _validate


def validate_563():
    error = ErrorDefinition(
        code='563',
        description='The child should no longer be placed for adoption but the date of the decision that the child should be placed for adoption is blank',
        affected_fields=['DATE_PLACED', 'REASON_PLACED_CEASED', 'DATE_PLACED_CEASED'],
    )

    def _validate(dfs):
        if 'PlacedAdoption' not in dfs:
            return {}
        else:
            placed_adoption = dfs['PlacedAdoption']
            mask = placed_adoption['REASON_PLACED_CEASED'].notna() & placed_adoption['DATE_PLACED_CEASED'].notna() & \
                   placed_adoption['DATE_PLACED'].isna()
            error_locations = placed_adoption.index[mask]
            return {'PlacedAdoption': error_locations.to_list()}

    return error, _validate


def validate_544():
    error = ErrorDefinition(
        code='544',
        description="Any child who has conviction information completed must also have immunisation, teeth check, health assessment and substance misuse problem identified fields completed.",
        affected_fields=['CONVICTED', 'IMMUNISATIONS', 'TEETH_CHECK', 'HEALTH_ASSESSMENT', 'SUBSTANCE_MISUSE'],
    )

    def _validate(dfs):
        if 'OC2' not in dfs:
            return {}
        else:
            oc2 = dfs['OC2']

            convict = oc2['CONVICTED'].astype(str) == '1'
            immunisations = oc2['IMMUNISATIONS'].isna()
            teeth_ck = oc2['TEETH_CHECK'].isna()
            health_ass = oc2['HEALTH_ASSESSMENT'].isna()
            sub_misuse = oc2['SUBSTANCE_MISUSE'].isna()

            error_mask = convict & (immunisations | teeth_ck | health_ass | sub_misuse)
            validation_error_locations = oc2.index[error_mask]

            return {'OC2': validation_error_locations.to_list()}

    return error, _validate


def validate_634():
    error = ErrorDefinition(
        code='634',
        description='There are entries for previous permanence options, but child has not started to be looked after from 1 April 2016 onwards.',
        affected_fields=['LA_PERM', 'PREV_PERM', 'DATE_PERM', 'DECOM']
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'PrevPerm' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            prevperm = dfs['PrevPerm']
            collection_start = dfs['metadata']['collection_start']
            # convert date field to appropriate format
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
            collection_start = pd.to_datetime(collection_start, format='%d/%m/%Y', errors='coerce')
            # the maximum date has the highest possibility of satisfying the condition
            episodes['LAST_DECOM'] = episodes.groupby('CHILD')['DECOM'].transform('max')

            # prepare to merge
            episodes.reset_index(inplace=True)
            prevperm.reset_index(inplace=True)
            merged = prevperm.merge(episodes, on='CHILD', how='left', suffixes=['_prev', '_eps'])
            # If <PREV_PERM> or <LA_PERM> or <DATE_PERM> provided, then at least 1 episode must have a <DECOM> later than 01/04/2016
            mask = (merged['PREV_PERM'].notna() | merged['DATE_PERM'].notna() | merged['LA_PERM'].notna()) & (
                    merged['LAST_DECOM'] < collection_start)
            eps_error_locs = merged.loc[mask, 'index_eps']
            prevperm_error_locs = merged.loc[mask, 'index_prev']

            # return {'PrevPerm':prevperm_error_locs}
            return {'Episodes': eps_error_locs.unique().tolist(), 'PrevPerm': prevperm_error_locs.unique().tolist()}

    return error, _validate


def validate_158():
    error = ErrorDefinition(
        code='158',
        description='If a child has been recorded as receiving an intervention for their substance misuse problem, then the additional item on whether an intervention was offered should be left blank.',
        affected_fields=['INTERVENTION_RECEIVED', 'INTERVENTION_OFFERED'],
    )

    def _validate(dfs):
        if 'OC2' not in dfs:
            return {}

        else:
            oc2 = dfs['OC2']

            error_mask = oc2['INTERVENTION_RECEIVED'].astype(str).eq('1') & oc2['INTERVENTION_OFFERED'].notna()

            error_locations = oc2.index[error_mask]

            return {'OC2': error_locations.tolist()}

    return error, _validate


def validate_133():
    error = ErrorDefinition(
        code='133',
        description='Data entry for accommodation after leaving care is invalid. If reporting on a childs accommodation after leaving care the data entry must be valid',
        affected_fields=['ACCOM'],
    )

    def _validate(dfs):
        if 'OC3' not in dfs:
            return {}

        else:
            oc3 = dfs['OC3']
            valid_codes = ['B1', 'B2', 'C1', 'C2', 'D1', 'D2', 'E1', 'E2', 'G1', 'G2', 'H1', 'H2', 'K1', 'K2', 'R1',
                           'R2', 'S2', 'T1', 'T2', 'U1', 'U2', 'V1', 'V2', 'W1', 'W2', 'X2', 'Y1', 'Y2', 'Z1', 'Z2',
                           '0']

            error_mask = ~oc3['ACCOM'].isna() & ~oc3['ACCOM'].isin(valid_codes)

            error_locations = oc3.index[error_mask]

            return {'OC3': error_locations.tolist()}

    return error, _validate


def validate_565():
    error = ErrorDefinition(
        code='565',
        description='The date that the child started to be missing or away from placement without authorisation has been completed but whether the child was missing or away from placement without authorisation has not been completed.',
        affected_fields=['MISSING', 'MIS_START']
    )

    def _validate(dfs):
        if 'Missing' not in dfs:
            return {}
        else:
            missing = dfs['Missing']
            mask = missing['MIS_START'].notna() & missing['MISSING'].isna()
            error_locations = missing.index[mask]
            return {'Missing': error_locations.to_list()}

    return error, _validate


def validate_433():
    error = ErrorDefinition(
        code='433',
        description='The reason for new episode suggests that this is a continuation episode, but the episode does not start on the same day as the last episode finished.',
        affected_fields=['RNE', 'DECOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            episodes['DECOM_dt'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
            episodes['DEC_dt'] = pd.to_datetime(episodes['DEC'], format='%d/%m/%Y', errors='coerce')

            episodes['original_index'] = episodes.index
            episodes.sort_values(['CHILD', 'DECOM_dt', 'DEC_dt'], inplace=True)
            episodes[['PREVIOUS_DEC', 'PREVIOUS_CHILD']] = episodes[['DEC', 'CHILD']].shift(1)

            rne_is_ongoing = episodes['RNE'].str.upper().astype(str).isin(['P', 'L', 'T', 'U', 'B'])
            date_mismatch = episodes['PREVIOUS_DEC'] != episodes['DECOM']
            missing_date = episodes['PREVIOUS_DEC'].isna() | episodes['DECOM'].isna()
            same_child = episodes['PREVIOUS_CHILD'] == episodes['CHILD']

            error_mask = rne_is_ongoing & (date_mismatch | missing_date) & same_child

            error_locations = episodes['original_index'].loc[error_mask].sort_values()

            return {'Episodes': error_locations.to_list()}

    return error, _validate


def validate_437():
    error = ErrorDefinition(
        code='437',
        description='Reason episode ceased is child has died or is aged 18 or over but there are further episodes.',
        affected_fields=['REC'],
    )

    # !# potential false negatives, as this only operates on the current year's data
    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']

            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')

            episodes.sort_values(['CHILD', 'DECOM'], inplace=True)
            episodes[['NEXT_DECOM', 'NEXT_CHILD']] = episodes[['DECOM', 'CHILD']].shift(-1)

            # drop rows with missing DECOM as invalid/missing values can lead to errors
            episodes = episodes.dropna(subset=['DECOM'])

            ceased_e2_e15 = episodes['REC'].str.upper().astype(str).isin(['E2', 'E15'])
            has_later_episode = episodes['CHILD'] == episodes['NEXT_CHILD']

            error_mask = ceased_e2_e15 & has_later_episode

            error_locations = episodes.index[error_mask]

            return {'Episodes': error_locations.to_list()}

    return error, _validate


def validate_547():
    error = ErrorDefinition(
        code='547',
        description="Any child who has health promotion information completed must also have immunisation, teeth check, health assessment and substance misuse problem identified fields completed.",
        affected_fields=['HEALTH_CHECK', 'IMMUNISATIONS', 'TEETH_CHECK', 'HEALTH_ASSESSMENT', 'SUBSTANCE_MISUSE'],
    )

    def _validate(dfs):
        if 'OC2' not in dfs:
            return {}
        else:
            oc2 = dfs['OC2']

            healthck = oc2['HEALTH_CHECK'].astype(str) == '1'
            immunisations = oc2['IMMUNISATIONS'].isna()
            teeth_ck = oc2['TEETH_CHECK'].isna()
            health_ass = oc2['HEALTH_ASSESSMENT'].isna()
            sub_misuse = oc2['SUBSTANCE_MISUSE'].isna()

            error_mask = healthck & (immunisations | teeth_ck | health_ass | sub_misuse)
            validation_error_locations = oc2.index[error_mask]

            return {'OC2': validation_error_locations.to_list()}

    return error, _validate


def validate_635():
    error = ErrorDefinition(
        code='635',
        description='There are entries for date of order and local authority code where previous permanence option was arranged but previous permanence code is Z1',
        affected_fields=['LA_PERM', 'DATE_PERM', 'PREV_PERM']
    )

    def _validate(dfs):
        if 'PrevPerm' not in dfs:
            return {}
        else:
            prev_perm = dfs['PrevPerm']
            # raise and error if either LA_PERM or DATE_PERM are present, yet PREV_PERM is absent.
            mask = ((prev_perm['LA_PERM'].notna() | prev_perm['DATE_PERM'].notna()) & prev_perm['PREV_PERM'].isna())

            error_locations = prev_perm.index[mask]
        return {'PrevPerm': error_locations.to_list()}

    return error, _validate


def validate_550():
    error = ErrorDefinition(
        code='550',
        description='A placement provider code of PR0 can only be associated with placement P1.',
        affected_fields=['PLACE', 'PLACE_PROVIDER'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']

            mask = (episodes['PLACE'] != 'P1') & episodes['PLACE_PROVIDER'].eq('PR0')

            validation_error_locations = episodes.index[mask]
            return {'Episodes': validation_error_locations.tolist()}

    return error, _validate


def validate_217():
    error = ErrorDefinition(
        code='217',
        description='Children who are placed for adoption with current foster carers (placement types A3 or A5) must have a reason for new episode of S, T or U.',
        affected_fields=['PLACE', 'DECOM', 'RNE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
            max_decom_allowed = pd.to_datetime('01/04/2015', format='%d/%m/%Y', errors='coerce')
            reason_new_ep = ['S', 'T', 'U']
            place_codes = ['A3', 'A5']

            mask = (episodes['PLACE'].isin(place_codes) & (episodes['DECOM'] >= max_decom_allowed)) & ~episodes[
                'RNE'].isin(reason_new_ep)

            validation_error_mask = mask
            validation_error_locations = episodes.index[validation_error_mask]

            return {'Episodes': validation_error_locations.tolist()}

    return error, _validate


def validate_518():
    error = ErrorDefinition(
        code='518',
        description='If reporting legal status of adopters is L4 then the genders of adopters should be coded as MM or FF. MM = the adopting couple are both males. FF = the adopting couple are both females.',
        affected_fields=['LS_ADOPTR', 'SEX_ADOPTR'],
    )

    def _validate(dfs):
        if 'AD1' not in dfs:
            return {}

        else:
            AD1 = dfs['AD1']

            error_mask = AD1['LS_ADOPTR'].eq('L4') & ~AD1['SEX_ADOPTR'].isin(['MM', 'FF'])

            error_locations = AD1.index[error_mask]

            return {'AD1': error_locations.tolist()}

    return error, _validate


def validate_517():
    error = ErrorDefinition(
        code='517',
        description='If reporting legal status of adopters is L3 then the genders of adopters should be coded as MF. MF = the adopting couple are male and female.',
        affected_fields=['LS_ADOPTR', 'SEX_ADOPTR'],
    )

    def _validate(dfs):
        if 'AD1' not in dfs:
            return {}

        else:
            AD1 = dfs['AD1']

            error_mask = AD1['LS_ADOPTR'].eq('L3') & ~AD1['SEX_ADOPTR'].isin(['MF'])

            error_locations = AD1.index[error_mask]

            return {'AD1': error_locations.tolist()}

    return error, _validate


def validate_558():
    error = ErrorDefinition(
        code='558',
        description='If a child has been adopted, then the decision to place them for adoption has not been disrupted and the date of the decision that a child should no longer be placed for adoption should be left blank. if the REC code is either E11 or E12 then the DATE PLACED CEASED date should not be provided',
        affected_fields=['DATE_PLACED_CEASED', 'REC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'PlacedAdoption' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            placedAdoptions = dfs['PlacedAdoption']

            episodes = episodes.reset_index()

            rec_codes = ['E11', 'E12']

            placeEpisodes = episodes[episodes['REC'].isin(rec_codes)]

            merged = placeEpisodes.merge(placedAdoptions, how='left', on='CHILD').set_index('index')

            episodes_with_errors = merged[merged['DATE_PLACED_CEASED'].notna()]

            error_mask = episodes.index.isin(episodes_with_errors.index)

            error_locations = episodes.index[error_mask]

            return {'Episodes': error_locations.to_list()}

    return error, _validate


def validate_453():
    error = ErrorDefinition(
        code='453',
        description='Contradiction between placement distance in the last episode of the previous year and in the first episode of the current year.',
        affected_fields=['PL_DISTANCE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        if 'Episodes_last' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            episodes_last = dfs['Episodes_last']

            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
            episodes_last['DECOM'] = pd.to_datetime(episodes_last['DECOM'], format='%d/%m/%Y', errors='coerce')
            episodes['PL_DISTANCE'] = pd.to_numeric(episodes['PL_DISTANCE'], errors='coerce')
            episodes_last['PL_DISTANCE'] = pd.to_numeric(episodes_last['PL_DISTANCE'], errors='coerce')

            # drop rows with missing DECOM before finding idxmin/max, as invalid/missing values can lead to errors
            episodes = episodes.dropna(subset=['DECOM'])
            episodes_last = episodes_last.dropna(subset=['DECOM'])

            episodes_min = episodes.groupby('CHILD')['DECOM'].idxmin()
            episodes_last_max = episodes_last.groupby('CHILD')['DECOM'].idxmax()

            episodes = episodes[episodes.index.isin(episodes_min)]
            episodes_last = episodes_last[episodes_last.index.isin(episodes_last_max)]

            episodes_merged = episodes.reset_index().merge(episodes_last, how='left', on=['CHILD'],
                                                           suffixes=('', '_last'), indicator=True).set_index('index')

            in_both_years = episodes_merged['_merge'] == 'both'
            same_rne = episodes_merged['RNE'] == episodes_merged['RNE_last']
            last_year_open = episodes_merged['DEC_last'].isna()
            different_pl_dist = abs(episodes_merged['PL_DISTANCE'] - episodes_merged['PL_DISTANCE_last']) >= 0.2

            error_mask = in_both_years & same_rne & last_year_open & different_pl_dist

            validation_error_locations = episodes.index[error_mask]

            return {'Episodes': validation_error_locations.tolist()}

    return error, _validate


def validate_516():
    error = ErrorDefinition(
        code='516',
        description='The episode data submitted for this child does not show that he/she was with their former foster carer(s) during the year.If the code in the reason episode ceased is E45 or E46 the child must have a placement code of U1 to U6.',
        affected_fields=['REC', 'PLACE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}

        else:
            episodes = dfs['Episodes']
            place_codes = ['U1', 'U2', 'U3', 'U4', 'U5', 'U6']
            rec_codes = ['E45', 'E46']

            error_mask = episodes['REC'].isin(rec_codes) & ~episodes['PLACE'].isin(place_codes)

            validation_error_locations = episodes.index[error_mask]

            return {'Episodes': validation_error_locations.tolist()}

    return error, _validate


def validate_511():
    error = ErrorDefinition(
        code='511',
        description='If reporting that the number of person(s) adopting the looked after child is two adopters then the code should only be MM, FF or MF. MM = the adopting couple are both males; FF = the adopting couple are both females; MF = The adopting couple are male and female.',
        affected_fields=['NB_ADOPTR', 'SEX_ADOPTR'],
    )

    def _validate(dfs):
        if 'AD1' not in dfs:
            return {}

        else:
            AD1 = dfs['AD1']

            mask = AD1['NB_ADOPTR'].astype(str).eq('2') & AD1['SEX_ADOPTR'].isin(['M1', 'F1'])

            validation_error_mask = mask
            validation_error_locations = AD1.index[validation_error_mask]

            return {'AD1': validation_error_locations.tolist()}

    return error, _validate


def validate_524():
    error = ErrorDefinition(
        code='524',
        description='If reporting legal status of adopters is L12 then the genders of adopters should be coded as MM or FF. MM = the adopting couple are both males. FF = the adopting couple are both females',
        affected_fields=['LS_ADOPTR', 'SEX_ADOPTR'],
    )

    def _validate(dfs):
        if 'AD1' not in dfs:
            return {}

        else:
            AD1 = dfs['AD1']

            error_mask = AD1['LS_ADOPTR'].eq('L12') & ~AD1['SEX_ADOPTR'].isin(['MM', 'FF'])

            error_locations = AD1.index[error_mask]

            return {'AD1': error_locations.tolist()}

    return error, _validate


def validate_441():
    error = ErrorDefinition(
        code='441',
        description='Participation method indicates child was 4 years old or over at the time of the review, but the date of birth and review date indicates the child was under 4 years old.',
        affected_fields=['DOB', 'REVIEW', 'REVIEW_CODE'],
    )

    def _validate(dfs):
        if 'Reviews' not in dfs:
            return {}
        else:
            reviews = dfs['Reviews']
            reviews['DOB'] = pd.to_datetime(reviews['DOB'], format='%d/%m/%Y', errors='coerce')
            reviews['REVIEW'] = pd.to_datetime(reviews['REVIEW'], format='%d/%m/%Y', errors='coerce')
            reviews = reviews.dropna(subset=['REVIEW', 'DOB'])

            mask = reviews['REVIEW_CODE'].isin(['PN1', 'PN2', 'PN3', 'PN4', 'PN5', 'PN6', 'PN7']) & (
                    reviews['REVIEW'] < reviews['DOB'] + pd.offsets.DateOffset(years=4))

            validation_error_mask = mask

            validation_error_locations = reviews.index[validation_error_mask]

            return {'Reviews': validation_error_locations.tolist()}

    return error, _validate


def validate_184():
    error = ErrorDefinition(
        code='184',
        description='Date of decision that a child should be placed for adoption is before the child was born.',
        affected_fields=['DATE_PLACED',  # PlacedAdoptino
                         'DOB'],  # Header
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'PlacedAdoption' not in dfs:
            return {}
        else:
            child_record = dfs['Header']
            placed_for_adoption = dfs['PlacedAdoption']

            all_data = (placed_for_adoption
                        .reset_index()
                        .merge(child_record, how='left', on='CHILD', suffixes=[None, '_P4A']))

            all_data['DATE_PLACED'] = pd.to_datetime(all_data['DATE_PLACED'], format='%d/%m/%Y', errors='coerce')
            all_data['DOB'] = pd.to_datetime(all_data['DOB'], format='%d/%m/%Y', errors='coerce')

            mask = (all_data['DATE_PLACED'] >= all_data['DOB']) | all_data['DATE_PLACED'].isna()

            validation_error = ~mask

            validation_error_locations = all_data[validation_error]['index'].unique()

            return {'PlacedAdoption': validation_error_locations.tolist()}

    return error, _validate


def validate_612():
    error = ErrorDefinition(
        code='612',
        description="Date of birth field has been completed but mother field indicates child is not a mother.",
        affected_fields=['SEX', 'MOTHER', 'MC_DOB'],
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}
        else:
            header = dfs['Header']

            error_mask = (
                    ((header['MOTHER'].astype(str) == '0') | header['MOTHER'].isna())
                    & (header['SEX'].astype(str) == '2')
                    & header['MC_DOB'].notna()
            )

            validation_error_locations = header.index[error_mask]

            return {'Header': validation_error_locations.tolist()}

    return error, _validate


def validate_552():
    """
  This error checks that the first adoption episode is after the last decision !
  If there are multiple of either there may be unexpected results !
  """

    error = ErrorDefinition(
        code="552",
        description="Date of Decision to place a child for adoption should be on or prior to the date that the child was placed for adoption.",
        # Field that defines date of decision to place a child for adoption is DATE_PLACED and the start of adoption is defined by DECOM with 'A' placement types.
        affected_fields=['DATE_PLACED', 'DECOM'],
    )

    def _validate(dfs):
        if ('PlacedAdoption' not in dfs) or ('Episodes' not in dfs):
            return {}
        else:
            # get the required datasets
            placed_adoption = dfs['PlacedAdoption']
            episodes = dfs['Episodes']
            # keep index values so that they stay the same when needed later on for error locations
            placed_adoption.reset_index(inplace=True)
            episodes.reset_index(inplace=True)

            adoption_eps = episodes[episodes['PLACE'].isin(['A3', 'A4', 'A5', 'A6'])].copy()
            # find most recent adoption decision
            placed_adoption['DATE_PLACED'] = pd.to_datetime(placed_adoption['DATE_PLACED'], format='%d/%m/%Y',
                                                            errors='coerce')
            # remove rows where either of the required values have not been filled.
            placed_adoption = placed_adoption[placed_adoption['DATE_PLACED'].notna()]

            placed_adoption_inds = placed_adoption.groupby('CHILD')['DATE_PLACED'].idxmax(skipna=True)
            last_decision = placed_adoption.loc[placed_adoption_inds]

            # first time child started adoption
            adoption_eps["DECOM"] = pd.to_datetime(adoption_eps['DECOM'], format='%d/%m/%Y', errors='coerce')
            adoption_eps = adoption_eps[adoption_eps['DECOM'].notna()]

            adoption_eps_inds = adoption_eps.groupby('CHILD')['DECOM'].idxmin(skipna=True)
            # full information of first adoption
            first_adoption = adoption_eps.loc[adoption_eps_inds]

            # date of decision and date of start of adoption (DECOM) have to be put in one table
            merged = first_adoption.merge(last_decision, on=['CHILD'], how='left', suffixes=['_EP', '_PA'])

            # check to see if date of decision to place is less than or equal to date placed.
            decided_after_placed = merged["DECOM"] < merged["DATE_PLACED"]

            # find the corresponding location of error values per file.
            episode_error_locs = merged.loc[decided_after_placed, 'index_EP']
            placedadoption_error_locs = merged.loc[decided_after_placed, 'index_PA']

            return {"PlacedAdoption": placedadoption_error_locs.to_list(), "Episodes": episode_error_locs.to_list()}

    return error, _validate


def validate_551():
    error = ErrorDefinition(
        code='551',
        description='Child has been placed for adoption but there is no date of the decision that the child should be placed for adoption.',
        affected_fields=['DATE_PLACED', 'PLACE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'PlacedAdoption' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            placedAdoptions = dfs['PlacedAdoption']

            episodes = episodes.reset_index()

            place_codes = ['A3', 'A4', 'A5', 'A6']

            placeEpisodes = episodes[episodes['PLACE'].isin(place_codes)]

            merged = placeEpisodes.merge(placedAdoptions, how='left', on='CHILD').set_index('index')

            episodes_with_errors = merged[merged['DATE_PLACED'].isna()]

            error_mask = episodes.index.isin(episodes_with_errors.index)

            error_locations = episodes.index[error_mask]

            return {'Episodes': error_locations.to_list()}

    return error, _validate


def validate_557():
    error = ErrorDefinition(
        code='557',
        description="Child for whom the decision was made that they should be placed for adoption has left care " +
                    "but was not adopted and information on the decision that they should no longer be placed for " +
                    "adoption items has not been completed.",
        affected_fields=['DATE_PLACED_CEASED', 'REASON_PLACED_CEASED',  # PlacedAdoption
                         'PLACE', 'LS', 'REC'],  # Episodes
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        if 'PlacedAdoption' not in dfs:
            return {}
        else:
            eps = dfs['Episodes']
            placed = dfs['PlacedAdoption']

            eps = eps.reset_index()
            placed = placed.reset_index()

            child_placed = eps['PLACE'].isin(['A3', 'A4', 'A5', 'A6'])
            order_granted = eps['LS'].isin(['D1', 'E1'])
            not_adopted = ~eps['REC'].isin(['E11', 'E12']) & eps['REC'].notna() & (eps['REC'] != 'X1')

            placed['ceased_incomplete'] = (
                    placed['DATE_PLACED_CEASED'].isna() | placed['REASON_PLACED_CEASED'].isna()
            )

            eps = eps[(child_placed | order_granted) & not_adopted]

            eps = eps.merge(placed, on='CHILD', how='left', suffixes=['_EP', '_PA'], indicator=True)

            eps = eps[(eps['_merge'] == 'left_only') | eps['ceased_incomplete']]

            EP_errors = eps['index_EP']
            PA_errors = eps['index_PA'].dropna()

            return {
                'Episodes': EP_errors.to_list(),
                'PlacedAdoption': PA_errors.to_list(),
            }

    return error, _validate


def validate_207():
    error = ErrorDefinition(
        code='207',
        description='Mother status for the current year disagrees with the mother status already recorded for this child.',
        affected_fields=['MOTHER'],
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'Header_last' not in dfs:
            return {}
        else:
            header = dfs['Header']
            header_last = dfs['Header_last']

            header_merged = header.reset_index().merge(header_last, how='left', on=['CHILD'], suffixes=('', '_last'),
                                                       indicator=True).set_index('index')

            in_both_years = header_merged['_merge'] == 'both'
            mother_is_different = header_merged['MOTHER'].astype(str) != header_merged['MOTHER_last'].astype(str)
            mother_was_true = header_merged['MOTHER_last'].astype(str) == '1'

            error_mask = in_both_years & mother_is_different & mother_was_true

            error_locations = header.index[error_mask]

            return {'Header': error_locations.to_list()}

    return error, _validate


def validate_523():
    error = ErrorDefinition(
        code='523',
        description="Date of decision that the child should be placed for adoption should be the same date as the decision that adoption is in the best interest (date should be placed).",
        affected_fields=['DATE_PLACED', 'DATE_INT'],
    )

    def _validate(dfs):
        if ("AD1" not in dfs) or ("PlacedAdoption" not in dfs):
            return {}
        else:
            placed_adoption = dfs["PlacedAdoption"]
            ad1 = dfs["AD1"]
            # keep initial index values to be reused for locating errors later on.
            placed_adoption.reset_index(inplace=True)
            ad1.reset_index(inplace=True)

            # convert to datetime to enable comparison
            placed_adoption['DATE_PLACED'] = pd.to_datetime(placed_adoption['DATE_PLACED'], format="%d/%m/%Y",
                                                            errors='coerce')
            ad1["DATE_INT"] = pd.to_datetime(ad1['DATE_INT'], format='%d/%m/%Y', errors='coerce')

            # drop rows where either of the required values have not been filled.
            placed_adoption = placed_adoption[placed_adoption["DATE_PLACED"].notna()]
            ad1 = ad1[ad1["DATE_INT"].notna()]

            # bring corresponding values together from both dataframes
            merged_df = placed_adoption.merge(ad1, on=['CHILD'], how='inner', suffixes=["_AD", "_PA"])
            # find error values
            different_dates = merged_df['DATE_INT'] != merged_df['DATE_PLACED']
            # map error locations to corresponding indices
            pa_error_locations = merged_df.loc[different_dates, 'index_PA']
            ad1_error_locations = merged_df.loc[different_dates, 'index_AD']

            return {"PlacedAdoption": pa_error_locations.to_list(), "AD1": ad1_error_locations.to_list()}

    return error, _validate


def validate_3001():
    error = ErrorDefinition(
        code='3001',
        description='Where care leavers information is being returned for a young person around their 17th birthday, the accommodation cannot be with their former foster carer(s).',
        affected_fields=['REC'],
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}
        if 'OC3' not in dfs:
            return {}
        else:
            header = dfs['Header']
            oc3 = dfs['OC3']
            collection_start = pd.to_datetime(dfs['metadata']['collection_start'], format='%d/%m/%Y', errors='coerce')
            collection_end = pd.to_datetime(dfs['metadata']['collection_end'], format='%d/%m/%Y', errors='coerce')

            header['DOB'] = pd.to_datetime(header['DOB'], format='%d/%m/%Y', errors='coerce')
            header['DOB17'] = header['DOB'] + pd.DateOffset(years=17)

            oc3_merged = oc3.reset_index().merge(header, how='left', on=['CHILD'], suffixes=('', '_header'),
                                                 indicator=True).set_index('index')

            accom_foster = oc3_merged['ACCOM'].str.upper().astype(str).isin(['Z1', 'Z2'])
            age_17_in_year = (oc3_merged['DOB17'] <= collection_end) & (oc3_merged['DOB17'] >= collection_start)

            error_mask = accom_foster & age_17_in_year

            error_locations = oc3.index[error_mask]

            return {'OC3': error_locations.to_list()}

    return error, _validate


def validate_389():
    error = ErrorDefinition(
        code='389',
        description='Reason episode ceased is that child transferred to care of adult social care services, but child is aged under 16.',
        affected_fields=['REC'],
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}
        if 'Episodes' not in dfs:
            return {}
        else:
            header = dfs['Header']
            episodes = dfs['Episodes']

            header['DOB'] = pd.to_datetime(header['DOB'], format='%d/%m/%Y', errors='coerce')
            episodes['DEC'] = pd.to_datetime(episodes['DEC'], format='%d/%m/%Y', errors='coerce')
            header['DOB16'] = header['DOB'] + pd.DateOffset(years=16)

            episodes_merged = episodes.reset_index().merge(header, how='left', on=['CHILD'], suffixes=('', '_header'),
                                                           indicator=True).set_index('index')

            ceased_asc = episodes_merged['REC'].str.upper().astype(str).isin(['E7'])
            ceased_over_16 = episodes_merged['DOB16'] <= episodes_merged['DEC']

            error_mask = ceased_asc & ~ceased_over_16

            error_locations = episodes_merged.index[error_mask].unique()

            return {'Episodes': error_locations.to_list()}

    return error, _validate


def validate_387():
    error = ErrorDefinition(
        code='387',
        description='Reason episode ceased is child moved into independent living arrangement, but the child is aged under 14.',
        affected_fields=['REC'],
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}
        if 'Episodes' not in dfs:
            return {}
        else:
            header = dfs['Header']
            episodes = dfs['Episodes']

            header['DOB'] = pd.to_datetime(header['DOB'], format='%d/%m/%Y', errors='coerce')
            episodes['DEC'] = pd.to_datetime(episodes['DEC'], format='%d/%m/%Y', errors='coerce')
            header['DOB14'] = header['DOB'] + pd.DateOffset(years=14)

            episodes_merged = episodes.reset_index().merge(header, how='left', on=['CHILD'], suffixes=('', '_header'),
                                                           indicator=True).set_index('index')

            ceased_indep = episodes_merged['REC'].str.upper().astype(str).isin(['E5', 'E6'])
            ceased_over_14 = episodes_merged['DOB14'] <= episodes_merged['DEC']
            dec_present = episodes_merged['DEC'].notna()

            error_mask = ceased_indep & ~ceased_over_14 & dec_present

            error_locations = episodes_merged.index[error_mask].unique()

            return {'Episodes': error_locations.to_list()}

    return error, _validate


def validate_452():
    error = ErrorDefinition(
        code='452',
        description='Contradiction between local authority of placement code in the last episode of the previous year and in the first episode of the current year.',
        affected_fields=['PL_LA'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        if 'Episodes_last' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            episodes_last = dfs['Episodes_last']

            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
            episodes_last['DECOM'] = pd.to_datetime(episodes_last['DECOM'], format='%d/%m/%Y', errors='coerce')

            episodes_min = episodes.groupby('CHILD')['DECOM'].idxmin()
            episodes_last_max = episodes_last.groupby('CHILD')['DECOM'].idxmax()

            episodes = episodes[episodes.index.isin(episodes_min)]
            episodes_last = episodes_last[episodes_last.index.isin(episodes_last_max)]

            episodes_merged = episodes.reset_index().merge(episodes_last, how='left', on=['CHILD'],
                                                           suffixes=('', '_last'), indicator=True).set_index('index')

            in_both_years = episodes_merged['_merge'] == 'both'
            same_rne = episodes_merged['RNE'] == episodes_merged['RNE_last']
            last_year_open = episodes_merged['DEC_last'].isna()
            different_pl_la = episodes_merged['PL_LA'].astype(str) != episodes_merged['PL_LA_last'].astype(str)

            error_mask = in_both_years & same_rne & last_year_open & different_pl_la

            validation_error_locations = episodes.index[error_mask]

            return {'Episodes': validation_error_locations.tolist()}

    return error, _validate


def validate_386():
    error = ErrorDefinition(
        code='386',
        description='Reason episode ceased is adopted but child has reached age 18.',
        affected_fields=['REC'],
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}
        if 'Episodes' not in dfs:
            return {}
        else:
            header = dfs['Header']
            episodes = dfs['Episodes']

            header['DOB'] = pd.to_datetime(header['DOB'], format='%d/%m/%Y', errors='coerce')
            episodes['DEC'] = pd.to_datetime(episodes['DEC'], format='%d/%m/%Y', errors='coerce')
            header['DOB18'] = header['DOB'] + pd.DateOffset(years=18)

            episodes_merged = (
                episodes
                    .reset_index()
                    .merge(header, how='left', on=['CHILD'], suffixes=('', '_header'), indicator=True)
                    .set_index('index')
                    .dropna(subset=['DOB18', 'DEC'])
            )

            ceased_adopted = episodes_merged['REC'].str.upper().astype(str).isin(['E11', 'E12'])
            ceased_under_18 = episodes_merged['DOB18'] > episodes_merged['DEC']

            error_mask = ceased_adopted & ~ceased_under_18

            error_locations = episodes_merged.index[error_mask]

            return {'Episodes': error_locations.to_list()}

    return error, _validate


def validate_363():
    error = ErrorDefinition(
        code='363',
        description='Child assessment order (CAO) lasted longer than 7 days allowed in the Children Act 1989.',
        affected_fields=['LS', 'DECOM', 'DEC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        episodes = dfs['Episodes']
        collection_end_str = dfs['metadata']['collection_end']

        L2_eps = episodes[episodes['LS'] == 'L3'].copy()
        L2_eps['original_index'] = L2_eps.index
        L2_eps = L2_eps[L2_eps['DECOM'].notna()]

        L2_eps.loc[L2_eps['DEC'].isna(), 'DEC'] = collection_end_str
        L2_eps['DECOM'] = pd.to_datetime(L2_eps['DECOM'], format='%d/%m/%Y', errors='coerce')
        L2_eps = L2_eps.dropna(subset=['DECOM'])
        L2_eps['DEC'] = pd.to_datetime(L2_eps['DEC'], format='%d/%m/%Y', errors='coerce')

        L2_eps.sort_values(['CHILD', 'DECOM'])

        L2_eps['index'] = pd.RangeIndex(0, len(L2_eps))
        L2_eps['index+1'] = L2_eps['index'] + 1
        L2_eps = L2_eps.merge(L2_eps, left_on='index', right_on='index+1',
                              how='left', suffixes=[None, '_prev'])
        L2_eps = L2_eps[['original_index', 'DECOM', 'DEC', 'DEC_prev', 'CHILD', 'CHILD_prev', 'LS']]

        L2_eps['new_period'] = (
                (L2_eps['DECOM'] > L2_eps['DEC_prev'])
                | (L2_eps['CHILD'] != L2_eps['CHILD_prev'])
        )

        L2_eps['duration'] = (L2_eps['DEC'] - L2_eps['DECOM']).dt.days
        L2_eps['period_id'] = L2_eps['new_period'].astype(int).cumsum()
        L2_eps['period_duration'] = L2_eps.groupby('period_id')['duration'].transform(sum)

        error_mask = L2_eps['period_duration'] > 7

        return {'Episodes': L2_eps.loc[error_mask, 'original_index'].to_list()}

    return error, _validate


def validate_364():
    error = ErrorDefinition(
        code='364',
        description='Sections 41-46 of Police and Criminal Evidence (PACE; 1984) severely limits ' +
                    'the time a child can be detained in custody in Local Authority (LA) accommodation.',
        affected_fields=['LS', 'DECOM', 'DEC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        episodes = dfs['Episodes']
        collection_end_str = dfs['metadata']['collection_end']

        J2_eps = episodes[episodes['LS'] == 'J2'].copy()
        J2_eps['original_index'] = J2_eps.index

        J2_eps['DECOM'] = pd.to_datetime(J2_eps['DECOM'], format='%d/%m/%Y', errors='coerce')
        J2_eps = J2_eps[J2_eps['DECOM'].notna()]
        J2_eps.loc[J2_eps['DEC'].isna(), 'DEC'] = collection_end_str
        J2_eps['DEC'] = pd.to_datetime(J2_eps['DEC'], format='%d/%m/%Y', errors='coerce')

        J2_eps.sort_values(['CHILD', 'DECOM'])

        J2_eps['index'] = pd.RangeIndex(0, len(J2_eps))
        J2_eps['index_prev'] = J2_eps['index'] + 1
        J2_eps = J2_eps.merge(J2_eps, left_on='index', right_on='index_prev',
                              how='left', suffixes=[None, '_prev'])
        J2_eps = J2_eps[['original_index', 'DECOM', 'DEC', 'DEC_prev', 'CHILD', 'CHILD_prev', 'LS']]

        J2_eps['new_period'] = (
                (J2_eps['DECOM'] > J2_eps['DEC_prev'])
                | (J2_eps['CHILD'] != J2_eps['CHILD_prev'])
        )

        J2_eps['duration'] = (J2_eps['DEC'] - J2_eps['DECOM']).dt.days
        J2_eps['period_id'] = J2_eps['new_period'].astype(int).cumsum()
        J2_eps['period_duration'] = J2_eps.groupby('period_id')['duration'].transform(sum)

        error_mask = J2_eps['period_duration'] > 21

        return {'Episodes': J2_eps.loc[error_mask, 'original_index'].to_list()}

    return error, _validate


def validate_365():
    error = ErrorDefinition(
        code='365',
        description='Any individual short- term respite placement must not exceed 17 days.',
        affected_fields=['LS', 'DECOM', 'DEC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        episodes = dfs['Episodes']
        collection_end_str = dfs['metadata']['collection_end']

        episodes.loc[episodes['DEC'].isna(), 'DEC'] = collection_end_str
        episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
        episodes['DEC'] = pd.to_datetime(episodes['DEC'], format='%d/%m/%Y', errors='coerce')

        over_17_days = episodes['DEC'] > episodes['DECOM'] + pd.DateOffset(days=17)
        error_mask = (episodes['LS'] == 'V3') & over_17_days

        return {'Episodes': episodes.index[error_mask].to_list()}

    return error, _validate


def validate_367():
    error = ErrorDefinition(
        code='367',
        description='The maximum amount of respite care allowable is 75 days in any 12-month period.',
        affected_fields=['LS', 'DECOM', 'DEC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}

        episodes = dfs['Episodes']
        V3_eps = episodes[episodes['LS'] == 'V3']

        V3_eps = V3_eps.dropna(subset=['DECOM'])  # missing DECOM should get fixed before looking for this error

        collection_start = pd.to_datetime(dfs['metadata']['collection_start'], format='%d/%m/%Y', errors='coerce')
        collection_end = pd.to_datetime(dfs['metadata']['collection_end'], format='%d/%m/%Y', errors='coerce')
        V3_eps['DECOM_dt'] = pd.to_datetime(V3_eps['DECOM'], format='%d/%m/%Y', errors='coerce')
        V3_eps['DEC_dt'] = pd.to_datetime(V3_eps['DEC'], format='%d/%m/%Y', errors='coerce')

        # truncate episode start/end dates to collection start/end respectively
        V3_eps.loc[V3_eps['DEC'].isna() | (V3_eps['DEC_dt'] > collection_end), 'DEC_dt'] = collection_end
        V3_eps.loc[V3_eps['DECOM_dt'] < collection_start, 'DECOM_dt'] = collection_start

        V3_eps['duration'] = (V3_eps['DEC_dt'] - V3_eps['DECOM_dt']).dt.days
        V3_eps = V3_eps[V3_eps['duration'] > 0]

        V3_eps['year_total_duration'] = V3_eps.groupby('CHILD')['duration'].transform(sum)

        error_mask = V3_eps['year_total_duration'] > 75

        return {'Episodes': V3_eps.index[error_mask].to_list()}

    return error, _validate


def validate_440():
    error = ErrorDefinition(
        code='440',
        description='Participation method indicates child was under 4 years old at the time of the review, but date of birth and review date indicates the child was 4 years old or over.',
        affected_fields=['DOB', 'REVIEW', 'REVIEW_CODE'],
    )

    def _validate(dfs):
        if 'Reviews' not in dfs:
            return {}
        else:
            reviews = dfs['Reviews']
            reviews['DOB'] = pd.to_datetime(reviews['DOB'], format='%d/%m/%Y', errors='coerce')
            reviews['REVIEW'] = pd.to_datetime(reviews['REVIEW'], format='%d/%m/%Y', errors='coerce')

            mask = reviews['REVIEW_CODE'].eq('PN0') & (
                    reviews['REVIEW'] > reviews['DOB'] + pd.offsets.DateOffset(years=4))

            validation_error_mask = mask
            validation_error_locations = reviews.index[validation_error_mask]

            return {'Reviews': validation_error_locations.tolist()}

    return error, _validate


def validate_514():
    error = ErrorDefinition(
      code='514',
      description= 'Data entry on the legal status of adopters shows a single adopter but data entry for the numbers of adopters shows it as a couple.',
      affected_fields=['LS_ADOPTR', 'SEX_ADOPTR'],
    )

    def _validate(dfs):

        if 'AD1' not in dfs:
            return {}
        else:
            AD1 = dfs ['AD1']
            code_list = ['M1', 'F1']
            # Check if LS Adopter is L0 and Sex Adopter is not M1 or F1.
            error_mask = (AD1['LS_ADOPTR'] == 'L0') & (~AD1['SEX_ADOPTR'].isin(code_list))

            error_locations = AD1.index[error_mask]

            return {'AD1': error_locations.tolist()}


    return error, _validate

def validate_445():
    error = ErrorDefinition(
        code='445',
        description='D1 is not a valid code for episodes starting after December 2005.',
        affected_fields=['LS', 'DECOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
            max_decom_allowed = pd.to_datetime('31/12/2005', format='%d/%m/%Y', errors='coerce')

            mask = episodes['LS'].eq('D1') & (episodes['DECOM'] > max_decom_allowed)
            validation_error_mask = mask
            validation_error_locations = episodes.index[validation_error_mask]

            return {'Episodes': validation_error_locations.tolist()}

    return error, _validate


def validate_446():
    error = ErrorDefinition(
        code='446',
        description='E1 is not a valid code for episodes starting before December 2005.',
        affected_fields=['LS', 'DECOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
            min_decom_allowed = pd.to_datetime('01/12/2005', format='%d/%m/%Y', errors='coerce')

            mask = episodes['LS'].eq('E1') & (episodes['DECOM'] < min_decom_allowed)
            validation_error_mask = mask
            validation_error_locations = episodes.index[validation_error_mask]

            return {'Episodes': validation_error_locations.tolist()}

    return error, _validate


def validate_208():
    error = ErrorDefinition(
        code='208',
        description='Unique Pupil Number (UPN) for the current year disagrees with the Unique Pupil Number (UPN) already recorded for this child.',
        affected_fields=['UPN'],
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'Header_last' not in dfs:
            return {}
        else:
            header = dfs['Header']
            header_last = dfs['Header_last']

            header_merged = header.reset_index().merge(header_last, how='left', on=['CHILD'], suffixes=('', '_last'),
                                                       indicator=True).set_index('index')

            in_both_years = header_merged['_merge'] == 'both'
            upn_is_different = header_merged['UPN'].str.upper().astype(str) != header_merged[
                'UPN_last'].str.upper().astype(str)
            upn_not_recorded = header_merged['UPN'].str.upper().astype(str).isin(['UN2', 'UN3', 'UN4', 'UN5', 'UN6']) & \
                               header_merged['UPN_last'].str.upper().astype(str).isin(['UN1'])

            error_mask = in_both_years & upn_is_different & ~upn_not_recorded

            error_locations = header.index[error_mask]

            return {'Header': error_locations.to_list()}

    return error, _validate


def validate_204():
    error = ErrorDefinition(
        code='204',
        description='Ethnic origin code disagrees with the ethnic origin already recorded for this child.',
        affected_fields=['ETHNIC'],
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'Header_last' not in dfs:
            return {}
        else:
            header = dfs['Header']
            header_last = dfs['Header_last']

            header_merged = header.reset_index().merge(header_last, how='left', on=['CHILD'], suffixes=('', '_last'),
                                                       indicator=True).set_index('index')

            in_both_years = header_merged['_merge'] == 'both'
            ethnic_is_different = header_merged['ETHNIC'].astype(str).str.upper() != header_merged[
                'ETHNIC_last'].astype(str).str.upper()

            error_mask = in_both_years & ethnic_is_different

            error_locations = header.index[error_mask]

            return {'Header': error_locations.to_list()}

    return error, _validate


def validate_203():
    error = ErrorDefinition(
        code='203',
        description='Date of birth disagrees with the date of birth already recorded for this child.',
        affected_fields=['DOB'],
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'Header_last' not in dfs:
            return {}
        else:
            header = dfs['Header']
            header_last = dfs['Header_last']

            header['DOB'] = pd.to_datetime(header['DOB'], format='%d/%m/%Y', errors='coerce')
            header_last['DOB'] = pd.to_datetime(header_last['DOB'], format='%d/%m/%Y', errors='coerce')

            header_merged = header.reset_index().merge(header_last, how='left', on=['CHILD'], suffixes=('', '_last'),
                                                       indicator=True).set_index('index')

            in_both_years = header_merged['_merge'] == 'both'
            dob_is_different = header_merged['DOB'].astype(str) != header_merged['DOB_last'].astype(str)

            error_mask = in_both_years & dob_is_different

            error_locations = header.index[error_mask]

            return {'Header': error_locations.to_list()}

    return error, _validate


def validate_530():
    error = ErrorDefinition(
        code='530',
        description="A placement provider code of PR4 cannot be associated with placement P1.",
        affected_fields=['PLACE', 'PLACE_PROVIDER'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            mask = episodes['PLACE'].eq('P1') & episodes['PLACE_PROVIDER'].eq('PR4')

            validation_error_mask = mask
            validation_error_locations = episodes.index[validation_error_mask]

            return {'Episodes': validation_error_locations.tolist()}

    return error, _validate


def validate_571():
    error = ErrorDefinition(
        code='571',
        description='The date that the child ceased to be missing or away from placement without authorisation is before the start or after the end of the collection year.',
        affected_fields=['MIS_END'],
    )

    def _validate(dfs):
        if 'Missing' not in dfs:
            return {}
        else:
            missing = dfs['Missing']
            collection_start = pd.to_datetime(dfs['metadata']['collection_start'], format='%d/%m/%Y', errors='coerce')
            collection_end = pd.to_datetime(dfs['metadata']['collection_end'], format='%d/%m/%Y', errors='coerce')

            missing['fMIS_END'] = pd.to_datetime(missing['MIS_END'], format='%d/%m/%Y', errors='coerce')

            end_date_before_year = missing['fMIS_END'] < collection_start
            end_date_after_year = missing['fMIS_END'] > collection_end

            error_mask = end_date_before_year | end_date_after_year

            error_locations = missing.index[error_mask]

            return {'Missing': error_locations.to_list()}

    return error, _validate


def validate_1005():
    error = ErrorDefinition(
        code='1005',
        description='The end date of the missing episode or episode that the child was away from placement without authorisation is not a valid date.',
        affected_fields=['MIS_END'],
    )

    def _validate(dfs):
        if 'Missing' not in dfs:
            return {}
        else:
            missing = dfs['Missing']
            missing['fMIS_END'] = pd.to_datetime(missing['MIS_END'], format='%d/%m/%Y', errors='coerce')

            missing_end_date = missing['MIS_END'].isna()
            invalid_end_date = missing['fMIS_END'].isna()

            error_mask = ~missing_end_date & invalid_end_date

            error_locations = missing.index[error_mask]

            return {'Missing': error_locations.to_list()}

    return error, _validate


def validate_1004():
    error = ErrorDefinition(
        code='1004',
        description='The start date of the missing episode or episode that the child was away from placement without authorisation is not a valid date.',
        affected_fields=['MIS_START'],
    )

    def _validate(dfs):
        if 'Missing' not in dfs:
            return {}
        else:
            missing = dfs['Missing']

            missing['fMIS_START'] = pd.to_datetime(missing['MIS_START'], format='%d/%m/%Y', errors='coerce')

            missing_start_date = missing['MIS_START'].isna()
            invalid_start_date = missing['fMIS_START'].isna()

            error_mask = missing_start_date | invalid_start_date

            error_locations = missing.index[error_mask]

            return {'Missing': error_locations.to_list()}

    return error, _validate


def validate_202():
    error = ErrorDefinition(
        code='202',
        description='The gender code conflicts with the gender already recorded for this child.',
        affected_fields=['SEX'],
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'Header_last' not in dfs:
            return {}
        else:
            header = dfs['Header']
            header_last = dfs['Header_last']

            header_merged = header.reset_index().merge(header_last, how='left', on=['CHILD'], suffixes=('', '_last'),
                                                       indicator=True).set_index('index')

            in_both_years = header_merged['_merge'] == 'both'
            sex_is_different = header_merged['SEX'].astype(str) != header_merged['SEX_last'].astype(str)

            error_mask = in_both_years & sex_is_different

            error_locations = header_merged.index[error_mask]

            return {'Header': error_locations.to_list()}

    return error, _validate


def validate_621():
    error = ErrorDefinition(
        code='621',
        description="Mother’s field has been completed but date of birth shows that the mother is younger than her child.",
        affected_fields=['DOB', 'MC_DOB'],
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}
        else:
            header = dfs['Header']

            header['MC_DOB'] = pd.to_datetime(header['MC_DOB'], format='%d/%m/%Y', errors='coerce')
            header['DOB'] = pd.to_datetime(header['DOB'], format='%d/%m/%Y', errors='coerce')
            mask = (header['MC_DOB'] > header['DOB']) | header['MC_DOB'].isna()

            validation_error_mask = ~mask
            validation_error_locations = header.index[validation_error_mask]

            return {'Header': validation_error_locations.tolist()}

    return error, _validate


def validate_556():
    error = ErrorDefinition(
        code='556',
        description='Date of decision that the child should be placed for adoption should be on or prior to the date that the freeing order was granted.',
        affected_fields=['DATE_PLACED', 'DECOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'PlacedAdoption' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            placedAdoptions = dfs['PlacedAdoption']

            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
            placedAdoptions['DATE_PLACED'] = pd.to_datetime(placedAdoptions['DATE_PLACED'], format='%d/%m/%Y',
                                                            errors='coerce')

            episodes = episodes.reset_index()

            D1Episodes = episodes[episodes['LS'] == 'D1']

            merged = D1Episodes.reset_index().merge(placedAdoptions, how='left', on='CHILD', ).set_index('index')

            episodes_with_errors = merged[merged['DATE_PLACED'] > merged['DECOM']]

            error_mask = episodes.index.isin(episodes_with_errors.index)

            error_locations = episodes.index[error_mask]

            return {'Episodes': error_locations.to_list()}

    return error, _validate


def validate_393():
    error = ErrorDefinition(
        code='393',
        description='Child is looked after but mother field is not completed.',
        affected_fields=['MOTHER'],
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'Episodes' not in dfs:
            return {}
        else:
            header = dfs['Header']
            episodes = dfs['Episodes']

            header_female = header[header['SEX'].astype(str) == '2']

            applicable_episodes = episodes[~episodes['LS'].str.upper().isin(['V3', 'V4'])]

            error_mask = header_female['CHILD'].isin(applicable_episodes['CHILD']) & header_female['MOTHER'].isna()

            error_locations = header_female.index[error_mask]

            return {'Header': error_locations.to_list()}

    return error, _validate


def validate_NoE():
    error = ErrorDefinition(
        code='NoE',
        description='This child has no episodes loaded for previous year even though child started to be looked after before this current year.',
        affected_fields=['DECOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'Episodes_last' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
            episodes_last = dfs['Episodes_last']
            episodes_last['DECOM'] = pd.to_datetime(episodes_last['DECOM'], format='%d/%m/%Y', errors='coerce')
            collection_start = pd.to_datetime(dfs['metadata']['collection_start'], format='%d/%m/%Y', errors='coerce')

            episodes_before_year = episodes[episodes['DECOM'] < collection_start]

            episodes_merged = episodes_before_year.reset_index().merge(episodes_last, how='left', on=['CHILD'],
                                                                       indicator=True).set_index('index')

            episodes_not_matched = episodes_merged[episodes_merged['_merge'] == 'left_only']

            error_mask = episodes.index.isin(episodes_not_matched.index)

            error_locations = episodes.index[error_mask]

            return {'Episodes': error_locations.to_list()}

    return error, _validate


def validate_356():
    error = ErrorDefinition(
        code='356',
        description='The date the episode ceased is before the date the same episode started.',
        affected_fields=['DECOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
            episodes['DEC'] = pd.to_datetime(episodes['DEC'], format='%d/%m/%Y', errors='coerce')

            error_mask = episodes['DEC'].notna() & (episodes['DEC'] < episodes['DECOM'])

            return {'Episodes': episodes.index[error_mask].to_list()}

    return error, _validate


def validate_611():
    error = ErrorDefinition(
        code='611',
        description="Date of birth field is blank, but child is a mother.",
        affected_fields=['MOTHER', 'MC_DOB'],
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}
        else:
            header = dfs['Header']
            validation_error_mask = header['MOTHER'].astype(str).isin(['1']) & header['MC_DOB'].isna()
            validation_error_locations = header.index[validation_error_mask]

            return {'Header': validation_error_locations.tolist()}

    return error, _validate


def validate_1009():
    error = ErrorDefinition(
        code='1009',
        description='Reason for placement change is not a valid code.',
        affected_fields=['REASON_PLACE_CHANGE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}

        episodes = dfs['Episodes']
        code_list = [
            'CARPL',
            'CLOSE',
            'ALLEG',
            'STAND',
            'APPRR',
            'CREQB',
            'CREQO',
            'CHILD',
            'LAREQ',
            'PLACE',
            'CUSTOD',
            'OTHER'
        ]

        mask = episodes['REASON_PLACE_CHANGE'].isin(code_list) | episodes['REASON_PLACE_CHANGE'].isna()

        validation_error_mask = ~mask
        validation_error_locations = episodes.index[validation_error_mask]

        return {'Episodes': validation_error_locations.tolist()}

    return error, _validate


def validate_1006():
    error = ErrorDefinition(
        code='1006',
        description='Missing type invalid.',
        affected_fields=['MISSING'],
    )

    def _validate(dfs):
        if 'Missing' not in dfs:
            return {}

        missing_from_care = dfs['Missing']
        code_list = ['M', 'A']

        mask = missing_from_care['MISSING'].isin(code_list) | missing_from_care['MISSING'].isna()

        validation_error_mask = ~mask
        validation_error_locations = missing_from_care.index[validation_error_mask]

        return {'Missing': validation_error_locations.tolist()}

    return error, _validate


def validate_631():
    error = ErrorDefinition(
        code='631',
        description='Previous permanence option not a valid value.',
        affected_fields=['PREV_PERM'],
    )

    def _validate(dfs):
        if 'PrevPerm' not in dfs:
            return {}

        previous_permanence = dfs['PrevPerm']
        code_list = ['P1', 'P2', 'P3', 'P4', 'Z1']

        mask = previous_permanence['PREV_PERM'].isin(code_list) | previous_permanence['PREV_PERM'].isna()

        validation_error_mask = ~mask
        validation_error_locations = previous_permanence.index[validation_error_mask]

        return {'PrevPerm': validation_error_locations.tolist()}

    return error, _validate


def validate_196():
    error = ErrorDefinition(
        code='196',
        description='Strengths and Difficulties (SDQ) reason is not a valid code.',
        affected_fields=['SDQ_REASON'],
    )

    def _validate(dfs):
        if 'OC2' not in dfs:
            return {}

        oc2 = dfs['OC2']
        code_list = ['SDQ1', 'SDQ2', 'SDQ3', 'SDQ4', 'SDQ5']

        mask = oc2['SDQ_REASON'].isin(code_list) | oc2['SDQ_REASON'].isna()

        validation_error_mask = ~mask
        validation_error_locations = oc2.index[validation_error_mask]

        return {'OC2': validation_error_locations.tolist()}

    return error, _validate


def validate_177():
    error = ErrorDefinition(
        code='177',
        description='The legal status of adopter(s) code is not a valid code.',
        affected_fields=['LS_ADOPTR'],
    )

    def _validate(dfs):
        if 'AD1' not in dfs:
            return {}

        adoptions = dfs['AD1']
        code_list = ['L0', 'L11', 'L12', 'L2', 'L3', 'L4']

        mask = adoptions['LS_ADOPTR'].isin(code_list) | adoptions['LS_ADOPTR'].isna()

        validation_error_mask = ~mask
        validation_error_locations = adoptions.index[validation_error_mask]

        return {'AD1': validation_error_locations.tolist()}

    return error, _validate


def validate_176():
    error = ErrorDefinition(
        code='176',
        description='The gender of adopter(s) at the date of adoption code is not a valid code.',
        affected_fields=['SEX_ADOPTR'],
    )

    def _validate(dfs):
        if 'AD1' not in dfs:
            return {}

        adoptions = dfs['AD1']
        code_list = ['M1', 'F1', 'MM', 'FF', 'MF']

        mask = adoptions['SEX_ADOPTR'].isin(code_list) | adoptions['SEX_ADOPTR'].isna()

        validation_error_mask = ~mask
        validation_error_locations = adoptions.index[validation_error_mask]

        return {'AD1': validation_error_locations.tolist()}

    return error, _validate


def validate_175():
    error = ErrorDefinition(
        code='175',
        description='The number of adopter(s) code is not a valid code.',
        affected_fields=['NB_ADOPTR'],
    )

    def _validate(dfs):
        if 'AD1' not in dfs:
            return {}

        adoptions = dfs['AD1']
        code_list = ['1', '2']

        mask = adoptions['NB_ADOPTR'].astype(str).isin(code_list) | adoptions['NB_ADOPTR'].isna()

        validation_error_mask = ~mask
        validation_error_locations = adoptions.index[validation_error_mask]

        return {'AD1': validation_error_locations.tolist()}

    return error, _validate


def validate_132():
    error = ErrorDefinition(
        code='132',
        description='Data entry for activity after leaving care is invalid.',
        affected_fields=['ACTIV'],
    )

    def _validate(dfs):
        if 'OC3' not in dfs:
            return {}

        care_leavers = dfs['OC3']
        code_list = [
            'F1',
            'P1',
            'F2',
            'P2',
            'F4',
            'P4',
            'F5',
            'P5',
            'G4',
            'G5',
            'G6',
            '0'
        ]
        mask = care_leavers['ACTIV'].astype(str).isin(code_list) | care_leavers['ACTIV'].isna()

        validation_error_mask = ~mask
        validation_error_locations = care_leavers.index[validation_error_mask]

        return {'OC3': validation_error_locations.tolist()}

    return error, _validate


def validate_131():
    error = ErrorDefinition(
        code='131',
        description='Data entry for being in touch after leaving care is invalid.',
        affected_fields=['IN_TOUCH'],
    )

    def _validate(dfs):
        if 'OC3' not in dfs:
            return {}

        care_leavers = dfs['OC3']
        code_list = [
            'YES',
            'NO',
            'DIED',
            'REFU',
            'NREQ',
            'RHOM'
        ]
        mask = care_leavers['IN_TOUCH'].isin(code_list) | care_leavers['IN_TOUCH'].isna()

        validation_error_mask = ~mask
        validation_error_locations = care_leavers.index[validation_error_mask]

        return {'OC3': validation_error_locations.tolist()}

    return error, _validate


def validate_120():
    error = ErrorDefinition(
        code='120',
        description='The reason for the reversal of the decision that the child should be placed for adoption code is not valid.',
        affected_fields=['REASON_PLACED_CEASED'],
    )

    def _validate(dfs):
        if 'PlacedAdoption' not in dfs:
            return {}

        placed_adoptions = dfs['PlacedAdoption']
        code_list = ['RD1', 'RD2', 'RD3', 'RD4']

        mask = placed_adoptions['REASON_PLACED_CEASED'].isin(code_list) | placed_adoptions[
            'REASON_PLACED_CEASED'].isna()

        validation_error_mask = ~mask
        validation_error_locations = placed_adoptions.index[validation_error_mask]

        return {'PlacedAdoption': validation_error_locations.tolist()}

    return error, _validate


def validate_114():
    error = ErrorDefinition(
        code='114',
        description='Data entry to record the status of former carer(s) of an adopted child is invalid.',
        affected_fields=['FOSTER_CARE'],
    )

    def _validate(dfs):
        if 'AD1' not in dfs:
            return {}

        adoptions = dfs['AD1']
        code_list = ['0', '1']

        mask = adoptions['FOSTER_CARE'].astype(str).isin(code_list) | adoptions['FOSTER_CARE'].isna()

        validation_error_mask = ~mask
        validation_error_locations = adoptions.index[validation_error_mask]

        return {'AD1': validation_error_locations.tolist()}

    return error, _validate


def validate_178():
    error = ErrorDefinition(
        code='178',
        description='Placement provider code is not a valid code.',
        affected_fields=['PLACE_PROVIDER'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}

        episodes = dfs['Episodes']

        code_list_placement_provider = ['PR0', 'PR1', 'PR2', 'PR3', 'PR4', 'PR5']
        code_list_placement_with_no_provider = ['T0', 'T1', 'T2', 'T3', 'T4', 'Z1']

        place_provider_needed_and_correct = episodes['PLACE_PROVIDER'].isin(code_list_placement_provider) & ~episodes[
            'PLACE'].isin(code_list_placement_with_no_provider)

        place_provider_not_provided = episodes['PLACE_PROVIDER'].isna()

        place_provider_not_needed = episodes['PLACE_PROVIDER'].isna() & episodes['PLACE'].isin(
            code_list_placement_with_no_provider)

        mask = place_provider_needed_and_correct | place_provider_not_provided | place_provider_not_needed

        validation_error_mask = ~mask
        validation_error_locations = episodes.index[validation_error_mask]

        return {'Episodes': validation_error_locations.tolist()}

    return error, _validate


def validate_103():
    error = ErrorDefinition(
        code='103',
        description='The ethnicity code is either not valid or has not been entered.',
        affected_fields=['ETHNIC'],
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}

        header = dfs['Header']
        code_list = [
            'WBRI',
            'WIRI',
            'WOTH',
            'WIRT',
            'WROM',
            'MWBC',
            'MWBA',
            'MWAS',
            'MOTH',
            'AIND',
            'APKN',
            'ABAN',
            'AOTH',
            'BCRB',
            'BAFR',
            'BOTH',
            'CHNE',
            'OOTH',
            'REFU',
            'NOBT'
        ]

        mask = header['ETHNIC'].isin(code_list)

        validation_error_mask = ~mask
        validation_error_locations = header.index[validation_error_mask]

        return {'Header': validation_error_locations.tolist()}

    return error, _validate


def validate_143():
    error = ErrorDefinition(
        code='143',
        description='The reason for new episode code is not a valid code.',
        affected_fields=['RNE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}

        episodes = dfs['Episodes']
        code_list = ['S', 'P', 'L', 'T', 'U', 'B']

        mask = episodes['RNE'].isin(code_list) | episodes['RNE'].isna()

        validation_error_mask = ~mask
        validation_error_locations = episodes.index[validation_error_mask]

        return {'Episodes': validation_error_locations.tolist()}

    return error, _validate


def validate_144():
    error = ErrorDefinition(
        code='144',
        description='The legal status code is not a valid code.',
        affected_fields=['LS'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}

        episodes = dfs['Episodes']
        code_list = [
            'C1',
            'C2',
            'D1',
            'E1',
            'V2',
            'V3',
            'V4',
            'J1',
            'J2',
            'J3',
            'L1',
            'L2',
            'L3'
        ]

        mask = episodes['LS'].isin(code_list) | episodes['LS'].isna()

        validation_error_mask = ~mask
        validation_error_locations = episodes.index[validation_error_mask]

        return {'Episodes': validation_error_locations.tolist()}

    return error, _validate


def validate_145():
    error = ErrorDefinition(
        code='145',
        description='Category of need code is not a valid code.',
        affected_fields=['CIN'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}

        episodes = dfs['Episodes']
        code_list = [
            'N1',
            'N2',
            'N3',
            'N4',
            'N5',
            'N6',
            'N7',
            'N8',
        ]

        mask = episodes['CIN'].isin(code_list) | episodes['CIN'].isna()
        validation_error_mask = ~mask
        validation_error_locations = episodes.index[validation_error_mask]

        return {'Episodes': validation_error_locations.tolist()}

    return error, _validate


def validate_146():
    error = ErrorDefinition(
        code='146',
        description='Placement type code is not a valid code.',
        affected_fields=['PLACE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}

        episodes = dfs['Episodes']
        code_list = [
            'A3',
            'A4',
            'A5',
            'A6',
            'H5',
            'K1',
            'K2',
            'P1',
            'P2',
            'P3',
            'R1',
            'R2',
            'R3',
            'R5',
            'S1',
            'T0',
            'T1',
            'T2',
            'T3',
            'T4',
            'U1',
            'U2',
            'U3',
            'U4',
            'U5',
            'U6',
            'Z1'
        ]

        mask = episodes['PLACE'].isin(code_list) | episodes['PLACE'].isna()

        validation_error_mask = ~mask
        validation_error_locations = episodes.index[validation_error_mask]

        return {'Episodes': validation_error_locations.tolist()}

    return error, _validate


def validate_149():
    error = ErrorDefinition(
        code='149',
        description='Reason episode ceased code is not valid. ',
        affected_fields=['REC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}

        episodes = dfs['Episodes']
        code_list = [
            'E11',
            'E12',
            'E2',
            'E3',
            'E4A',
            'E4B',
            'E13',
            'E41',
            'E45',
            'E46',
            'E47',
            'E48',
            'E5',
            'E6',
            'E7',
            'E8',
            'E9',
            'E14',
            'E15',
            'E16',
            'E17',
            'X1'
        ]

        mask = episodes['REC'].isin(code_list) | episodes['REC'].isna()

        validation_error_mask = ~mask
        validation_error_locations = episodes.index[validation_error_mask]

        return {'Episodes': validation_error_locations.tolist()}

    return error, _validate


def validate_167():
    error = ErrorDefinition(
        code='167',
        description='Data entry for participation is invalid or blank.',
        affected_fields=['REVIEW_CODE'],
    )

    def _validate(dfs):
        if 'Reviews' not in dfs:
            return {}

        review = dfs['Reviews']
        code_list = ['PN0', 'PN1', 'PN2', 'PN3', 'PN4', 'PN5', 'PN6', 'PN7']

        mask = review['REVIEW'].notna() & review['REVIEW_CODE'].isin(code_list) | review['REVIEW'].isna() & review[
            'REVIEW_CODE'].isna()

        validation_error_mask = ~mask
        validation_error_locations = review.index[validation_error_mask]

        return {'Reviews': validation_error_locations.tolist()}

    return error, _validate


def validate_101():
    error = ErrorDefinition(
        code='101',
        description='Gender code is not valid.',
        affected_fields=['SEX'],
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}

        header = dfs['Header']
        code_list = ['1', '2']

        mask = header['SEX'].astype(str).isin(code_list)

        validation_error_mask = ~mask
        validation_error_locations = header.index[validation_error_mask]

        return {'Header': validation_error_locations.tolist()}

    return error, _validate


def validate_141():
    error = ErrorDefinition(
        code='141',
        description='Date episode began is not a valid date.',
        affected_fields=['DECOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            mask = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce').notna()

            na_location = episodes['DECOM'].isna()

            validation_error_mask = ~mask & ~na_location
            validation_error_locations = episodes.index[validation_error_mask]

            return {'Episodes': validation_error_locations.tolist()}

    return error, _validate


def validate_147():
    error = ErrorDefinition(
        code='147',
        description='Date episode ceased is not a valid date.',
        affected_fields=['DEC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            mask = pd.to_datetime(episodes['DEC'], format='%d/%m/%Y', errors='coerce').notna()

            na_location = episodes['DEC'].isna()

            validation_error_mask = ~mask & ~na_location
            validation_error_locations = episodes.index[validation_error_mask]

            return {'Episodes': validation_error_locations.tolist()}

    return error, _validate


def validate_171():
    error = ErrorDefinition(
        code='171',
        description="Date of birth of mother's child is not a valid date.",
        affected_fields=['MC_DOB'],
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}
        else:
            header = dfs['Header']
            mask = pd.to_datetime(header['MC_DOB'], format='%d/%m/%Y', errors='coerce').notna()

            na_location = header['MC_DOB'].isna()

            validation_error_mask = ~mask & ~na_location
            validation_error_locations = header.index[validation_error_mask]

            return {'Header': validation_error_locations.tolist()}

    return error, _validate


def validate_102():
    error = ErrorDefinition(
        code='102',
        description='Date of birth is not a valid date.',
        affected_fields=['DOB'],
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}
        else:
            header = dfs['Header']
            mask = pd.to_datetime(header['DOB'], format='%d/%m/%Y', errors='coerce').notna()

            validation_error_mask = ~mask
            validation_error_locations = header.index[validation_error_mask]

            return {'Header': validation_error_locations.tolist()}

    return error, _validate


def validate_112():
    error = ErrorDefinition(
        code='112',
        description='Date should be placed for adoption is not a valid date.',
        affected_fields=['DATE_INT'],
    )

    def _validate(dfs):
        if 'AD1' not in dfs:
            return {}
        else:
            ad1 = dfs['AD1']
            mask = pd.to_datetime(ad1['DATE_INT'], format='%d/%m/%Y', errors='coerce').notna()

            na_location = ad1['DATE_INT'].isna()

            validation_error_mask = ~mask & ~na_location
            validation_error_locations = ad1.index[validation_error_mask]

            return {'AD1': validation_error_locations.tolist()}

    return error, _validate


def validate_115():
    error = ErrorDefinition(
        code='115',
        description="Date of Local Authority's (LA) decision that a child should be placed for adoption is not a valid date.",
        affected_fields=['DATE_PLACED'],
    )

    def _validate(dfs):
        if 'PlacedAdoption' not in dfs:
            return {}
        else:
            adopt = dfs['PlacedAdoption']
            mask = pd.to_datetime(adopt['DATE_PLACED'], format='%d/%m/%Y', errors='coerce').notna()

            na_location = adopt['DATE_PLACED'].isna()

            validation_error_mask = ~mask & ~na_location
            validation_error_locations = adopt.index[validation_error_mask]

            return {'PlacedAdoption': validation_error_locations.tolist()}

    return error, _validate


def validate_116():
    error = ErrorDefinition(
        code='116',
        description="Date of Local Authority's (LA) decision that a child should no longer be placed for adoption is not a valid date.",
        affected_fields=['DATE_PLACED_CEASED'],
    )

    def _validate(dfs):
        if 'PlacedAdoption' not in dfs:
            return {}
        else:
            adopt = dfs['PlacedAdoption']
            mask = pd.to_datetime(adopt['DATE_PLACED_CEASED'], format='%d/%m/%Y', errors='coerce').notna()

            na_location = adopt['DATE_PLACED_CEASED'].isna()

            validation_error_mask = ~mask & ~na_location
            validation_error_locations = adopt.index[validation_error_mask]

            return {'PlacedAdoption': validation_error_locations.tolist()}

    return error, _validate


def validate_392c():
    error = ErrorDefinition(
        code='392c',
        description='Postcode(s) provided are invalid.',
        affected_fields=['HOME_POST', 'PL_POST'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']

            home_provided = episodes['HOME_POST'].notna()
            home_details = merge_postcodes(episodes, "HOME_POST")
            home_valid = home_details['pcd'].notna()

            pl_provided = episodes['PL_POST'].notna()
            pl_details = merge_postcodes(episodes, "PL_POST")
            pl_valid = pl_details['pcd'].notna()

            error_mask = (home_provided & ~home_valid) | (pl_provided & ~pl_valid)

            return {'Episodes': episodes.index[error_mask].tolist()}

    return error, _validate


def validate_213():
    error = ErrorDefinition(
        code='213',
        description='Placement provider information not required.',
        affected_fields=['PLACE_PROVIDER'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            df = dfs['Episodes']
            mask = df['PLACE'].isin(['T0', 'T1', 'T2', 'T3', 'T4', 'Z1']) & df['PLACE_PROVIDER'].notna()
            return {'Episodes': df.index[mask].tolist()}

    return error, _validate


def validate_168():
    error = ErrorDefinition(
        code='168',
        description='Unique Pupil Number (UPN) is not valid. If unknown, default codes should be UN1, UN2, UN3, UN4 or UN5.',
        affected_fields=['UPN'],
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}
        else:
            df = dfs['Header']
            mask = df['UPN'].str.match(r'(^((?![IOS])[A-Z]){1}(\d{12}|\d{11}[A-Z]{1})$)|^(UN[1-5])$', na=False)
            mask = ~mask & df['UPN'].notnull()
            return {'Header': df.index[mask].tolist()}

    return error, _validate


def validate_388():
    error = ErrorDefinition(
        code='388',
        description='Reason episode ceased is coded new episode begins, but there is no continuation episode.',
        affected_fields=['REC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            df = dfs['Episodes']
            df['DECOM'] = pd.to_datetime(df['DECOM'], format='%d/%m/%Y', errors='coerce')
            df['DEC'] = pd.to_datetime(df['DEC'], format='%d/%m/%Y', errors='coerce')

            df['DECOM'] = df['DECOM'].fillna('01/01/1901')  # Watch for potential future issues
            df = df.sort_values(['CHILD', 'DECOM'])

            df['DECOM_NEXT_EPISODE'] = df.groupby(['CHILD'])['DECOM'].shift(-1)

            # The max DECOM for each child is also the one with no next episode
            # And we also add the skipna option
            # grouped_decom_by_child = df.groupby(['CHILD'])['DECOM'].idxmax(skipna=True)
            no_next = df.DECOM_NEXT_EPISODE.isna() & df.CHILD.notna()

            # Dataframe with the maximum DECOM removed
            max_decom_removed = df[~no_next]
            # Dataframe with the maximum DECOM only
            max_decom_only = df[no_next]

            # Case 1: If reason episode ceased is coded X1 there must be a subsequent episode
            #        starting on the same day.
            case1 = max_decom_removed[(max_decom_removed['REC'] == 'X1') &
                                      (max_decom_removed['DEC'].notna()) &
                                      (max_decom_removed['DECOM_NEXT_EPISODE'].notna()) &
                                      (max_decom_removed['DEC'] != max_decom_removed['DECOM_NEXT_EPISODE'])]

            # Case 2: If an episode ends but the child continues to be looked after, a new
            #        episode should start on the same day.The reason episode ceased code of
            #        the episode which ends must be X1.
            case2 = max_decom_removed[(max_decom_removed['REC'] != 'X1') &
                                      (max_decom_removed['REC'].notna()) &
                                      (max_decom_removed['DEC'].notna()) &
                                      (max_decom_removed['DECOM_NEXT_EPISODE'].notna()) &
                                      (max_decom_removed['DEC'] == max_decom_removed['DECOM_NEXT_EPISODE'])]

            # Case 3: If a child ceases to be looked after reason episode ceased code X1 must
            #        not be used. 
            case3 = max_decom_only[(max_decom_only['DEC'].notna()) &
                                   (max_decom_only['REC'] == 'X1')]

            mask_case1 = case1.index.tolist()
            mask_case2 = case2.index.tolist()
            mask_case3 = case3.index.tolist()

            mask = mask_case1 + mask_case2 + mask_case3

            mask.sort()
            return {'Episodes': mask}

    return error, _validate


def validate_113():
    error = ErrorDefinition(
        code='113',
        description='Date matching child and adopter(s) is not a valid date.',
        affected_fields=['DATE_MATCH'],
    )

    def _validate(dfs):
        if 'AD1' not in dfs:
            return {}
        else:
            ad1 = dfs['AD1']
            mask = pd.to_datetime(ad1['DATE_MATCH'], format='%d/%m/%Y', errors='coerce').notna()

            na_location = ad1['DATE_MATCH'].isna()

            validation_error_mask = ~mask & ~na_location
            validation_error_locations = ad1.index[validation_error_mask]

            return {'AD1': validation_error_locations.tolist()}

    return error, _validate


def validate_134():
    error = ErrorDefinition(
        code='134',
        description='Data on adoption should not be entered for the OC3 cohort.',
        affected_fields=['IN_TOUCH', 'ACTIV', 'ACCOM', 'DATE_INT', 'DATE_MATCH', 'FOSTER_CARE', 'NB_ADOPTR',
                         'SEX_ADOPTR', 'LS_ADOPTR'],
    )

    def _validate(dfs):
        if 'OC3' not in dfs or 'AD1' not in dfs:
            return {}
        else:
            oc3 = dfs['OC3']
            ad1 = dfs['AD1']
            ad1['ad1_index'] = ad1.index

            all_data = ad1.merge(oc3, how='left', on='CHILD')

            na_oc3_data = (
                    all_data['IN_TOUCH'].isna() &
                    all_data['ACTIV'].isna() &
                    all_data['ACCOM'].isna()
            )

            na_ad1_data = (
                    all_data['DATE_INT'].isna() &
                    all_data['DATE_MATCH'].isna() &
                    all_data['FOSTER_CARE'].isna() &
                    all_data['NB_ADOPTR'].isna() &
                    all_data['SEX_ADOPTR'].isna() &
                    all_data['LS_ADOPTR'].isna()
            )

            validation_error = ~na_oc3_data & ~na_ad1_data
            validation_error_locations = all_data.loc[validation_error, 'ad1_index'].unique()

            return {'AD1': validation_error_locations.tolist()}

    return error, _validate


def validate_119():
    error = ErrorDefinition(
        code='119',
        description='If the decision is made that a child should no longer be placed for adoption, then the date of this decision and the reason why this decision was made must be completed.',
        affected_fields=['REASON_PLACED_CEASED', 'DATE_PLACED_CEASED'],
    )

    def _validate(dfs):
        if 'PlacedAdoption' not in dfs:
            return {}
        else:
            adopt = dfs['PlacedAdoption']
            na_placed_ceased = adopt['DATE_PLACED_CEASED'].isna()
            na_reason_ceased = adopt['REASON_PLACED_CEASED'].isna()

            validation_error = (na_placed_ceased & ~na_reason_ceased) | (~na_placed_ceased & na_reason_ceased)
            validation_error_locations = adopt.index[validation_error]

            return {'PlacedAdoption': validation_error_locations.tolist()}

    return error, _validate


def validate_159():
    error = ErrorDefinition(
        code='159',
        description='If a child has been recorded as not receiving an intervention for their substance misuse problem, then the additional item on whether an intervention was offered should be completed as well.',
        affected_fields=['SUBSTANCE_MISUSE', 'INTERVENTION_RECEIVED', 'INTERVENTION_OFFERED'],
    )

    def _validate(dfs):
        if 'OC2' not in dfs:
            return {}
        else:
            oc2 = dfs['OC2']
            mask1 = oc2['SUBSTANCE_MISUSE'].astype(str) == '1'
            mask2 = oc2['INTERVENTION_RECEIVED'].astype(str) == '0'
            mask3 = oc2['INTERVENTION_OFFERED'].isna()

            validation_error = mask1 & mask2 & mask3
            validation_error_locations = oc2.index[validation_error]

            return {'OC2': validation_error_locations.tolist()}

    return error, _validate


def validate_142():
    error = ErrorDefinition(
        code='142',
        description='A new episode has started, but the previous episode has not ended.',
        affected_fields=['DEC', 'REC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            df = dfs['Episodes']
            df['DECOM'] = pd.to_datetime(df['DECOM'], format='%d/%m/%Y', errors='coerce')
            df['DEC'] = pd.to_datetime(df['DEC'], format='%d/%m/%Y', errors='coerce')

            df['DECOM'] = df['DECOM'].fillna('01/01/1901')  # Watch for potential future issues

            df['DECOM'] = df['DECOM'].replace('01/01/1901', pd.NA)

            last_episodes = df.sort_values('DECOM').reset_index().groupby(['CHILD'])['index'].last()
            ended_episodes_df = df.loc[~df.index.isin(last_episodes)]

            ended_episodes_df = ended_episodes_df[(ended_episodes_df['DEC'].isna() | ended_episodes_df['REC'].isna()) &
                                                  ended_episodes_df['CHILD'].notna() & ended_episodes_df[
                                                      'DECOM'].notna()]
            mask = ended_episodes_df.index.tolist()

            return {'Episodes': mask}

    return error, _validate


def validate_148():
    error = ErrorDefinition(
        code='148',
        description='Date episode ceased and reason episode ceased must both be coded, or both left blank.',
        affected_fields=['DEC', 'REC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            df = dfs['Episodes']
            df['DEC'] = pd.to_datetime(df['DEC'], format='%d/%m/%Y', errors='coerce')

            mask = ((df['DEC'].isna()) & (df['REC'].notna())) | ((df['DEC'].notna()) & (df['REC'].isna()))

            return {'Episodes': df.index[mask].tolist()}

    return error, _validate


def validate_151():
    error = ErrorDefinition(
        code='151',
        description='All data items relating to a childs adoption must be coded or left blank.',
        affected_fields=['DATE_INT', 'DATE_MATCH', 'FOSTER_CARE', 'NB_ADOPTER', 'SEX_ADOPTR', 'LS_ADOPTR'],
    )

    def _validate(dfs):
        if 'AD1' not in dfs:
            return {}
        else:
            ad1 = dfs['AD1']
            na_date_int = ad1['DATE_INT'].isna()
            na_date_match = ad1['DATE_MATCH'].isna()
            na_foster_care = ad1['FOSTER_CARE'].isna()
            na_nb_adoptr = ad1['NB_ADOPTR'].isna()
            na_sex_adoptr = ad1['SEX_ADOPTR'].isna()
            na_lsadoptr = ad1['LS_ADOPTR'].isna()

            ad1_not_null = (
                    ~na_date_int & ~na_date_match & ~na_foster_care & ~na_nb_adoptr & ~na_sex_adoptr & ~na_lsadoptr)

            validation_error = (
                                       ~na_date_int | ~na_date_match | ~na_foster_care | ~na_nb_adoptr | ~na_sex_adoptr | ~na_lsadoptr) & ~ad1_not_null
            validation_error_locations = ad1.index[validation_error]

            return {'AD1': validation_error_locations.tolist()}

    return error, _validate


def validate_182():
    error = ErrorDefinition(
        code='182',
        description='Data entries on immunisations, teeth checks, health assessments and substance misuse problem identified should be completed or all OC2 fields should be left blank.',
        affected_fields=['IMMUNISATIONS', 'TEETH_CHECK', 'HEALTH_ASSESSMENT', 'SUBSTANCE_MISUSE', 'CONVICTED',
                         'HEALTH_CHECK', 'INTERVENTION_RECEIVED', 'INTERVENTION_OFFERED'],
    )

    def _validate(dfs):
        if 'OC2' not in dfs:
            return {}
        else:
            oc2 = dfs['OC2']

            mask1 = (
                    oc2['IMMUNISATIONS'].isna() |
                    oc2['TEETH_CHECK'].isna() |
                    oc2['HEALTH_ASSESSMENT'].isna() |
                    oc2['SUBSTANCE_MISUSE'].isna()
            )
            mask2 = (
                    oc2['CONVICTED'].isna() &
                    oc2['HEALTH_CHECK'].isna() &
                    oc2['INTERVENTION_RECEIVED'].isna() &
                    oc2['INTERVENTION_OFFERED'].isna()
            )

            validation_error = mask1 & ~mask2
            validation_error_locations = oc2.index[validation_error]

            return {'OC2': validation_error_locations.tolist()}

    return error, _validate


def validate_214():
    error = ErrorDefinition(
        code='214',
        description='Placement location information not required.',
        affected_fields=['PL_POST', 'URN'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            df = dfs['Episodes']
            mask = df['LS'].isin(['V3', 'V4']) & ((df['PL_POST'].notna()) | (df['URN'].notna()))
            return {'Episodes': df.index[mask].tolist()}

    return error, _validate


def validate_222():
    error = ErrorDefinition(
        code='222',
        description='Ofsted Unique reference number (URN) should not be recorded for this placement type.',
        affected_fields=['URN'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            df = dfs['Episodes']
            place_code_list = ['H5', 'P1', 'P2', 'P3', 'R1', 'R2', 'R5', 'T0', 'T1', 'T2', 'T3', 'T4', 'Z1']
            mask = (df['PLACE'].isin(place_code_list)) & (df['URN'].notna()) & (df['URN'] != 'XXXXXX')
            return {'Episodes': df.index[mask].tolist()}

    return error, _validate


def validate_366():
    error = ErrorDefinition(
        code='366',
        description='A child cannot change placement during the course of an individual short-term respite break.',
        affected_fields=['RNE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            df = dfs['Episodes']
            mask = (df['LS'] == 'V3') & (df['RNE'] != 'S')
            return {'Episodes': df.index[mask].tolist()}

    return error, _validate


def validate_628():
    error = ErrorDefinition(
        code='628',
        description='Motherhood details are not required for care leavers who have not been looked after during the year.',
        affected_fields=['MOTHER'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'Header' not in dfs or 'OC3' not in dfs:
            return {}
        else:
            hea = dfs['Header']
            epi = dfs['Episodes']
            oc3 = dfs['OC3']

            hea = hea.reset_index()
            oc3_no_nulls = oc3[oc3[['IN_TOUCH', 'ACTIV', 'ACCOM']].notna().any(axis=1)]

            hea_merge_epi = hea.merge(epi, how='left', on='CHILD', indicator=True)
            hea_not_in_epi = hea_merge_epi[hea_merge_epi['_merge'] == 'left_only']

            cohort_to_check = hea_not_in_epi.merge(oc3_no_nulls, how='inner', on='CHILD')
            error_cohort = cohort_to_check[cohort_to_check['MOTHER'].notna()]

            error_list = list(set(error_cohort['index'].to_list()))
            error_list.sort()
            return {'Header': error_list}

    return error, _validate


def validate_164():
    error = ErrorDefinition(
        code='164',
        description='Distance is not valid. Please check a valid postcode has been entered.',
        affected_fields=['PL_DISTANCE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            df = dfs['Episodes']
            is_short_term = df['LS'].isin(['V3', 'V4'])
            distance = pd.to_numeric(df['PL_DISTANCE'], errors='coerce')
            # Use a bit of tolerance in these bounds
            distance_valid = distance.gt(-0.2) & distance.lt(1001.0)
            mask = ~is_short_term & ~distance_valid
            return {'Episodes': df.index[mask].tolist()}

    return error, _validate


def validate_169():
    error = ErrorDefinition(
        code='169',
        description='Local Authority (LA) of placement is not valid or is missing. Please check a valid postcode has been entered.',
        affected_fields=['PL_LA'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            df = dfs['Episodes']
            is_short_term = df['LS'].isin(['V3', 'V4'])

            # Because PL_LA is derived, it will always be valid if present
            mask = ~is_short_term & df['PL_LA'].isna()
            return {'Episodes': df.index[mask].tolist()}

    return error, _validate


def validate_179():
    error = ErrorDefinition(
        code='179',
        description='Placement location code is not a valid code.',
        affected_fields=['PL_LOCATION'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            df = dfs['Episodes']
            is_short_term = df['LS'].isin(['V3', 'V4'])

            # Because PL_LOCATION is derived, it will always be valid if present
            mask = ~is_short_term & df['PL_LOCATION'].isna()
            return {'Episodes': df.index[mask].tolist()}

    return error, _validate


def validate_1015():
    error = ErrorDefinition(
        code='1015',
        description='Placement provider is own provision but child not placed in own LA.',
        affected_fields=['PL_LA'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            df = dfs['Episodes']
            local_authority = dfs['metadata']['localAuthority']

            placement_fostering_or_adoption = df['PLACE'].isin([
                'A3', 'A4', 'A5', 'A6', 'U1', 'U2', 'U3', 'U4', 'U5', 'U6',
            ])
            own_provision = df['PLACE_PROVIDER'].eq('PR1')
            is_short_term = df['LS'].isin(['V3', 'V4'])
            is_pl_la = df['PL_LA'].eq(local_authority)

            checked_episodes = ~placement_fostering_or_adoption & ~is_short_term & own_provision
            checked_episodes = checked_episodes & df['LS'].notna() & df['PLACE'].notna()
            mask = checked_episodes & ~is_pl_la

            return {'Episodes': df.index[mask].tolist()}

    return error, _validate


def validate_411():
    error = ErrorDefinition(
        code='411',
        description='Placement location code disagrees with LA of placement.',
        affected_fields=['PL_LOCATION'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            df = dfs['Episodes']
            local_authority = dfs['metadata']['localAuthority']

            mask = df['PL_LOCATION'].eq('IN') & df['PL_LA'].ne(local_authority)

            return {'Episodes': df.index[mask].tolist()}

    return error, _validate


def validate_420():
    error = ErrorDefinition(
        code='420',
        description='LA of placement completed but child is looked after under legal status V3 or V4.',
        affected_fields=['PL_LA'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            df = dfs['Episodes']
            is_short_term = df['LS'].isin(['V3', 'V4'])

            mask = is_short_term & df['PL_LA'].notna()
            return {'Episodes': df.index[mask].tolist()}

    return error, _validate


def validate_355():
    error = ErrorDefinition(
        code='355',
        description='Episode appears to have lasted for less than 24 hours',
        affected_fields=['DECOM', 'DEC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            df = dfs['Episodes']
            mask = df['DECOM'].astype(str) == df['DEC'].astype(str)
            return {'Episodes': df.index[mask].tolist()}

    return error, _validate


def validate_586():
    error = ErrorDefinition(
        code='586',
        description='Dates of missing periods are before child’s date of birth.',
        affected_fields=['MIS_START'],
    )

    def _validate(dfs):
        if 'Missing' not in dfs:
            return {}
        else:
            df = dfs['Missing']
            df['DOB'] = pd.to_datetime(df['DOB'], format='%d/%m/%Y', errors='coerce')
            df['MIS_START'] = pd.to_datetime(df['MIS_START'], format='%d/%m/%Y', errors='coerce')

            error_mask = df['MIS_START'].notna() & (df['MIS_START'] <= df['DOB'])
            return {'Missing': df.index[error_mask].to_list()}

    return error, _validate


def validate_630():
    error = ErrorDefinition(
        code='630',
        description='Information on previous permanence option should be returned.',
        affected_fields=['RNE'],
    )

    def _validate(dfs):
        if 'PrevPerm' not in dfs or 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            pre = dfs['PrevPerm']

            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')
            collection_start = pd.to_datetime(dfs['metadata']['collection_start'], format='%d/%m/%Y', errors='coerce')

            epi = epi.reset_index()

            # Form the episode dataframe which has an 'RNE' of 'S' in this financial year
            epi_has_rne_of_S_in_year = epi[(epi['RNE'] == 'S') & (epi['DECOM'] >= collection_start)]
            # Merge to see
            # 1) which CHILD ids are missing from the PrevPerm file
            # 2) which CHILD are in the prevPerm file, but don't have the LA_PERM/DATE_PERM field completed where they should be
            # 3) which CHILD are in the PrevPerm file, but don't have the PREV_PERM field completed.
            merged_epi_preperm = epi_has_rne_of_S_in_year.merge(pre, on='CHILD', how='left', indicator=True)

            error_not_in_preperm = merged_epi_preperm['_merge'] == 'left_only'
            error_wrong_values_in_preperm = (merged_epi_preperm['PREV_PERM'] != 'Z1') & (
                merged_epi_preperm[['LA_PERM', 'DATE_PERM']].isna().any(axis=1))
            error_null_prev_perm = (merged_epi_preperm['_merge'] == 'both') & (merged_epi_preperm['PREV_PERM'].isna())

            error_mask = error_not_in_preperm | error_wrong_values_in_preperm | error_null_prev_perm

            error_list = merged_epi_preperm[error_mask]['index'].to_list()
            error_list = list(set(error_list))
            error_list.sort()

            return {'Episodes': error_list}

    return error, _validate


def validate_501():
    error = ErrorDefinition(
        code='501',
        description='A new episode has started before the end date of the previous episode.',
        affected_fields=['DECOM', 'DEC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            epi = epi.reset_index()
            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')
            epi['DEC'] = pd.to_datetime(epi['DEC'], format='%d/%m/%Y', errors='coerce')

            epi = epi.sort_values(['CHILD', 'DECOM'])

            epi_lead = epi.shift(1)
            epi_lead = epi_lead.reset_index()

            m_epi = epi.merge(epi_lead, left_on='index', right_on='level_0', suffixes=('', '_prev'))

            error_cohort = m_epi[(m_epi['CHILD'] == m_epi['CHILD_prev']) & (m_epi['DECOM'] < m_epi['DEC_prev'])]
            error_list = error_cohort['index'].to_list()
            error_list.sort()
            return {'Episodes': error_list}

    return error, _validate


def validate_502():
    error = ErrorDefinition(
        code='502',
        description='Last year’s record ended with an open episode. The date on which that episode started does not match the start date of the first episode on this year’s record.',
        affected_fields=['DECOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'Episodes_last' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            epi_last = dfs['Episodes_last']
            epi = epi.reset_index()

            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')
            epi_last['DECOM'] = pd.to_datetime(epi_last['DECOM'], format='%d/%m/%Y', errors='coerce')

            epi_last_no_dec = epi_last[epi_last['DEC'].isna()]

            epi_min_decoms_index = epi[['CHILD', 'DECOM']].groupby(['CHILD'])['DECOM'].idxmin()

            epi_min_decom_df = epi.loc[epi_min_decoms_index, :]

            merged_episodes = epi_min_decom_df.merge(epi_last_no_dec, on='CHILD', how='inner')
            error_cohort = merged_episodes[merged_episodes['DECOM_x'] != merged_episodes['DECOM_y']]

            error_list = error_cohort['index'].to_list()
            error_list = list(set(error_list))
            error_list.sort()

            return {'Episodes': error_list}

    return error, _validate


def validate_153():
    error = ErrorDefinition(
        code='153',
        description="All data items relating to a child's activity or accommodation after leaving care must be coded or left blank.",
        affected_fields=['IN_TOUCH', 'ACTIV', 'ACCOM'],
    )

    def _validate(dfs):
        if 'OC3' not in dfs:
            return {}

        oc3 = dfs['OC3']

        oc3_not_na = (
                oc3['IN_TOUCH'].notna() &
                oc3['ACTIV'].notna() &
                oc3['ACCOM'].notna()
        )

        oc3_all_na = (
                oc3['IN_TOUCH'].isna() &
                oc3['ACTIV'].isna() &
                oc3['ACCOM'].isna()
        )

        validation_error = ~oc3_not_na & ~oc3_all_na

        validation_error_locations = oc3.index[validation_error]

        return {'OC3': validation_error_locations.to_list()}

    return error, _validate


def validate_166():
    error = ErrorDefinition(
        code='166',
        description="Date of review is invalid or blank.",
        affected_fields=['REVIEW'],
    )

    def _validate(dfs):
        if 'Reviews' not in dfs:
            return {}
        else:
            review = dfs['Reviews']

            error_mask = pd.to_datetime(review['REVIEW'], format='%d/%m/%Y', errors='coerce').isna()

            validation_error_locations = review.index[error_mask]

            return {'Reviews': validation_error_locations.to_list()}

    return error, _validate


def validate_174():
    error = ErrorDefinition(
        code='174',
        description="Mother's child date of birth is recorded but gender shows that the child is a male.",
        affected_fields=['SEX', 'MC_DOB'],
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}
        else:
            header = dfs['Header']

            child_is_male = header['SEX'].astype(str) == '1'
            mc_dob_recorded = header['MC_DOB'].notna()

            error_mask = child_is_male & mc_dob_recorded

            validation_error_locations = header.index[error_mask]

            return {'Header': validation_error_locations.to_list()}

    return error, _validate


def validate_180():
    error = ErrorDefinition(
        code='180',
        description="Data entry for the strengths and difficulties questionnaire (SDQ) score is invalid.",
        affected_fields=['SDQ_SCORE'],
    )

    def _validate(dfs):
        if 'OC2' not in dfs:
            return {}
        else:
            oc2 = dfs['OC2']

            oc2['SDQ_SCORE_num'] = pd.to_numeric(oc2['SDQ_SCORE'], errors='coerce')

            error_mask = oc2['SDQ_SCORE'].notna() & ~oc2['SDQ_SCORE_num'].isin(range(41))

            validation_error_locations = oc2.index[error_mask]

            return {'OC2': validation_error_locations.to_list()}

    return error, _validate


def validate_181():
    error = ErrorDefinition(
        code='181',
        description="Data items relating to children looked after continuously for 12 months should be completed with a 0 or 1.",
        affected_fields=['CONVICTED', 'HEALTH_CHECK', 'IMMUNISATIONS', 'TEETH_CHECK', 'HEALTH_ASSESSMENT',
                         'SUBSTANCE_MISUSE', 'INTERVENTION_RECEIVED', 'INTERVENTION_OFFERED'],
    )

    def _validate(dfs):
        if 'OC2' not in dfs:
            return {}
        else:
            oc2 = dfs['OC2']
            code_list = ['0', '1']

            fields_of_interest = ['CONVICTED', 'HEALTH_CHECK', 'IMMUNISATIONS', 'TEETH_CHECK', 'HEALTH_ASSESSMENT',
                                  'SUBSTANCE_MISUSE', 'INTERVENTION_RECEIVED', 'INTERVENTION_OFFERED']

            error_mask = (
                    oc2[fields_of_interest].notna()
                    & ~oc2[fields_of_interest].astype(str).isin(['0', '1'])
            ).any(axis=1)

            validation_error_locations = oc2.index[error_mask]

            return {'OC2': validation_error_locations.tolist()}

    return error, _validate


def validate_192():
    error = ErrorDefinition(
        code='192',
        description="Child has been identified as having a substance misuse problem but the additional item on whether an intervention was received has been left blank.",
        affected_fields=['SUBSTANCE_MISUSE', 'INTERVENTION_RECEIVED'],
    )

    def _validate(dfs):
        if 'OC2' not in dfs:
            return {}
        else:
            oc2 = dfs['OC2']

            misuse = oc2['SUBSTANCE_MISUSE'].astype(str) == '1'
            intervention_blank = oc2['INTERVENTION_RECEIVED'].isna()

            error_mask = misuse & intervention_blank
            validation_error_locations = oc2.index[error_mask]

            return {'OC2': validation_error_locations.to_list()}

    return error, _validate


def validate_193():
    error = ErrorDefinition(
        code='193',
        description="Child not identified as having a substance misuse problem but at least one of the two additional items on whether an intervention were offered and received have been completed.",
        affected_fields=['SUBSTANCE_MISUSE', 'INTERVENTION_RECEIVED', 'INTERVENTION_OFFERED'],
    )

    def _validate(dfs):
        if 'OC2' not in dfs:
            return {}
        else:
            oc2 = dfs['OC2']

            no_substance_misuse = oc2['SUBSTANCE_MISUSE'].isna() | (oc2['SUBSTANCE_MISUSE'].astype(str) == '0')
            intervention_not_blank = oc2['INTERVENTION_RECEIVED'].notna() | oc2['INTERVENTION_OFFERED'].notna()

            error_mask = no_substance_misuse & intervention_not_blank
            validation_error_locations = oc2.index[error_mask]

            return {'OC2': validation_error_locations.tolist()}

    return error, _validate


def validate_197a():
    error = ErrorDefinition(
        code='197a',
        description="Reason for no Strengths and Difficulties (SDQ) score is not required if Strengths and Difficulties Questionnaire score is filled in.",
        affected_fields=['SDQ_SCORE', 'SDQ_REASON'],
    )

    def _validate(dfs):
        if 'OC2' not in dfs:
            return {}
        else:
            oc2 = dfs['OC2']

            sdq_filled_in = oc2['SDQ_SCORE'].notna()
            reason_filled_in = oc2['SDQ_REASON'].notna()

            error_mask = sdq_filled_in & reason_filled_in
            validation_error_locations = oc2.index[error_mask]

            return {'OC2': validation_error_locations.tolist()}

    return error, _validate


def validate_567():
    error = ErrorDefinition(
        code='567',
        description='The date that the missing episode or episode that the child was away from placement without authorisation ended is before the date that it started.',
        affected_fields=['MIS_START', 'MIS_END'],
    )

    def _validate(dfs):
        if 'Missing' not in dfs:
            return {}
        else:
            mis = dfs['Missing']
            mis['MIS_START'] = pd.to_datetime(mis['MIS_START'], format='%d/%m/%Y', errors='coerce')
            mis['MIS_END'] = pd.to_datetime(mis['MIS_END'], format='%d/%m/%Y', errors='coerce')

            mis_error = mis[mis['MIS_START'] > mis['MIS_END']]

            return {'Missing': mis_error.index.to_list()}

    return error, _validate


def validate_304():
    error = ErrorDefinition(
        code='304',
        description='Date unaccompanied asylum-seeking child (UASC) status ceased must be on or before the 18th birthday of a child.',
        affected_fields=['DUC'],
    )

    def _validate(dfs):
        if 'UASC' not in dfs:
            return {}
        else:
            uasc = dfs['UASC']
            uasc['DOB'] = pd.to_datetime(uasc['DOB'], format='%d/%m/%Y', errors='coerce')
            uasc['DUC'] = pd.to_datetime(uasc['DUC'], format='%d/%m/%Y', errors='coerce')
            mask = uasc['DUC'].notna() & (uasc['DUC'] > uasc['DOB'] + pd.offsets.DateOffset(years=18))

            return {'UASC': uasc.index[mask].to_list()}

    return error, _validate


def validate_333():
    error = ErrorDefinition(
        code='333',
        description='Date should be placed for adoption must be on or prior to the date of matching child with adopter(s).',
        affected_fields=['DATE_INT'],
    )

    def _validate(dfs):
        if 'AD1' not in dfs:
            return {}
        else:
            adt = dfs['AD1']
            adt['DATE_MATCH'] = pd.to_datetime(adt['DATE_MATCH'], format='%d/%m/%Y', errors='coerce')
            adt['DATE_INT'] = pd.to_datetime(adt['DATE_INT'], format='%d/%m/%Y', errors='coerce')

            # If <DATE_MATCH> provided, then <DATE_INT> must also be provided and be <= <DATE_MATCH>
            mask1 = adt['DATE_MATCH'].notna() & adt['DATE_INT'].isna()
            mask2 = adt['DATE_MATCH'].notna() & adt['DATE_INT'].notna() & (adt['DATE_INT'] > adt['DATE_MATCH'])
            mask = mask1 | mask2

            return {'AD1': adt.index[mask].to_list()}

    return error, _validate


def validate_1011():
    error = ErrorDefinition(
        code='1011',
        description='This child is recorded as having his/her care transferred to another local authority for the final episode and therefore should not have the care leaver information completed.',
        affected_fields=['IN_TOUCH', 'ACTIV', 'ACCOM'],
    )

    def _validate(dfs):
        if 'OC3' not in dfs or 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            oc3 = dfs['OC3']
            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')

            # If final <REC> = 'E3' then <IN_TOUCH>; <ACTIV> and <ACCOM> should not be provided
            epi.sort_values(['CHILD', 'DECOM'], inplace=True)
            grouped_decom_by_child = epi.groupby(['CHILD'])['DECOM'].idxmax(skipna=True)
            max_decom_only = epi.loc[epi.index.isin(grouped_decom_by_child), :]
            E3_is_last = max_decom_only[max_decom_only['REC'] == 'E3']

            oc3.reset_index(inplace=True)
            cohort_to_check = oc3.merge(E3_is_last, on='CHILD', how='inner')
            error_mask = cohort_to_check[['IN_TOUCH', 'ACTIV', 'ACCOM']].notna().any(axis=1)

            error_list = cohort_to_check['index'][error_mask].to_list()
            error_list = list(set(error_list))
            error_list.sort()

            return {'OC3': error_list}

    return error, _validate


def validate_574():
    error = ErrorDefinition(
        code='574',
        description='A new missing/away from placement without authorisation period cannot start when the previous missing/away from placement without authorisation period is still open. Missing/away from placement without authorisation periods should also not overlap.',
        affected_fields=['MIS_START', 'MIS_END'],
    )

    def _validate(dfs):
        if 'Missing' not in dfs:
            return {}
        else:

            mis = dfs['Missing']
            mis['MIS_START'] = pd.to_datetime(mis['MIS_START'], format='%d/%m/%Y', errors='coerce')
            mis['MIS_END'] = pd.to_datetime(mis['MIS_END'], format='%d/%m/%Y', errors='coerce')

            mis.sort_values(['CHILD', 'MIS_START'], inplace=True)

            mis.reset_index(inplace=True)
            mis.reset_index(inplace=True)  # Twice on purpose

            mis['LAG_INDEX'] = mis['level_0'].shift(-1)

            lag_mis = mis.merge(mis, how='inner', left_on='level_0', right_on='LAG_INDEX', suffixes=['', '_PREV'])

            # We're only interested in cases where there is more than one row for a child.
            lag_mis = lag_mis[lag_mis['CHILD'] == lag_mis['CHILD_PREV']]

            # A previous MIS_END date is null
            mask1 = lag_mis['MIS_END_PREV'].isna()
            # MIS_START is before previous MIS_END (overlapping dates)
            mask2 = lag_mis['MIS_START'] < lag_mis['MIS_END_PREV']

            mask = mask1 | mask2

            error_list = lag_mis['index'][mask].to_list()
            error_list.sort()
            return {'Missing': error_list}

    return error, _validate


def validate_564():
    error = ErrorDefinition(
        code='564',
        description='Child was missing or away from placement without authorisation and the date started is blank.',
        affected_fields=['MISSING', 'MIS_START'],
    )

    def _validate(dfs):
        if 'Missing' not in dfs:
            return {}
        else:
            mis = dfs['Missing']
            error_mask = mis['MISSING'].isin(['M', 'A', 'm', 'a']) & mis['MIS_START'].isna()
            return {'Missing': mis.index[error_mask].to_list()}

    return error, _validate


def validate_566():
    error = ErrorDefinition(
        code='566',
        description='The date that the child' + chr(
            39) + 's episode of being missing or away from placement without authorisation ended has been completed but whether the child was missing or away without authorisation has not been completed.',
        affected_fields=['MISSING', 'MIS_END'],
    )

    def _validate(dfs):
        if 'Missing' not in dfs:
            return {}
        else:
            mis = dfs['Missing']
            error_mask = mis['MISSING'].isna() & mis['MIS_END'].notna()
            return {'Missing': mis.index[error_mask].to_list()}

    return error, _validate


def validate_436():
    error = ErrorDefinition(
        code='436',
        description='Reason for new episode is that both child’s placement and legal status have changed, but this is not reflected in the episode data.',
        affected_fields=['RNE', 'LS', 'PLACE', 'PL_POST', 'URN', 'PLACE_PROVIDER'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:

            epi = dfs['Episodes']
            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')

            epi.sort_values(['CHILD', 'DECOM'], inplace=True)
            epi.reset_index(inplace=True)
            epi.reset_index(inplace=True)
            epi['LAG_INDEX'] = epi['level_0'].shift(-1)
            epi.fillna(value={"LS": '*', "PLACE": '*', "PL_POST": '*', "URN": '*', "PLACE_PROVIDER": '*'}, inplace=True)
            epi_merge = epi.merge(epi, how='inner', left_on='level_0', right_on='LAG_INDEX', suffixes=['', '_PRE'])

            epi_multi_row = epi_merge[epi_merge['CHILD'] == epi_merge['CHILD_PRE']]
            epi_has_B_U = epi_multi_row[epi_multi_row['RNE'].isin(['U', 'B'])]

            mask_ls = epi_has_B_U['LS'] == epi_has_B_U['LS_PRE']

            mask1 = epi_has_B_U['PLACE'] == epi_has_B_U['PLACE_PRE']
            mask2 = epi_has_B_U['PL_POST'] == epi_has_B_U['PL_POST_PRE']
            mask3 = epi_has_B_U['URN'] == epi_has_B_U['URN_PRE']
            mask4 = epi_has_B_U['PLACE_PROVIDER'] == epi_has_B_U['PLACE_PROVIDER_PRE']

            error_mask = mask_ls | (mask1 & mask2 & mask3 & mask4)

            error_list = epi_has_B_U[error_mask]['index'].to_list()
            error_list.sort()
            return {'Episodes': error_list}

    return error, _validate


def validate_570():
    error = ErrorDefinition(
        code='570',
        description='The date that the child started to be missing or away from placement without authorisation is after the end of the collection year.',
        affected_fields=['MIS_START'],
    )

    def _validate(dfs):
        if 'Missing' not in dfs:
            return {}
        else:
            mis = dfs['Missing']
            collection_end = pd.to_datetime(dfs['metadata']['collection_end'], format='%d/%m/%Y', errors='coerce')

            mis['MIS_START'] = pd.to_datetime(mis['MIS_START'], format='%d/%m/%Y', errors='coerce')
            error_mask = mis['MIS_START'] > collection_end

            return {'Missing': mis.index[error_mask].to_list()}

    return error, _validate


def validate_531():
    error = ErrorDefinition(
        code='531',
        description='A placement provider code of PR5 cannot be associated with placements P1.',
        affected_fields=['PLACE', 'PLACE_PROVIDER'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            error_mask = (epi['PLACE'] == 'P1') & (epi['PLACE_PROVIDER'] == 'PR5')
            return {'Episodes': epi.index[error_mask].to_list()}

    return error, _validate


def validate_542():
    error = ErrorDefinition(
        code='542',
        description='A child aged under 10 at 31 March should not have conviction information completed.',
        affected_fields=['CONVICTED'],
    )

    def _validate(dfs):
        if 'OC2' not in dfs:
            return {}
        else:
            oc2 = dfs['OC2']
            oc2['DOB'] = pd.to_datetime(oc2['DOB'], format='%d/%m/%Y', errors='coerce')
            collection_end = pd.to_datetime(dfs['metadata']['collection_end'], format='%d/%m/%Y', errors='coerce')
            error_mask = (oc2['DOB'] + pd.offsets.DateOffset(years=10) > collection_end) & oc2['CONVICTED'].notna()
            return {'OC2': oc2.index[error_mask].to_list()}

    return error, _validate


def validate_620():
    error = ErrorDefinition(
        code='620',
        description='Child has been recorded as a mother, but date of birth shows that the mother is under 11 years of age.',
        affected_fields=['DOB', 'MOTHER'],
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}
        else:
            hea = dfs['Header']
            collection_start = pd.to_datetime(dfs['metadata']['collection_start'], format='%d/%m/%Y', errors='coerce')
            hea['DOB'] = pd.to_datetime(hea['DOB'], format='%d/%m/%Y', errors='coerce')

            hea_mother = hea[hea['MOTHER'].astype(str) == '1']
            error_cohort = (hea_mother['DOB'] + pd.offsets.DateOffset(years=11)) > collection_start

            return {'Header': hea_mother.index[error_cohort].to_list()}

    return error, _validate


def validate_225():
    error = ErrorDefinition(
        code='225',
        description='Reason for placement change must be recorded.',
        affected_fields=['REASON_PLACE_CHANGE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')
            epi.sort_values(['CHILD', 'DECOM'], inplace=True)
            epi.reset_index(inplace=True)
            epi.reset_index(inplace=True)
            epi['LAG_INDEX'] = epi['level_0'].shift(1)
            m_epi = epi.merge(epi, how='inner', left_on='level_0', right_on='LAG_INDEX', suffixes=['', '_NEXT'])
            m_epi = m_epi[m_epi['CHILD'] == m_epi['CHILD_NEXT']]

            mask_is_X1 = m_epi['REC'] == 'X1'
            mask_null_place_chg = m_epi['REASON_PLACE_CHANGE'].isna()
            mask_place_not_T = ~m_epi['PLACE'].isin(['T0', 'T1', 'T2', 'T3', 'T4'])
            mask_next_is_PBTU = m_epi['RNE_NEXT'].isin(['P', 'B', 'T', 'U'])
            mask_next_place_not_T = ~m_epi['PLACE_NEXT'].isin(['T0', 'T1', 'T2', 'T3', 'T4'])

            error_mask = mask_is_X1 & mask_null_place_chg & mask_place_not_T & mask_next_is_PBTU & mask_next_place_not_T

            error_list = m_epi['index'][error_mask].to_list()
            return {'Episodes': error_list}

    return error, _validate


def validate_353():
    error = ErrorDefinition(
        code='353',
        description='No episode submitted can start before 14 October 1991.',
        affected_fields=['DECOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')
            min_decom_allowed = pd.to_datetime('14/10/1991', format='%d/%m/%Y', errors='coerce')
            error_mask = epi['DECOM'] < min_decom_allowed
            return {'Episodes': epi.index[error_mask].to_list()}

    return error, _validate


def validate_528():
    error = ErrorDefinition(
        code='528',
        description='A placement provider code of PR2 cannot be associated with placements P1, R2 or R5.',
        affected_fields=['PLACE', 'PLACE_PROVIDER'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            error_mask = (epi['PLACE'].isin(['P1', 'R2', 'R5'])) & (epi['PLACE_PROVIDER'] == 'PR2')
            return {'Episodes': epi.index[error_mask].to_list()}

    return error, _validate


def validate_527():
    error = ErrorDefinition(
        code='527',
        description='A placement provider code of PR1 cannot be associated with placements P1, R2 or R5.',
        affected_fields=['PLACE', 'PLACE_PROVIDER'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            error_mask = (epi['PLACE'].isin(['P1', 'R2', 'R5'])) & (epi['PLACE_PROVIDER'] == 'PR1')
            return {'Episodes': epi.index[error_mask].to_list()}

    return error, _validate


def validate_359():
    error = ErrorDefinition(
        code='359',
        description='Child being looked after following 18th birthday must be accommodated under section 20(5) of the Children Act 1989 in a community home.',
        affected_fields=['DEC', 'LS', 'PLACE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'Header' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            hea = dfs['Header']
            hea['DOB'] = pd.to_datetime(hea['DOB'], format='%d/%m/%Y', errors='coerce')
            collection_end = pd.to_datetime(dfs['metadata']['collection_end'], format='%d/%m/%Y', errors='coerce')

            epi.reset_index(inplace=True)
            epi = epi.merge(hea, on='CHILD', how='left', suffixes=['', '_HEA'])

            mask_older_18 = (epi['DOB'] + pd.offsets.DateOffset(years=18)) < collection_end
            mask_null_dec = epi['DEC'].isna()
            mask_is_V2_K2 = (epi['LS'] == 'V2') & (epi['PLACE'] == 'K2')

            error_mask = mask_older_18 & mask_null_dec & ~mask_is_V2_K2
            error_list = epi['index'][error_mask].to_list()
            error_list = list(set(error_list))

            return {'Episodes': error_list}

    return error, _validate


def validate_562():
    error = ErrorDefinition(
        code='562',
        description='Episode commenced before the start of the current collection year but there is a missing continuous episode in the previous year.',
        affected_fields=['DECOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'Episodes_last' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            epi_last = dfs['Episodes_last']
            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')
            epi_last['DECOM'] = pd.to_datetime(epi_last['DECOM'], format='%d/%m/%Y', errors='coerce')
            collection_start = pd.to_datetime(dfs['metadata']['collection_start'], format='%d/%m/%Y', errors='coerce')

            epi.reset_index(inplace=True)
            epi = epi[epi['DECOM'] < collection_start]

            grp_decom_by_child = epi.groupby(['CHILD'])['DECOM'].idxmin(skipna=True)
            min_decom = epi.loc[epi.index.isin(grp_decom_by_child), :]

            grp_last_decom_by_child = epi_last.groupby(['CHILD'])['DECOM'].idxmax(skipna=True)
            max_last_decom = epi_last.loc[epi_last.index.isin(grp_last_decom_by_child), :]

            merged_co = min_decom.merge(max_last_decom, how='left', on=['CHILD', 'DECOM'], suffixes=['', '_PRE'],
                                        indicator=True)
            error_cohort = merged_co[merged_co['_merge'] == 'left_only']

            error_list = error_cohort['index'].to_list()
            error_list = list(set(error_list))
            error_list.sort()
            return {'Episodes': error_list}

    return error, _validate


def validate_354():
    error = ErrorDefinition(
        code='354',
        description="Date episode ceased must be on or before the end of the current collection year.",
        affected_fields=['DECOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            collection_end = pd.to_datetime(dfs['metadata']['collection_end'], format='%d/%m/%Y', errors='coerce')
            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')
            error_mask = epi['DECOM'] > collection_end
            error_list = epi.index[error_mask].to_list()
            return {'Episodes': error_list}

    return error, _validate


def validate_385():
    error = ErrorDefinition(
        code='385',
        description="Date episode ceased must be on or before the end of the current collection year.",
        affected_fields=['DEC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            collection_end = pd.to_datetime(dfs['metadata']['collection_end'], format='%d/%m/%Y', errors='coerce')
            epi['DEC'] = pd.to_datetime(epi['DEC'], format='%d/%m/%Y', errors='coerce')
            error_mask = epi['DEC'] > collection_end
            error_list = epi.index[error_mask].to_list()
            return {'Episodes': error_list}

    return error, _validate


def validate_408():
    error = ErrorDefinition(
        code='408',
        description='Child is placed for adoption with a placement order, but no placement order has been recorded.',
        affected_fields=['PLACE', 'LS'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            error_mask = epi['PLACE'].isin(['A5', 'A6']) & (epi['LS'] != 'E1')
            return {'Episodes': epi.index[error_mask].to_list()}

    return error, _validate


def validate_380():
    error = ErrorDefinition(
        code='380',
        description='A period of care cannot start with a temporary placement.',
        affected_fields=['PLACE', 'RNE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            error_mask = (epi['PLACE'].isin(['T0', 'T1', 'T2', 'T3', 'T4'])) & (~epi['RNE'].isin(['P', 'B']))
            return {'Episodes': epi.index[error_mask].to_list()}

    return error, _validate


def validate_381():
    error = ErrorDefinition(
        code='381',
        description='A period of care cannot end with a temporary placement.',
        affected_fields=['PLACE', 'REC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            error_mask = (epi['PLACE'].isin(['T0', 'T1', 'T2', 'T3', 'T4'])) & (epi['REC'] != 'X1') & (
                epi['REC'].notna())
            return {'Episodes': epi.index[error_mask].to_list()}

    return error, _validate


def validate_504():
    error = ErrorDefinition(
        code='504',
        description='The category of need code differs from that reported at start of current period of being looked after',
        affected_fields=['CIN'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')
            epi['DEC'] = pd.to_datetime(epi['DEC'], format='%d/%m/%Y', errors='coerce')

            epi.sort_values(['CHILD', 'DECOM'], inplace=True)
            epi.reset_index(inplace=True)
            epi.reset_index(inplace=True)
            epi['LAG_INDEX'] = epi['level_0'].shift(1)

            merge_epi = epi.merge(epi, how='inner', left_on='LAG_INDEX', right_on='level_0', suffixes=['', '_PRE'])
            merge_epi = merge_epi[merge_epi['CHILD'] == merge_epi['CHILD_PRE']]
            merge_epi = merge_epi[(merge_epi['REC_PRE'] == 'X1') & (merge_epi['DEC_PRE'] == merge_epi['DECOM'])]
            error_cohort = merge_epi[merge_epi['CIN'] != merge_epi['CIN_PRE']]
            error_list = error_cohort['index'].unique().tolist()
            error_list.sort()
            return {'Episodes': error_list}

    return error, _validate


def validate_431():
    error = ErrorDefinition(
        code='431',
        description='The reason for new episode is started to be looked after, but the previous episode ended on the same day.',
        affected_fields=['RNE', 'DECOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')
            epi['DEC'] = pd.to_datetime(epi['DEC'], format='%d/%m/%Y', errors='coerce')
            epi.sort_values(['CHILD', 'DECOM'], inplace=True)

            epi.reset_index(inplace=True)
            epi.reset_index(inplace=True)
            epi['LAG_INDEX'] = epi['level_0'].shift(-1)

            m_epi = epi.merge(epi, how='inner', left_on='level_0', right_on='LAG_INDEX', suffixes=['', '_PREV'])

            m_epi = m_epi[(m_epi['CHILD'] == m_epi['CHILD_PREV']) & (m_epi['RNE'] == 'S')]
            error_mask = m_epi['DECOM'] <= m_epi['DEC_PREV']
            error_list = m_epi['index'][error_mask].to_list()
            error_list.sort()
            return {'Episodes': error_list}

    return error, _validate


def validate_503_Generic(subval):
    Gen_503_dict = {
        "A": {
            "Desc": "The reason for new episode in the first episode does not match open episode at end of last year.",
            "Fields": 'RNE'},
        "B": {"Desc": "The legal status in the first episode does not match open episode at end of last year.",
              "Fields": 'LS'},
        "C": {"Desc": "The category of need in the first episode does not match open episode at end of last year.",
              "Fields": 'CIN'},
        "D": {"Desc": "The placement type in the first episode does not match open episode at end of last year",
              "Fields": 'PLACE'},
        "E": {"Desc": "The placement provider in the first episode does not match open episode at end of last year.",
              "Fields": 'PLACE_PROVIDER'},
        "F": {"Desc": "The Ofsted URN in the  first episode does not match open episode at end of last year.",
              "Fields": 'URN'},
        "G": {"Desc": "The distance in first episode does not match open episode at end of last year.",
              "Fields": 'PL_DISTANCE'},
        "H": {"Desc": "The placement LA in first episode does not match open episode at end of last year.",
              "Fields": 'PL_LA'},
        "J": {"Desc": "The placement location in first episode does not match open episode at end of last year.",
              "Fields": 'PL_LOCATION'},
    }
    error = ErrorDefinition(
        code='503' + subval,
        description=Gen_503_dict[subval]['Desc'],
        affected_fields=[Gen_503_dict[subval]['Fields']],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'Episodes_last' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            epi_last = dfs['Episodes_last']
            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')
            epi_last['DECOM'] = pd.to_datetime(epi_last['DECOM'], format='%d/%m/%Y', errors='coerce')

            epi.reset_index(inplace=True)

            grp_decom_by_child = epi.groupby(['CHILD'])['DECOM'].idxmin(skipna=True)
            min_decom = epi.loc[epi.index.isin(grp_decom_by_child), :]

            grp_last_decom_by_child = epi_last.groupby(['CHILD'])['DECOM'].idxmax(skipna=True)
            max_last_decom = epi_last.loc[epi_last.index.isin(grp_last_decom_by_child), :]

            merged_co = min_decom.merge(max_last_decom, how='inner', on=['CHILD', 'DECOM'], suffixes=['', '_PRE'])

            this_one = Gen_503_dict[subval]['Fields']
            pre_one = this_one + '_PRE'

            if subval == 'G':
                err_mask = abs(merged_co[this_one].astype(float) - merged_co[pre_one].astype(float)) >= 0.2
            else:
                err_mask = merged_co[this_one].astype(str) != merged_co[pre_one].astype(str)

            err_list = merged_co['index'][err_mask].unique().tolist()
            err_list.sort()
            return {'Episodes': err_list}

    return error, _validate


def validate_503A():
    return validate_503_Generic('A')


def validate_503B():
    return validate_503_Generic('B')


def validate_503C():
    return validate_503_Generic('C')


def validate_503D():
    return validate_503_Generic('D')


def validate_503E():
    return validate_503_Generic('E')


def validate_503F():
    return validate_503_Generic('F')


def validate_503G():
    return validate_503_Generic('G')


def validate_503H():
    return validate_503_Generic('H')


def validate_503J():
    return validate_503_Generic('J')


def validate_526():
    error = ErrorDefinition(
        code='526',
        description='Child is missing a placement provider code for at least one episode.',
        affected_fields=['PLACE', 'PLACE_PROVIDER'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            error_mask = ~epi['PLACE'].isin(['T0', 'T1', 'T2', 'T3', 'T4', 'Z1']) & epi['PLACE_PROVIDER'].isna()
            return {'Episodes': epi.index[error_mask].to_list()}

    return error, _validate


def validate_370to376and379(subval):
    Gen_370_dict = {
        "370": {"Desc": "Child in independent living should be at least 15.",
                "P_Code": 'P2', "Y_gap": 15},
        "371": {"Desc": "Child in semi-independent living accommodation not subject to children’s homes regulations " +
                        "should be at least 14.",
                "P_Code": 'H5', "Y_gap": 14},
        "372": {"Desc": "Child in youth custody or prison should be at least 10.",
                "P_Code": 'R5', "Y_gap": 10},
        "373": {"Desc": "Child placed in a school should be at least 4 years old.",
                "P_Code": 'S1', "Y_gap": 4},
        "374": {"Desc": "Child in residential employment should be at least 14 years old.",
                "P_Code": 'P3', "Y_gap": 14},
        "375": {"Desc": "Hospitalisation coded as a temporary placement exceeds six weeks.",
                "P_Code": 'T1', "Y_gap": 42},
        "376": {"Desc": "Temporary placements coded as being due to holiday of usual foster carer(s) cannot exceed " +
                        "three weeks.",
                "P_Code": 'T3', "Y_gap": 21},
        "379": {"Desc": "Temporary placements for unspecified reason (placement code T4) cannot exceed seven days.",
                "P_Code": 'T4', "Y_gap": 7},
    }
    error = ErrorDefinition(
        code=str(subval),
        description=Gen_370_dict[subval]['Desc'],
        affected_fields=['DECOM', 'PLACE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'Header' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            hea = dfs['Header']
            hea['DOB'] = pd.to_datetime(hea['DOB'], format='%d/%m/%Y', errors='coerce')
            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')
            epi['DEC'] = pd.to_datetime(epi['DEC'], format='%d/%m/%Y', errors='coerce')
            epi.reset_index(inplace=True)
            epi_p2 = epi[epi['PLACE'] == Gen_370_dict[subval]['P_Code']]
            merged_e = epi_p2.merge(hea, how='inner', on='CHILD')
            merged_e = merged_e.dropna(subset=['DECOM', 'DEC', 'DOB'])
            if subval in ['370', '371', '372', '373', '374']:
                error_mask = merged_e['DECOM'] < (merged_e['DOB'] +
                                                  pd.offsets.DateOffset(years=Gen_370_dict[subval]['Y_gap']))
            else:
                error_mask = merged_e['DEC'] > (merged_e['DECOM'] +
                                                pd.offsets.DateOffset(days=Gen_370_dict[subval]['Y_gap']))
            return {'Episodes': merged_e['index'][error_mask].unique().tolist()}

    return error, _validate


def validate_370():
    return validate_370to376and379('370')


def validate_371():
    return validate_370to376and379('371')


def validate_372():
    return validate_370to376and379('372')


def validate_373():
    return validate_370to376and379('373')


def validate_374():
    return validate_370to376and379('374')


def validate_375():
    return validate_370to376and379('375')


def validate_376():
    return validate_370to376and379('376')


def validate_379():
    return validate_370to376and379('379')


def validate_529():
    error = ErrorDefinition(
        code='529',
        description='Placement provider code of PR3 cannot be associated with placements P1, A3 to A6, K1, K2 and U1 to U6 as these placements cannot be provided by other public organisations.',
        affected_fields=['PLACE', 'PLACE_PROVIDER'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            code_list_placement_type = ['A3', 'A4', 'A5', 'A6', 'K1', 'K2', 'P1', 'U1', 'U2', 'U3', 'U4', 'U5', 'U6']
            error_mask = epi['PLACE'].isin(code_list_placement_type) & (epi['PLACE_PROVIDER'] == 'PR3')
            return {'Episodes': epi.index[error_mask].to_list()}

    return error, _validate


def validate_383():
    error = ErrorDefinition(
        code='383',
        description='A child in a temporary placement must subsequently return to his/her normal placement.',
        affected_fields=['PLACE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')
            epi.sort_values(['CHILD', 'DECOM'], inplace=True)

            epi.reset_index(inplace=True)
            epi.reset_index(inplace=True)
            epi['LAG_INDEX'] = epi['level_0'].shift(-1)
            epi['LEAD_INDEX'] = epi['level_0'].shift(1)

            m_epi = epi.merge(epi, how='inner', left_on='level_0', right_on='LAG_INDEX', suffixes=['', '_TOP'])
            m_epi = m_epi.merge(epi, how='inner', left_on='level_0', right_on='LEAD_INDEX', suffixes=['', '_BOTM'])
            m_epi = m_epi[m_epi['CHILD'] == m_epi['CHILD_TOP']]
            m_epi = m_epi[m_epi['CHILD'] == m_epi['CHILD_BOTM']]
            m_epi = m_epi[m_epi['PLACE'].isin(['T0', 'T1', 'T2', 'T3', 'T4'])]

            mask1 = m_epi['RNE_BOTM'] != 'P'
            mask2 = m_epi['PLACE_BOTM'] != m_epi['PLACE_TOP']
            err_mask = mask1 | mask2
            err_list = m_epi['index'][err_mask].unique().tolist()
            err_list.sort()
            return {'Episodes': err_list}

    return error, _validate


def validate_377():
    error = ErrorDefinition(
        code='377',
        description='Only two temporary placements coded as being due to holiday of usual foster carer(s) are ' +
                    'allowed in any 12- month period.',
        affected_fields=['PLACE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')
            epi.reset_index(inplace=True)

            potent_cohort = epi[epi['PLACE'] == 'T3']

            # Here I'm after the CHILD ids where there are more than 2 T3 placements.
            count_them = potent_cohort.groupby('CHILD')['CHILD'].count().to_frame(name='cc')
            count_them.reset_index(inplace=True)
            count_them = count_them[count_them['cc'] > 2]

            err_coh = epi[epi['CHILD'].isin(count_them['CHILD'])]
            err_coh = err_coh[err_coh['PLACE'] == 'T3']

            err_list = err_coh['index'].unique().tolist()
            err_list.sort()
            return {'Episodes': err_list}

    return error, _validate


# !# Potential false negatives - if child has no missing periods in current year's Missing table nothing is flagged!
def validate_576():
    error = ErrorDefinition(
        code='576',
        description='There is an open missing/away from placement without authorisation period in ' +
                    'last year’s return and there is no corresponding period recorded at the start of ' +
                    'this year.',
        affected_fields=['CHILD'],
    )

    def _validate(dfs):
        if 'Missing' not in dfs or 'Missing_last' not in dfs:
            return {}
        else:
            mis = dfs['Missing']
            mis_l = dfs['Missing_last']
            mis['MIS_START'] = pd.to_datetime(mis['MIS_START'], format='%d/%m/%Y', errors='coerce')
            mis_l['MIS_START'] = pd.to_datetime(mis_l['MIS_START'], format='%d/%m/%Y', errors='coerce')

            mis.reset_index(inplace=True)
            mis['MIS_START'].fillna(pd.to_datetime('01/01/2099', format='%d/%m/%Y', errors='coerce'), inplace=True)
            min_mis = mis.groupby(['CHILD'])['MIS_START'].idxmin()
            mis = mis.loc[min_mis, :]

            open_mis_l = mis_l.query("MIS_END.isnull()")

            err_coh = mis.merge(open_mis_l, how='left', on='CHILD', suffixes=['', '_LAST'])
            err_coh = err_coh.query("(MIS_START != MIS_START_LAST) & MIS_START_LAST.notnull()")

            err_list = err_coh['index'].unique().tolist()
            err_list.sort()
            return {'Missing': err_list}

    return error, _validate


def validate_553():
    error = ErrorDefinition(
        code='553',
        description='Placement order has been granted but there is no date of decision that the child should ' +
                    'be placed for adoption.',
        affected_fields=['CHILD', 'DATE_PLACED', 'DATE_PLACED_CEASED', 'REASON_PLACED_CEASED'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'PlacedAdoption' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            sho = dfs['PlacedAdoption']
            sho.reset_index(inplace=True)
            epi.reset_index(inplace=True)

            epi_has_e1 = epi[epi['LS'] == 'E1']
            merge_w_sho = epi_has_e1.merge(sho, how='left', on='CHILD', suffixes=['_EP', '_PA'], indicator=True)

            # E1 episodes without a corresponding PlacedAdoption entry
            err_list_epi = merge_w_sho.query("(_merge == 'left_only')")['index_EP'].unique().tolist()

            # Open E1 Episodes where DATE_PLACED_CEASED or REASON_PLACED_CEASED is filled in
            epi_open_e1 = epi[(epi['LS'] == 'E1') & epi['DEC'].isna()]
            merge_w_sho2 = epi_open_e1.merge(sho, how='inner', on='CHILD', suffixes=['_EP', '_PA'])
            err_list_sho = merge_w_sho2['index_PA'][merge_w_sho2['DATE_PLACED_CEASED'].notna()
                                                    | merge_w_sho2['REASON_PLACED_CEASED'].notna()]
            err_list_sho = err_list_sho.unique().tolist()
            return {'Episodes': err_list_epi, 'PlacedAdoption': err_list_sho}

    return error, _validate


def validate_555():
    error = ErrorDefinition(
        code='555',
        description='Freeing order has been granted but there is no date of decision that the child should ' +
                    'be placed for adoption.',
        affected_fields=['CHILD', 'DATE_PLACED', 'DATE_PLACED_CEASED', 'REASON_PLACED_CEASED'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'PlacedAdoption' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            sho = dfs['PlacedAdoption']
            sho.reset_index(inplace=True)
            epi.reset_index(inplace=True)

            # D1 episodes without a corresponding PlacedAdoption entry
            epi_has_d1 = epi[epi['LS'] == 'D1']
            merge_w_sho = epi_has_d1.merge(sho, how='left', on='CHILD', suffixes=['_EP', '_PA'], indicator=True)
            err_list_epi = merge_w_sho.query("_merge == 'left_only'")['index_EP'].unique().tolist()

            # Open D1 Episodes where DATE_PLACED_CEASED or REASON_PLACED_CEASED is filled in
            epi_open_d1 = epi[(epi['LS'] == 'D1') & epi['DEC'].isna()]
            merge_w_sho2 = epi_open_d1.merge(sho, how='inner', on='CHILD', suffixes=['_EP', '_PA'])
            err_list_sho = merge_w_sho2['index_PA'][merge_w_sho2['DATE_PLACED_CEASED'].notna()
                                                    | merge_w_sho2['REASON_PLACED_CEASED'].notna()]
            err_list_sho = err_list_sho.unique().tolist()
            return {'Episodes': err_list_epi, 'PlacedAdoption': err_list_sho}

    return error, _validate


def validate_382():
    error = ErrorDefinition(
        code='382',
        description='A child receiving respite care cannot be in a temporary placement.',
        affected_fields=['LS', 'PLACE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            err_list = epi.query("LS.isin(['V3', 'V4']) & PLACE.isin(['T0', 'T1', 'T2', 'T3', 'T4'])").index.tolist()
            return {'Episodes': err_list}

    return error, _validate


def validate_602():
    error = ErrorDefinition(
        code='602',
        description='The episode data submitted for this child does not show that he/she was adopted during the year.',
        affected_fields=['CHILD'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'AD1' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            ad1 = dfs['AD1']
            epi['DEC'] = pd.to_datetime(epi['DEC'], format='%d/%m/%Y', errors='coerce')
            collection_start = pd.to_datetime(dfs['metadata']['collection_start'], format='%d/%m/%Y', errors='coerce')
            collection_end = pd.to_datetime(dfs['metadata']['collection_end'], format='%d/%m/%Y', errors='coerce')

            mask1 = (epi['DEC'] <= collection_end) & (epi['DEC'] >= collection_start)
            mask2 = epi['REC'].isin(['E11', 'E12'])
            adoption_eps = epi[mask1 & mask2]

            adoption_fields = ['DATE_INT', 'DATE_MATCH', 'FOSTER_CARE', 'NB_ADOPTR', 'SEX_ADOPTR', 'LS_ADOPTR']

            err_list = (ad1
                        .reset_index()
                        .merge(adoption_eps, how='left', on='CHILD', indicator=True)
                        .query("_merge == 'left_only'")
                        .dropna(subset=adoption_fields, how='all')
                        .set_index('index')
                        .index
                        .unique()
                        .to_list())

            return {'AD1': err_list}

    return error, _validate


def validate_580():
    error = ErrorDefinition(
        code='580',
        description='Child is missing when cease being looked after but reason episode ceased not ‘E8’.',
        affected_fields=['REC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'Missing' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            mis = dfs['Missing']
            mis['MIS_END'] = pd.to_datetime(mis['MIS_END'], format='%d/%m/%Y', errors='coerce')
            mis['DOB'] = pd.to_datetime(mis['DOB'], format='%d/%m/%Y', errors='coerce')
            epi['DEC'] = pd.to_datetime(epi['DEC'], format='%d/%m/%Y', errors='coerce')

            epi.reset_index(inplace=True)
            mis['BD18'] = mis['DOB'] + pd.DateOffset(years=18)

            m_coh = mis.merge(epi, how='inner', on='CHILD')
            m_coh = m_coh.query("(BD18 == MIS_END) & (MIS_END == DEC) & DEC.notnull()")
            err_list = m_coh.query("REC != 'E8'")['index'].unique().tolist()
            err_list.sort()
            return {'Episodes': err_list}

    return error, _validate


def validate_575():
    error = ErrorDefinition(
        code='575',
        description='If the placement from which the child goes missing/away from placement without ' +
                    'authorisation ends, the missing/away from placement without authorisation period in ' +
                    'the missing module must also have an end date.',
        affected_fields=['MIS_END'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'Missing' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            mis = dfs['Missing']

            mis.reset_index(inplace=True)

            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')
            epi['DEC'] = pd.to_datetime(epi['DEC'], format='%d/%m/%Y', errors='coerce')
            mis['MIS_START'] = pd.to_datetime(mis['MIS_START'], format='%d/%m/%Y', errors='coerce')

            m_coh = epi.merge(mis, how='inner', on='CHILD') \
                .query("(MIS_START >= DECOM) & (MIS_START <= DEC) & MIS_END.isnull() & DEC.notnull()")

            err_list = m_coh['index'].unique().tolist()
            err_list.sort()
            return {'Missing': err_list}

            return {'Episodes': Episodes_errs,
                    'AD1': AD1_errs}

    return error, _validate


def validate_1012():
    error = ErrorDefinition(
        code='1012',
        description='No other data should be returned for OC3 children who had no episodes in the current year',
        affected_fields=['CHILD'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}

        epi = dfs['Episodes']

        error_dict = {}
        for table in ['PlacedAdoption', 'Missing', 'Reviews', 'AD1', 'PrevPerm', 'OC2']:
            if table in dfs.keys():
                df = dfs[table]
                error_dict[table] = (
                    df
                        .reset_index()
                        .merge(epi, how='left', on='CHILD', indicator=True)
                        .query("_merge == 'left_only'")
                    ['index'].unique()
                        .tolist()
                )
        return error_dict

    return error, _validate


def validate_432():
    error = ErrorDefinition(
        code='432',
        description='The child ceased to be looked after at the end of the previous episode but the reason for ' +
                    'the new episode is not started to be looked after.',
        affected_fields=['RNE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']

            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')

            epi.sort_values(['CHILD', 'DECOM'], inplace=True)
            epi.reset_index(inplace=True)
            epi.reset_index(inplace=True)

            rec_vals1 = ['E2', 'E3', 'E4A', 'E4B', 'E5', 'E6', 'E7', 'E8', 'E9', 'E11']
            rec_vals2 = ['E12', 'E13', 'E14', 'E15', 'E16', 'E17', 'E41', 'E45', 'E46', 'E47', 'E48']
            rec_vals = rec_vals1 + rec_vals2

            epi['LAG'] = epi['level_0'].shift(-1)

            err_co = epi.merge(epi, how='inner', left_on='level_0', right_on='LAG', suffixes=['', '_PRE']) \
                .query("CHILD == CHILD_PRE & REC_PRE.isin(@rec_vals) & RNE != 'S'")

            err_list = err_co['index'].unique().tolist()
            err_list.sort()

            return {'Episodes': err_list}

    return error, _validate


def validate_331():
    error = ErrorDefinition(
        code='331',
        description='Date of matching child and adopter(s) should be the same as, or prior to, the date of placement of adoption.',
        affected_fields=['DATE_MATCH',  # AD1
                         'DECOM', 'REC'],  # Episodes
    )

    def _validate(dfs):
        if 'AD1' not in dfs or 'Episodes' not in dfs:
            return {}
        else:
            adt = dfs['AD1']
            eps = dfs['Episodes']

            # Save indexes of each table so we can retreive the original positions in each for our error rows
            adt['AD1_index'] = adt.index
            eps['Episodes_index'] = eps.index

            adt['DATE_MATCH'] = pd.to_datetime(adt['DATE_MATCH'], format='%d/%m/%Y', errors='coerce')
            eps['DECOM'] = pd.to_datetime(eps['DECOM'], format='%d/%m/%Y', errors='coerce')

            # Only keep the episodes where <Adopted> = 'Y'
            adoption_eps = eps[eps['REC'].isin(['E11', 'E12'])]

            # Merge AD1 and Episodes so we can compare DATE_MATCH and DECOM
            adoption_eps = adoption_eps.merge(adt, on='CHILD')

            # A child cannot be placed for adoption before the child has been matched with prospective adopter(s).
            error_mask = adoption_eps['DATE_MATCH'] > adoption_eps['DECOM']

            # Get the rows of each table where the dates clash
            AD1_errs = list(adoption_eps.loc[error_mask, 'AD1_index'].unique())
            Episodes_errs = list(adoption_eps.loc[error_mask, 'Episodes_index'].unique())

            return {'AD1': AD1_errs,
                    'Episodes': Episodes_errs}

    return error, _validate


def validate_362():
    error = ErrorDefinition(
        code='362',
        description='Emergency protection order (EPO) lasted longer than 21 days',
        affected_fields=['DECOM', 'LS', 'DEC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']

            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')
            epi['DEC'] = pd.to_datetime(epi['DEC'], format='%d/%m/%Y', errors='coerce')
            collection_end = pd.to_datetime(dfs['metadata']['collection_end'], format='%d/%m/%Y', errors='coerce')

            epi.sort_values(['CHILD', 'DECOM'], inplace=True)
            epi.reset_index(inplace=True)
            epi.reset_index(inplace=True)

            epi['LAG'] = epi['level_0'] - 1

            epi['DEC'].fillna(collection_end, inplace=True)

            err_co = epi.merge(epi, how='left', left_on='level_0', right_on='LAG', suffixes=['', '_NEXT']) \
                .query("LS == 'L2'")

            # Create a partition "FLOWS" for two or more separate flow sequences of L2 code dates within the same child.
            # when the dec / decom_next dates stop flowing or the child id changes
            # the cumsum is incremented this can then be used as the partition.
            err_co['FLOWS'] = (err_co['DEC'] == err_co['DECOM_NEXT']) & (err_co['CHILD'] == err_co['CHILD_NEXT'])
            err_co['FLOWS'] = err_co['FLOWS'].shift(1)
            err_co['FLOWS'].fillna(False, inplace=True)
            err_co['FLOWS'] = ~err_co['FLOWS']
            err_co['FLOWS'] = err_co['FLOWS'].astype(int).cumsum()

            # Calc the min decom and max dec in each group so the days between them can be calculated.
            grp_decom = err_co.groupby(['CHILD', 'FLOWS'])['DECOM'].min().to_frame(name='MIN_DECOM').reset_index()
            grp_dec = err_co.groupby(['CHILD', 'FLOWS'])['DEC'].max().to_frame(name='MAX_DEC').reset_index()
            grp_len_l2 = grp_decom.merge(grp_dec, how='inner', on=['CHILD', 'FLOWS'])

            # Throw out anything <= 21 days.
            grp_len_l2['DAY_DIF'] = (grp_len_l2['MAX_DEC'] - grp_len_l2['MIN_DECOM']).dt.days
            grp_len_l2 = grp_len_l2.query("DAY_DIF > 21").copy()

            # Inner join back to the err_co and get the original index out.
            err_co['MERGE_KEY'] = err_co['CHILD'].astype(str) + err_co['FLOWS'].astype(str)
            grp_len_l2['MERGE_KEY'] = grp_len_l2['CHILD'].astype(str) + grp_len_l2['FLOWS'].astype(str)
            err_final = err_co.merge(grp_len_l2, how='inner', on=['MERGE_KEY'], suffixes=['', '_IG'])

            err_list = err_final['index'].unique().tolist()
            err_list.sort()

            return {'Episodes': err_list}

    return error, _validate


def validate_361():
    error = ErrorDefinition(
        code='361',
        description='Police protection legal status lasted longer than maximum 72 hours allowed ' +
                    'in the Children Act 1989.',
        affected_fields=['DECOM', 'LS', 'DEC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']

            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')
            epi['DEC'] = pd.to_datetime(epi['DEC'], format='%d/%m/%Y', errors='coerce')
            collection_end = pd.to_datetime(dfs['metadata']['collection_end'], format='%d/%m/%Y', errors='coerce')

            epi.sort_values(['CHILD', 'DECOM'], inplace=True)
            epi.reset_index(inplace=True)
            epi.reset_index(inplace=True)

            epi['LAG'] = epi['level_0'] - 1

            epi['DEC'].fillna(collection_end, inplace=True)

            err_co = epi.merge(epi, how='left', left_on='level_0', right_on='LAG', suffixes=['', '_NEXT']) \
                .query("LS == 'L1'")

            # Create a partition "FLOWS" for two or more separate flow sequences of L2 code dates within the same child.
            # when the dec / decom_next dates stop flowing or the child id changes
            # the cumsum is incremented this can then be used as the partition.
            err_co['FLOWS'] = (err_co['DEC'] == err_co['DECOM_NEXT']) & (err_co['CHILD'] == err_co['CHILD_NEXT'])
            err_co['FLOWS'] = err_co['FLOWS'].shift(1)
            err_co['FLOWS'].fillna(False, inplace=True)
            err_co['FLOWS'] = ~err_co['FLOWS']
            err_co['FLOWS'] = err_co['FLOWS'].astype(int).cumsum()

            # Calc the min decom and max dec in each group so the days between them can be calculated.
            grp_decom = err_co.groupby(['CHILD', 'FLOWS'])['DECOM'].min().to_frame(name='MIN_DECOM').reset_index()
            grp_dec = err_co.groupby(['CHILD', 'FLOWS'])['DEC'].max().to_frame(name='MAX_DEC').reset_index()
            grp_len_l2 = grp_decom.merge(grp_dec, how='inner', on=['CHILD', 'FLOWS'])

            # Throw out anything <= 3 days.
            grp_len_l2['DAY_DIF'] = (grp_len_l2['MAX_DEC'] - grp_len_l2['MIN_DECOM']).dt.days
            grp_len_l2 = grp_len_l2.query("DAY_DIF > 3").copy()

            # Inner join back to the err_co and get the original index out.
            err_co['MERGE_KEY'] = err_co['CHILD'].astype(str) + err_co['FLOWS'].astype(str)
            grp_len_l2['MERGE_KEY'] = grp_len_l2['CHILD'].astype(str) + grp_len_l2['FLOWS'].astype(str)
            err_final = err_co.merge(grp_len_l2, how='inner', on=['MERGE_KEY'], suffixes=['', '_IG'])

            err_list = err_final['index'].unique().tolist()
            err_list.sort()

            return {'Episodes': err_list}

    return error, _validate


def validate_435():
    error = ErrorDefinition(
        code='435',
        description='Reason for new episode is that child’s placement has changed but not the legal status, ' +
                    'but this is not reflected in the episode data recorded.',
        affected_fields=['LS', 'PLACE', 'PL_POST', 'URN', 'PLACE_PROVIDER'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')
            epi.sort_values(['CHILD', 'DECOM'], inplace=True)
            epi['idx_orig'] = epi.index
            epi.reset_index(inplace=True)
            epi['idx_ordered'] = epi.index
            epi['idx_previous'] = epi.index + 1

            err_co = epi.merge(epi, how='inner', left_on='idx_ordered', right_on='idx_previous', suffixes=['', '_PRE']) \
                .query("RNE.isin(['P', 'T']) & CHILD == CHILD_PRE") \
                .query("(LS != LS_PRE) | ((PLACE == PLACE_PRE) & (PL_POST == PL_POST_PRE) & (URN == URN_PRE) & " +
                       "(PLACE_PROVIDER == PLACE_PROVIDER_PRE))")

            err_list = err_co['idx_orig'].unique().tolist()
            err_list.sort()

            return {'Episodes': err_list}

    return error, _validate


# !# False positives if child was UASC in last 2 years but data not provided
def validate_392B():
    error = ErrorDefinition(
        code='392B',
        description='Child is looked after but no postcodes are recorded. [NOTE: This check may result in false positives for children formerly UASC]',
        affected_fields=['HOME_POST', 'PL_POST'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            epi['orig_idx'] = epi.index
            if 'UASC' in dfs:
                uas = dfs['UASC']
                err_co = epi.merge(uas, how='left', on='CHILD', indicator=True).query("_merge == 'left_only'")
                err_co.drop(['_merge'], axis=1, inplace=True)
            if 'UASC_last' in dfs:
                uas_l = dfs['UASC_last']
                err_co = err_co.merge(uas_l, how='left', on='CHILD', indicator=True).query("_merge == 'left_only'")

            err_co = err_co.query("(~LS.isin(['V3','V4'])) & (HOME_POST.isna() | PL_POST.isna())")
            err_list = err_co['orig_idx'].unique().tolist()
            err_list.sort()

            return {'Episodes': err_list}

    return error, _validate
