# This file was used to check the functioning of the backend before the command line tool was built.

from validator903.validator import Validator
from validator903.report import Report
from validator903.types import UploadedFile

#import logging
#logger = logging.getLogger('validator903.validator')
#logger.setLevel(logging.INFO)
#logger.addHandler(logging.StreamHandler())

p4a_path = '/workspaces/quality-lac-data-beta-validator/tests/fake_data/placed_for_adoption_errors.csv'
ad1_path = '/workspaces/quality-lac-data-beta-validator/tests/fake_data/ad1.csv'

# construct 'files' list of dicts (nb filetexts are bytes not str)
with open(p4a_path, 'rb') as f:
    p4a_filetext = f.read()

with open(ad1_path, 'rb') as f:
    ad1_filetext = f.read()

files_list = [
    UploadedFile(name=p4a_path, description='This year', file_content=p4a_filetext),
    UploadedFile(name=ad1_path, description='This year', file_content=ad1_filetext),
]

# the rest of the metadata is added in read_from_text() when instantiating Validator
metadata = {'collectionYear': '2022',
            'localAuthority': 'E09000027'}
# Richmond: E09000027 // Wandsworth: E09000032 (https://www.richmond.gov.uk/wandsworth)
# (not that it should matter for this)

# create the validator object
v = Validator(metadata=metadata, files=files_list)

# list of error codes to validate
# 523 seemed to cause the exception // 115 checks DATE_PLACED is a date // 101 needs Header table
errs = ['523', '115', '101']
# invalid date as an example
#v.dfs['PlacedAdoption'].loc[2, 'DATE_PLACED'] = 'JUS CHECKIN'

results = v.validate(errs)

# print(results)

print()
print('skipped:', v.skips)
print('done:', v.dones)
print('errd:', v.fails)
print()
print('-- AD1 Columns --')
print(results['AD1'].columns)
print()
print(results['AD1'], ['DATE_PLACED', 'ERR_523'])
print('-- PlacedAdoption Columns --')
print(results['PlacedAdoption'].columns)
print()
print(results['PlacedAdoption'], ['DATE_PLACED', 'ERR_523'])

r = Report(results)
print(r.report)
print(r.error_report)
print(r.error_summary)