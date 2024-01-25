import os
from CustomXMLParser import XmlParser

tdx_file = os.path.join('unittest', 'test_data', 'test_dx.XML')
config_file = os.path.join('unittest', 'test_data', 'CONFIG_EXAMPLE.json')

parser = XmlParser(config_file=config_file, parser_type='custom', verbose=False)
data = parser.parse(tdx_file)

out_tdx = tdx_file.replace('.XML', '_mod.XML')
parser.dump(data, out_tdx, input_format='custom', root='root')

print("Done!!")