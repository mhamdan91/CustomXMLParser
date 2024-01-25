__version__ = "1.1.0"
__author__ = "Muhammad Hamdan <mhamdan.prod@gmail.com>"
__copyright__ = """
BSD 3-Clause License

Copyright (c) 2023, Muhammad Hamdan, and Intel Corporation
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

LONG_DESCRIPTION="""
Custom XML to Dict Parser
==============================
## Table of Contents

 * [Overview](#overview)
 * [Library Installalion](#library-installalion)
 * [Library Usage](#library-usage)
 * [Config file](#config-file)


## Overview
This package allows you to parse XML files. The tool uses the `xml2dict` package to parse XML files in raw format and returns data as a python dictionary and builds on that to provide custom tailoring of what information to return from the XML file. In other words, with a configuration file, you can return specific data from the XML file in a specific format.

## Library Installalion
To install the library simply run the following command in a cmd, shell or whatever...

```bash
# It's recommended to create a virtual environment

# Windows
pip install CustomXMLParser

# Linux
pip3 install CustomXMLParser
```

## Library usage?

### Example usage
If you wish to read the XML file as is and simply convert it to a python dictionary, then do the following:
```python
from CustomXMLParser import XmlParser

xml_parser = XmlParser(parser_type='raw')
xml_file = 'path_to_xml_file'
xml_dict = xml_parser.parse(xml_file)
```

If you wish to dump a dict to XML file or a string, then do the following:
```python
from CustomXMLParser import XmlParser
xml_parser = XmlParser(parser_type='raw')
xml_file = 'path_to_xml_file'
xml_dict = xml_parser.parse(xml_file)
my_dict = manipulate(xml_dict) # Manipulate raw dict, but MUST maintain structure
out_xml_file = 'path_to_out_xml_file'
xml_parser.dump(out_xml_file, my_dict, pretty=True) # This dump dict to xml file
my_xml_string = xml_parser.dumps(data, pretty=True) # This dumps dict to a string
```


If you wish to read specific portions of the XML file and format them in a particular way, then do the following:
```python
from CustomXMLParser import XmlParser

config_file = 'path_to_config_file'
xml_parser = XmlParser(config_file=config_file, parser_type='custom')
xml_file = 'path_to_xml_file'
xml_dict = xml_parser.parse(xml_file)
```

If you wish to dump a any dict to XML file or a string, then do the following:
```python
from CustomXMLParser import XmlParser
xml_parser = XmlParser(parser_type='raw')
xml_file = 'path_to_xml_file'
xml_dict = xml_parser.parse(xml_file)
my_dict = manipulate(xml_dict)... # Manipulate raw dict, but MUST maintain structure
out_xml_file = 'path_to_out_xml_file'
xml_parser.dump(my_dict, out_xml_file, input_format='custom', root='root', pretty=True) # This dump dict to xml file
my_xml_string = xml_parser.dumps(my_dict, input_format='custom', root='root', pretty=True) # This dumps dict to a string
```


Note, the `XmlParser` class uses the following default XML attributes

```python
'''
name_key (str, optional): this is a custom/xml configuration parameter, and it is the name of primary tag. Defaults to "@name".
table_key (str, optional): this is a custom/xml configuration parameter, and it is the table identifier. Defaults to "th".
header_key (str, optional): this is a custom/xml configuration parameter, and it is the header identifier. Defaults to 'header'.
data_key (str, optional): this is a custom/xml configuration parameter, and it is the data identifier. Defaults to "rows".
header_text_key (str, optional): this is a custom/xml configuration parameter, and it is the table's key identifier. Defaults to "#text".
'''
```

You can override those attributes by passing them to the constructor of the `XmlParser` class as follows:

```python
from CustomXMLParser import XmlParser

config_file = 'path_to_config_file'
xml_parser = XmlParser(config_file=config_file, parser_type='custom', encoding='utf-8',
                       name_key='<desired_name_key>', table_key='<desired_table_key>', header_key='<desired_header_keyr>',
                       data_key='<desired_data_key>', header_text_key='<desired_header_text_key>')
xml_file = 'path_to_xml_file'
xml_dict = xml_parser.parse(xml_file)
```

## Config file

Below shows an example of configurations for custom parsing of XML.

```json
{
  "TREE":{
    "TABLE_A": {},
    "TABLE_B": {"TABLE_C": {"KEYS": "key1,key2"}}
  },

  "TABLE_A":
    [
      "element0_tag,element0_name",
      "element1_tag,element1_name"
    ],
  "TABLE_B":
    [
      "element0_tag*,element1_tag*,element2_tag,element2_name"
    ],
  "TABLE_C":
    [
      "element0_tag,element0_name"
    ]
}

```

### General Rules
- Capitalize all dictionary keys.
- \* is wildcard notation: returns data for all available elements

### Tree structure
The structure can be flat or nested. If you wish to return child data for a particular parent, then you have to include the child as value for the parent. For example, parent **TABLE_B** has child **TABLE_C**. If **TABLE_C** has a child of its own, then we add it to **TABLE_C** in the same way.

```yaml
REQUESTING_SPECIFIC_KEYS:
  notice that **TABLE_C** specifies a key called `KEYS` and a value of `key1,key2`.
  This configuration allows you to only return matching keys `key1` and `key2` for *TABLE_C*.
  If the `KEYS` key is not specified, then all keys are returned by default.
  The `KEYS` key must be unique and is not present in the XML file. If it is present,
  then user can change the default key name through class attributes.

```

### Data structure
Let's make some assumptions about elements to make this example easy to follow.
- For **TABLE_A**, assume element0_tag and element1_tag map to `table`, element0_name to `info`, and element1_name to `metadata`.
- For **TABLE_B**, assume element0_tag maps to `container`, element1_tag to `node`, and element2_tag to `table`, and element2_name to `info`.
- For **TABLE_C**, assume element0_tag maps to `table` and element0_name to `images`

In the above config example, we are interested in returning data for **TABLE_A**, **TABLE_B**, AND **TABLE_C**.
For each key, a path or a list of paths (xpath) is/are required to be provided in order to retrieve data from the XML file. For example:
- **TABLE_A** has two paths ["table,info", "table,metadata"], data under `info` and `metadata` tables will be returned and stored in *TABLE_A*
- **TABLE_B** has single path ["container*,node*,table,images"], data under `info` table for all nodes and all containers will be returned and stored in *TABLE_B*.
- **TABLE_C** has single path ["table,images"], data under `images` table for all parent nodes and containers will be returned and stored in *TABLE_C*. 

```yaml
NOTICE:
  full path isn't required for **TABLE_C** and the *GFC* (greatest common factor) between the child **TABLE_C**,
  and the parent **TABLE_B** is only required in the parent table. Since **TABLE_C** is a child of **TABLE_B**,
  it falls under the same path, but **TABLE_C** breaks away at "table,images" and that's why it is the only specified path.
  In other words, since **TABLE_C** is a child of **TABLE_B**, all *TABLE_B* rules carry over to *TABLE_C*. 
```

----------------------------------------
Author: Hamdan, Muhammad (@mhamdan - ©)

"""