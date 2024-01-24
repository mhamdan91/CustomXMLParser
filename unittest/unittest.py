import os
from CustomXMLParser import XmlParser
from dicttoxml import dicttoxml as dtx
import xml.dom.minidom
from typing import Dict, List

tdx_file = os.path.join('unittest', 'test_data', 'test_dx.XML')
config_file = os.path.join('unittest', 'test_data', 'TDX_CONFIG_CIM_CAMTEK_2.0.0.json')

parser = XmlParser(config_file=config_file, parser_type='custom', verbose=False)
data = parser.parse(tdx_file)

out_tdx = tdx_file.replace('.XML', '_mod.XML')
xmlout = parser.dumps(data, input_format='custom', root='root')
# xmlout = parser.dump(data, out_tdx, input_format='custom', root='root')

with open(out_tdx, 'w') as of:
    of.write(xmlout)

print()