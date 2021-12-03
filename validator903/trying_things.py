def validate_1014():
error = ErrorDefinition(
    code = '1014',
    description = 'UASC information is not required for care leavers',
    affected_fields = ['ACTIV', 'ACCOM', 'IN_TOUCH', 'DECOM']
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

      #episodes['EPS'] = (episodes['DECOM']>=collection_start) & (episodes['DECOM']<=collection_end)
      #episodes['EPS_COUNT'] = episodes.groupby('CHILD')['EPS'].transform('count')
      
    # Take only episodes of children which are also found on the uasc table
      merged = episodes.merge(uasc, on='CHILD', how='inner', suffixes=['_eps', '_er']).merge(oc3, on='CHILD', how='left')

      # eps_in_year = (merged['EPS_COUNT']==0)
      eps_in_year = (episodes['DECOM']>=collection_start) & (episodes['DECOM']<=collection_end) 
      some_provided = (merged['ACTIV'].notna() | merged['ACCOM'].notna()| merged['IN_TOUCH'].notna())
      # If <IN_TOUCH>, <ACTIV> or <ACCOM> are provided AND count of the current collection year's episodes = 0 the <UASC> must be '0' and <DUC> must be Null.
      mask = ~(eps_in_year) & some_provided
      # That is, if 
      error_locations = header.index[mask]

      return {'Header':error_locations.tolist()}
  return error, _validate