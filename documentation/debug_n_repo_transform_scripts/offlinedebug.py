# This file was used to check the functioning of the backend before the command line tool was built.

from validator903.validator import Validator
from lac_validator.report import Report
from lac_validator.types import UploadedFile

#import logging
#logger = logging.getLogger('validator903.validator')
#logger.setLevel(logging.INFO)
#logger.addHandler(logging.StreamHandler())

# p4a_path = '/workspaces/quality-lac-data-beta-validator/tests/fake_data/placed_for_adoption_errors.csv'
# ad1_path = '/workspaces/quality-lac-data-beta-validator/tests/fake_data/ad1.csv'

p4a_path = 'tests\\fake_data\episodes.csv'
ad1_path = 'tests\\fake_data\header.csv'

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
lac_rule_codes = ['1000', '1001', '1002', '1003', '1004', '1005', '1006', '1007', '1008', '1009', '101', '1010', '1011', '1012', '1014', '1015', '102', '103', '104', '105', '112', '113', '114', '115', '116', '117', '118', '119', '120', '131', '132', '133', '134', '141', '142', '143', '144', '145', '146', '147', '148', '149', '151', '153', '157', '158', '159', '164', '165', '166', '167', '168', '169', '171', '174', '175', '176', '177', '178', '179', '180', '181', '182', '184', '185', '186', '187', '188', '189', '190', '191', '192', '193', '196', '197a', '197B', '198', '199', '202', '203', '204', '205A', '205B', '205C', '205D', '207', '208', '209', '210', '213', '214', '215', '217', '218', '219', '221', '222', '224', '225', '226', '227', '228', '229', '3001', '301', '302', '303', '304', '331', '333', '334', '335', '336', '344', '345', '351', '352', '353', '354', '355', '356', '357', '358', '359', '361', '362', '363', '364', '365', '366', '367', '370', '371', '372', '373', '374', '375', '376', '377', '378', '379', '380', '381', '382', '383', '384', '385', '386', '387', '388', '389', '390', '391', '392A', '392B', '392c', '393', '398', '399', '406', '407', '408', '411', '420', '426', '431', '432', '433', '434', '435', '436', '437', '440', '441', '442', '445', '446', '451', '452', '453', '460', '501', '502', '503A', '503B', '503C', '503D', '503E', '503F', '503G', '503H', '503J', '504', '511', '514', '516', '517', '518', '519', '520', '521', '522', '523', '524', '525', '526', '527', '528', '529', '530', '531', '542', '543', '544', '545', '546', '547', '550', '551', '552', '553', '554', '555', '556', '557', '558', '559', '560', '561', '562', '563', '564', '565', '566', '567', '570', '571', '574', '575', '576', '577', '578', '579', '580', '586', '601', '602', '607', '611', '612', '620', '621', '624', '625', '626', '628', '630', '631', '632', '633', '634', '635', 'EPI', 'INT01', 'INT02', 'INT03', 'INT04', 'INT05', 'INT06', 'INT07', 'INT08', 'INT09', 'INT11', 'INT12', 'INT13', 'INT14', 'INT15', 'INT16', 'INT17', 'INT18', 'INT21', 'INT31', 'INT32', 'INT33', 'INT34', 'INT35', 'INT36', 'NoE']

# invalid date as an example
#v.dfs['PlacedAdoption'].loc[2, 'DATE_PLACED'] = 'JUS CHECKIN'

# results = v.validate(errs)
results = v.validate(lac_rule_codes)

print(results)

# print()
# print('skipped:', v.skips)
# print('done:', v.dones)
# print('errd:', v.fails)
# print()
# print('-- AD1 Columns --')
# print(results['AD1'].columns)
# print()
# print(results['AD1'], ['DATE_PLACED', 'ERR_523'])
# print('-- PlacedAdoption Columns --')
# print(results['PlacedAdoption'].columns)
# print()
# print(results['PlacedAdoption'], ['DATE_PLACED', 'ERR_523'])

r = Report(results)
print(f"*****************Report******************")
print(r.report)
print(f"*****************Error report******************")
print(r.error_report)
print(f"****************Error summary******************")
print(r.error_summary)