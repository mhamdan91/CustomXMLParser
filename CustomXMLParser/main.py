import xmltodict
import time, json
from moecolor import print
from .README import LONG_DESCRIPTION
from typing import Dict, List, Any

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
    def __init__(self, config_file: str="", parser_type: str="raw", encoding: str="utf-8",
                name_key: str="@name", table_key: str="th", header_key: str='header',
                data_key: str="rows", header_text_key: str="#text") -> None:
        """
            Constructs all the necessary attributes for the XmlParser object.
        Args:
            config_file (str, optional): configuration file for custom formatting. Defaults to "". If not specified, the parser
            will return a json dictionary without custom formatting.
            parser_type (str, optional): type of parsing (custom: for xml to json using custom config, raw: for xml to json). Defaults to "raw".
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
        self._parser_type = parser_type
        self._config_file = config_file
        self._encoding    = encoding
        self._config = self._load_file(self._config_file, 'utf-8', 'json') if self._config_file else {}
        # custom keys configuration, can be set only once per instance - no setter or getter...
        self.name_key   = name_key
        self.table_key  = table_key
        self.header_key = header_key
        self.data_key   = data_key
        self.header_text_key = header_text_key

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

    def _load_file(self, file: str, encoding: str='', doc_type: str='xml') -> Dict:
        encoding = encoding if encoding else self.encoding
        with open(file, encoding=(self.encoding or encoding)) as f:
            return xmltodict.parse(f.read()) if doc_type == 'xml' else json.load(f)

    def _xml_to_dict(self, in_d: Dict4, out_d: Dict4={}):
        element_name = in_d.get(self.name_key, '')
        if self.data_key in in_d: # This means we're at the bottom...
            out_d[element_name] = {}
             # only if primary keys exist...
            if in_d.get(self.data_key) and in_d.get(self.header_key) and in_d.get(self.header_key, {}).get(self.table_key):
                rows = [row.split(',') for row in in_d.get(self.data_key, '').split('\n')]
                rows = list(zip(*rows))
                raw_header: List[Dict] = in_d.get(self.header_key, {}).get(self.table_key, [])
                missing_element = self.data_key if len(rows) < len(raw_header) else self.header_key
                if len(rows) != len(raw_header):
                    print(f"Header and rows for [{element_name}] do not match. [{missing_element}] is incomplete.", 'red')
                else:
                    for i, _dict in enumerate(raw_header):
                        out_d[element_name][_dict.get(self.header_text_key)] = rows[i]
        else:
            for key, value in in_d.items():  # recurse the dict...
                if isinstance(value, dict):
                    if self.name_key in in_d:
                        out_d[next(iter(out_d))].update({key: self._xml_to_dict(value, {})})
                    else:
                        out_d[key] = self._xml_to_dict(value, {})
                elif isinstance(value, list):
                    dict_list = {key: {}}
                    for v in value:
                        dict_list[key].update(self._xml_to_dict(v, {}))  # v is assumed a dictionary...
                    if out_d: # This if element has a name..
                        out_d[next(iter(out_d))].update(dict_list)
                    else:
                        out_d.update(dict_list)
                else:
                    out_d[value] = {}
        return out_d

    def _format_dict(self, payload: Dict4) -> Dict:

        def format_key(keys: List[str], wild_card: bool=False, payload:Dict4={}):
            tmp = payload.copy()
            formatted_key, root_key = '', ''
            wild_list = False
            if wild_card:
                for k in keys:
                    if "*" in k:
                        wild_key = k.strip('*')
                        try:
                            wild_dict: Dict = eval(f'tmp["{wild_key}"]') # need to consider all..
                        except Exception:
                            break # this means resource is not available...
                        for _key, _value in wild_dict.items():
                            if len(wild_dict) == 1:
                                tmp = _value  # if not a list, then return actual item...
                            else:
                                tmp = wild_dict
                                wild_list = True
                                break
                    else:
                        if not root_key:
                            root_key = k
                            if wild_list: # skip initial key if it's a wild list, since we'll use original list instead of the parent key...
                                wild_list = False
                                continue
                        formatted_key += f'["{k}"]'
            else:
                for k in keys:
                    if not root_key:
                        root_key = k
                    formatted_key += f'["{k}"]'
            return formatted_key, root_key, tmp

        def summarize(config: Dict[str, List[str]], parents: Dict, payload: Dict4, out_d: Dict4={}):
            for key, value in config.items():
                if key not in parents:
                    continue
                out_d[key] = {}
                _children = parents.get(key, {})
                for path in value:
                    if "*" in path: # Do wild-card (list) lookup...
                        keys = path.split(',')
                        formatted_key, root_key, tmp_payLoad = format_key(keys, True, payload)
                        if not formatted_key and not root_key:
                            print(f"Key [{key}] resource {value} is not available.", 'orange')
                            continue # this means resource is not avaiable
                        if tmp_payLoad.get(root_key):
                            try:
                                out_d[key] = eval(f'tmp_payLoad{formatted_key}')
                            except KeyError:
                                pass # this means resource is not available...
                        else:
                            # This means it's wild card list...
                            for k, v in tmp_payLoad.items():
                                out_d[key][k] = {}
                                try:
                                    out_d[key][k].update(eval(f'v["{root_key}"]{formatted_key}'))
                                except KeyError:
                                    print(f"Resource {formatted_key} is not available.", 'orange')
                                    pass # it means resource is not available...
                                if _children:
                                    for child in _children:
                                        out_d[key][k].update(summarize({child: config.get(child, [])}, _children, v, {}))
                    else:
                        # Do direct lookup...
                        keys = path.split(',')
                        try:
                            out_d[key].update(eval(f'payload{format_key(keys)[0]}'))
                        except KeyError:
                            pass # It means resource is not available...
            return out_d

        return summarize(self._config, self._config.get('TREE'), payload)

    def parse(self, file: str) -> Dict:
        parsed_content = {}
        st = time.perf_counter()
        if self.parser_type == 'raw':
            parsed_content = self._load_file(file)
            print(f'Raw xml2dict parsing.', 'green')
        else:
            unformatted_dict = self._xml_to_dict(self._load_file(file))
            if not self.config_file:
                parsed_content =  unformatted_dict
                print(f'Unformatted custom parsing.', 'green')
            else:
                if not self._config:
                    self._config = self._load_file(self.config_file, 'utf-8', 'json')
                parsed_content = self._format_dict(unformatted_dict[next(iter(unformatted_dict))])
                print(f'Formatted custom parsing.', 'green')
            [print(f'"{key}" table is empty.', 'orange') for key, value in parsed_content.items() if not value]
        print(f'Parsing time: {time.perf_counter() - st:0.2f}s', 'green', attr=['b'])
        return parsed_content

XmlParser.__doc__ = LONG_DESCRIPTION