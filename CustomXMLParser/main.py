import time
import json
import xmltodict
import xml.dom.minidom
import xml.etree.ElementTree as ET
from copy import deepcopy
from typing import Dict, List, Tuple, Union
from moecolor import print

from .version import LONG_DESCRIPTION

Dict4 = Dict[str, Dict[str, Dict[str, Dict[str, Dict]]]]


class ParserError(Exception):
    def __init__(self, error):
        self.error = error

    def __str__(self):
        return self.error

class MissingItems(ParserError):
    """
    Raised when the item or more are element are missing
    """

class XmlParser:
    """
    Class that parses xml documents and converts them into json objects. It accepts an xml file and optionally
    a configuration file for custom formatting. Parser types available are [raw, custom]. Raw for basic xml to json
    conversion, and custom for xml to custom format conversion

    Methods
    -------
    parse(file=str): Parses an input xml file and converts it into a dictionary
    """
    def __init__(self, config_file: str="", parser_type: str="raw", tree_idn: str='TREE', keys_idn: str='KEYS',
                encoding: str="utf-8", name_key: str="@name", table_key: str="th", header_key: str='header',
                data_key: str="rows", header_text_key: str="#text", verbose: bool=True) -> None:
        """
            Constructs all the necessary attributes for the XmlParser object.
        Args:
            config_file (str, optional): configuration file for custom formatting. Defaults to "". If not specified, the parser
            will return a json dictionary without custom formatting.
            parser_type (str, optional): type of parsing (custom: for xml to json using custom config, raw: for xml to json). Defaults to "raw".
            tree_idn (str, optional): Key identifier of the tree configuration dictionary in config file. Defaults to "TREE".
            keys_idn (str, optional): Key identifier of the requested keys per dictionary configuration in config file. Defaults to "KEYS".
            encoding (str, optional): character encoding of xml file . Defaults to "utf-8".
            name_key (str, optional): this is a custom/xml configuration parameter, and it is the name of primary tag. Defaults to "@name".
            table_key (str, optional): this is a custom/xml configuration parameter, and it is the table identifier. Defaults to "th".
            header_key (str, optional): this is a custom/xml configuration parameter, and it is the header identifier. Defaults to 'header'.
            data_key (str, optional): this is a custom/xml configuration parameter, and it is the data identifier. Defaults to "rows".
            header_text_key (str, optional): this is a custom/xml configuration parameter, and it is the table's key identifier. Defaults to "#text".
        Raises:
            ERROR on wrong parser type
        """
        if parser_type not in ["raw", "custom"]:
            raise ValueError(f"[ERROR] received invalid parser_type [{parser_type}]. Valid options [raw, custom].")

        self._parser_type: str = parser_type
        self._config_file: str = config_file
        self._encoding: str = encoding
        self._tree_idn: str = tree_idn
        self._keys_idn: str = keys_idn
        self._tree_config: Dict4 = {}
        self._raw_tree_config: Dict4 = {}
        self._target_keys_dict: Dict[str, str] = {}
        self._config: Dict = self.load_file(config_file, 'utf-8', 'json') if config_file else {}
        # custom keys configuration, can be set only once per instance - no setter or getter...
        self.name_key = name_key
        self.table_key = table_key
        self.header_key = header_key
        self.data_key = data_key
        self.header_text_key = header_text_key
        self.verbose = verbose

    def __repr__(self) -> str:
        return f'\n{self.__class__.__name__}(config_file={self._config_file!r}, parser_type={self._parser_type!r}, encoding={self._encoding!r}, '   \
               f'name_key={self.name_key}, table_key={self.table_key}, header_key={self.header_key}, data_key={self.data_key}, '                    \
               f'header_text_key={self.header_text_key})'

    @property
    def config_file(self):
        return self._config_file
    @config_file.setter
    def config_file(self, config_file: str=""):
        self._config_file = config_file

    @property
    def parser_type(self):
        return self._parser_type
    @parser_type.setter
    def parser_type(self, parser_type: str="raw"):
        if parser_type not in ["raw", "custom"]:
            raise ValueError(f"[ERROR] received invalid parser_type [{parser_type}]. Valid options [raw, custom].")
        self._parser_type = parser_type

    @property
    def encoding(self):
        return self._encoding
    @encoding.setter
    def encoding(self, encoding: str="raw"):
        self._encoding = encoding

    def _print(self, text: str, color: str, verbose: bool=False, **kwargs):
        verbose = verbose or self.verbose
        if verbose:
            print(text, color=color, **kwargs)

    def load_file(self, file: str, encoding: str='', doc_type: str='xml') -> Dict:
        try:
            encoding = encoding or self.encoding
            with open(file, encoding=encoding) as f:
                return xmltodict.parse(f.read()) if doc_type == 'xml' else json.load(f)
        except Exception as e:
            self._print(f"Failed to load file `{e}`", color='red')
            return {}

    def xml_to_dict(self, in_d: Dict4, out_d: Dict4={}):
        if self.data_key in in_d:  # This means we're at the bottom...
            element_name = in_d[self.name_key]
            out_d[element_name] = {}
            raw_header: List[Dict] = in_d.get(self.header_key, {}).get(self.table_key, [])
            if in_d.get(self.data_key) and raw_header:
                rows = list(zip(*[row.split(',') for row in in_d.get(self.data_key, '').split('\n')]))
                if len(rows) == len(raw_header):
                    for i, _dict in enumerate(raw_header):
                        out_d[element_name][_dict.get(self.header_text_key)] = rows[i]
                missing_element = self.data_key if len(rows) < len(raw_header) else self.header_key
                self._print(f"Header and rows for [{element_name}] do not match. " \
                            f"[{missing_element}] is incomplete.", color='red')
            return out_d

        for key, value in in_d.items():  # recurse the dict...
            if isinstance(value, dict):
                sub_dict = self.xml_to_dict(value, {})
                if self.name_key in in_d:
                    out_d[next(iter(out_d))].update({key: sub_dict})
                else:
                    out_d[key] = sub_dict
            elif isinstance(value, list):
                dict_list = {key: {}}
                for v in value:
                    dict_list[key].update(self.xml_to_dict(v, {}))  # v is assumed a dictionary...
                if out_d:
                    out_d[next(iter(out_d))].update(dict_list)
                else:
                    out_d.update(dict_list)
            elif value:
                out_d[value] = {}

        return out_d

    def dict_to_xml(self, data: Dict, pretty: bool=False, root: str='root',
                header: str="<?xml version='1.0' encoding='utf-8'?>"):

            def _dict_to_xml(element: List, data: Dict):
                for key, value in data.items():
                    item_element = ET.Element(key)
                    element.append(item_element)
                    if isinstance(value, dict):
                        _dict_to_xml(item_element, value)
                    elif isinstance(value, list):
                        _list_to_xml(item_element, value)
                    else:
                        item_element.text = str(value)

            def _list_to_xml(element: List, data_list: Union[dict, list]):
                for item in data_list:
                    item_element = ET.Element('item')
                    element.append(item_element)
                    if isinstance(item, (dict, list)):
                        _dict_to_xml(item_element, item)
                    else:
                        item_element.text = str(item)

            def _prettify_xml(xml_string: str) -> str:
                dom = xml.dom.minidom.parseString(xml_string)
                pretty_xml = dom.toprettyxml(indent="    ")
                return pretty_xml

            xml_tree = ET.Element(root)
            _dict_to_xml(xml_tree, data)
            tmp: bytes = ET.tostring(xml_tree, encoding='utf-8')
            output = header + tmp.decode('utf-8')
            return _prettify_xml(output) if pretty else output

    def format_dict(self, payload: Dict4) -> Dict:

        def _process_payload(raw_keys: List[str], payload: Dict4={}) -> Tuple[str, List, Dict]:
            wild_list = False
            wild_dict: Dict = {}
            valid_keys, root_key = [], ''
            payload_copy = deepcopy(payload)
            for key in raw_keys:
                if "*" in key:
                    wild_key = key.strip('*')
                    wild_dict = payload_copy.get(wild_key, {})  # need to consider all..
                    if not wild_dict:
                        break  # this means resource is not available...
                    elif len(wild_dict) == 1:
                        # return actual item if not a list...
                        payload_copy = list(wild_dict.values()).pop()
                    else:
                        payload_copy = wild_dict
                        wild_list = True
                else:
                    root_key = root_key or key
                    # skip initial key if it's a wild list,
                    if not wild_list:
                        valid_keys.append(key)
                    else:
                        wild_list = False
            return (root_key, valid_keys, payload_copy)

        def _get_dict_values(d: Dict4, keys: List) -> Dict:
            for key in keys:
                d = d[key]
            return d

        def _populate_dict(key: str, valid_keys: List, sub_payload: Dict4, print_err: bool=False):
            tmp_dict: Dict = {}
            try:
                tmp_dict = _get_dict_values(sub_payload, valid_keys)
                if key in self._target_keys_dict:
                    sub_keys = [key.strip() for key in self._target_keys_dict.get(key, '').split(',')]
                    tmp_dict = {k:v for k, v in tmp_dict.items() if k in sub_keys}
            except KeyError:
                # this means resource is not available...
                self._print(f"Resource `{','.join(valid_keys)}` is not available.", color='orange')
            return tmp_dict

        def _summarize(config: Dict[str, List[str]], parents: Dict, payload: Dict4, out_d: Dict4={}):
            for key, value in config.items():
                if key not in parents:
                    continue
                out_d[key] = {}
                children: Dict4 = parents.get(key, {})
                for path in value:
                    raw_keys = path.split(',')
                    if "*" in path:  # Do wild-card (list) lookup...
                        root_key, valid_keys, sub_payload = _process_payload(raw_keys, payload)
                        if not (valid_keys or root_key):
                            self._print(f"Key [{key}] resource {value} is not available.", color='orange')
                            continue  # this means resource is not avaiable
                        if sub_payload.get(root_key):
                            out_d[key].update(_populate_dict(key, valid_keys, sub_payload))
                        else:
                            # This means it's wild card list...
                            valid_keys.insert(0, root_key)
                            for k, v in sub_payload.items():
                                out_d[key][k] = {}
                                out_d[key][k].update(_populate_dict(key, valid_keys, v, True))
                                for child in children:
                                    out_d[key][k].update(_summarize({child: config.get(child, [])}, children, v, {}))
                    else:
                        # No wild card, do direct lookup...
                        valid_keys = raw_keys
                        out_d[key].update(_populate_dict(key, valid_keys, payload))

            return out_d

        return _summarize(self._config, self._tree_config, payload)

    def process_config(self):

        def _set_target_keys(d: Dict[str, Dict]) -> None:
            for k, v in d.items():
                if isinstance(v, dict) and v.get(self._keys_idn, ''):
                    self._target_keys_dict[k] = v[self._keys_idn]
                    _set_target_keys(v)

        def _prune_tree(d) -> Dict:
            if isinstance(d, dict):
                return {key: _prune_tree(value) for key, value in d.items() if key != self._keys_idn}
            elif isinstance(d, list):
                return [_prune_tree(item) for item in d]
            else:
                return d

        if not self._config:
            self._config = self.load_file(self.config_file, 'utf-8', 'json')

        self._raw_tree_config = self._config.get(self._tree_idn, {})
        self._tree_config = _prune_tree(self._raw_tree_config)
        _set_target_keys(self._raw_tree_config)

    def parse(self, file: str) -> Dict:
        st = time.perf_counter()
        self.process_config()
        if self.parser_type == 'raw':
            self._print(f'Raw xml to dict parsing.', color='yellow')
            return self.load_file(file)

        try:
            unformatted_dict = self.xml_to_dict(self.load_file(file), {})
            self._print(f'Unformatted custom parsing.', color='yellow')
            if not self._tree_config:
                return unformatted_dict
        except Exception:
            self._print(f"Corrupt file: {file}", color='red')
            return {}

        try:
            formatted_dict = self.format_dict(unformatted_dict[next(iter(unformatted_dict))])
        except Exception:
            self._print(f"Bad configuration, defaulting to unformatted parsing.", color='orange')
            return unformatted_dict


        self._print(f'Formatted custom parsing.', color='yellow')
        [self._print(f'"{key}" table is empty.', color='orange') for key, value in formatted_dict.items() if not value]
        self._print(f'Parsing time: {time.perf_counter() - st:0.2f}s', color='green', attr=['b'])

        return formatted_dict

    def dump(self, data: Dict, file: str, cdata: bool=True, pretty: bool=True, input_format: str='raw',
             root: str='root', header: str="<?xml version='1.0' encoding='utf-8'?>", **kwargs) -> None:
        if input_format == 'raw':
            output = xmltodict.unparse(data, pretty=pretty)
            if cdata:
                output = output.replace('<rows>', '<rows><![CDATA[').replace('</rows>', ']]></rows>')
        else:
            output = self.dict_to_xml(data, pretty, root, header)

        if kwargs.get('dumps'):
            return output

        with open(file, 'w') as of:
            of.write(output)

    def dumps(self, data: Dict, cdata: bool=True, pretty: bool=True, input_format: str='raw', root: str='') -> None:
        return self.dump(data, '', cdata, pretty, input_format, root, dumps=True)


XmlParser.__doc__ = LONG_DESCRIPTION
