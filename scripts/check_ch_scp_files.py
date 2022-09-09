#Used when testing amended ingress function for amended file formats.
from validator903.ingress import construct_provider_info_table

print(construct_provider_info_table('./CH2.xlsx', './SCP2.xlsx').columns)