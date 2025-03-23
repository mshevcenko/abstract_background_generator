from enum import Enum
from pydantic import BaseModel
from typing import Any, Dict, Optional, List, Union, Tuple
from typing_extensions import TypedDict


class DataType(str, Enum):
    INTEGER_TUPLE = "integer_tuple"  # python tuple of two integer numbers
    FLOAT_TUPLE = "float_tuple"      # python tuple of two float numbers
    INTEGER = "integer"              # python integer
    FLOAT = "float"                  # python float
    COLORS = "colors"                # python list of colors in hex format
    ENUM_LIST = "enum_list"          # python list of dicts{"value": "value", "visible_value": "visible_value"}
    BOOL = "bool"                    # python bool


class VisibleType(str, Enum):
    FIELD = "field"
    SLIDER = "slider"
    RANGE_SLIDER = "range_slider"
    CHECKBOX = "checkbox"
    COLORS = "colors"
    SELECTOR = "selector"


class EnumValueDict(TypedDict):
    value: Union[int, float, str, List[str], Tuple[int, int], Tuple[float, float], bool]
    visible_value: str


class ParameterModel(BaseModel):
    name: str
    visible_name: str
    data_type: DataType
    visible_type: VisibleType
    default: Union[int, float, str, List[str], Tuple[int, int], Tuple[float, float], bool]
    min_value: Union[int, float, None] = None
    max_value: Union[int, float, None] = None
    possible_values: Optional[List[EnumValueDict]] = None
    min_count: Optional[int] = None
    max_count: Optional[int] = None


class Parameter:

    def __init__(self,
                 name: str,
                 visible_name: str,
                 data_type: DataType,
                 visible_type: VisibleType,
                 default: Union[int, float, str, List[str], Tuple[int, int], Tuple[float, float], bool],
                 min_value: Union[int, float, None] = None,
                 max_value: Union[int, float, None] = None,
                 possible_values: Optional[List[EnumValueDict]] = None,
                 min_count: Optional[int] = None,
                 max_count: Optional[int] = None):
        self.name = name
        self.visible_name = visible_name
        self.visible_type = visible_type
        self.data_type = data_type
        self.min_value = min_value
        self.max_value = max_value
        self.default = default
        self.possible_values = possible_values
        self.min_count = min_count
        self.max_count = max_count
        self.__check()
        self.model = ParameterModel(
            name=self.name,
            visible_name=self.visible_name,
            visible_type=self.visible_type,
            data_type=self.data_type,
            min_value=self.min_value,
            max_value=self.max_value,
            default=default,
            possible_values=possible_values,
            min_count=min_count,
            max_count=max_count,
        )

    def __check(self) -> None:
        if not isinstance(self.name, str):
            raise ValueError(f"Parameter name(\"{self.name}\") is not str")
        if not isinstance(self.visible_name, str):
            raise ValueError(f"Parameter visible_name(\"{self.visible_name}\") is not str")
        if not isinstance(self.data_type, DataType):
            raise ValueError(f"Parameter data_type(\"{self.data_type}\") is not DataType")
        if not isinstance(self.visible_type, VisibleType):
            raise ValueError(f"Parameter visible_type(\"{self.visible_type}\") is not VisibleType")
        self.__check_data_type_visible_type()
        self.__check_min_value_max_value()
        self.__check_min_count_max_count()
        self.__check_possible_values()
        self.__check_default()

    def __check_default(self) -> None:
        if self.data_type == DataType.INTEGER or self.data_type == DataType.FLOAT:
            if self.data_type == DataType.INTEGER and not isinstance(self.default, int):
                raise ValueError(f"Parameter default(\"{self.default}\") of data_type \"{self.data_type}\" must be int")
            if self.data_type == DataType.FLOAT and not isinstance(self.default, float):
                raise ValueError(f"Parameter default(\"{self.default}\") of data_type \"{self.data_type}\" must be float")
            if self.min_value and self.min_value > self.default:
                raise ValueError(f"Parameter default(\"{self.default}\") of data_type \"{self.data_type}\" cannot be less than min_value(\"{self.min_value}\")")
            if self.max_value and self.max_value < self.default:
                raise ValueError(f"Parameter default(\"{self.default}\") of data_type \"{self.data_type}\" cannot be more than max_value(\"{self.max_value}\")")
            default_str = str(self.default)
            if self.min_count and len(default_str) < self.min_count:
                raise ValueError(f"Parameter default(\"{self.default}\") of data_type \"{self.data_type}\" cannot have count of numbers less than min_count(\"{self.min_count}\")")
            if self.max_count and len(default_str) > self.max_count:
                raise ValueError(f"Parameter default(\"{self.default}\") of data_type \"{self.data_type}\" cannot have count of numbers more than max_count(\"{self.max_count}\")")
        elif self.data_type == DataType.INTEGER_TUPLE or self.data_type == DataType.FLOAT_TUPLE:
            if self.data_type == DataType.INTEGER_TUPLE:
                if not isinstance(self.default, tuple):
                    raise ValueError(f"Parameter default(\"{self.default}\") of data_type \"{self.data_type}\" must be tuple of two integers")
                if len(self.default) != 2:
                    raise ValueError(f"Parameter default(\"{self.default}\") of data_type \"{self.data_type}\" must be tuple of two integers")
                for default_value in self.default:
                    if not isinstance(default_value, int):
                        raise ValueError(f"Parameter default(\"{self.default}\") of data_type \"{self.data_type}\" must be tuple of two integers")
            if self.data_type == DataType.FLOAT_TUPLE:
                if not isinstance(self.default, tuple):
                    raise ValueError(f"Parameter default(\"{self.default}\") of data_type \"{self.data_type}\" must be tuple of two floats")
                if len(self.default) != 2:
                    raise ValueError(f"Parameter default(\"{self.default}\") of data_type \"{self.data_type}\" must be tuple of two floats")
                for default_value in self.default:
                    if not isinstance(default_value, float):
                        raise ValueError(f"Parameter default(\"{self.default}\") of data_type \"{self.data_type}\" must be tuple of two floats")
            if self.default[0] > self.default[1]:
                raise ValueError(f"Parameter default(\"{self.default}\") of data_type \"{self.data_type}\" cannot have first number to be more than second number")
            if self.min_value and self.min_value > self.default[0]:
                raise ValueError(f"Parameter default(\"{self.default}\") of data_type \"{self.data_type}\" cannot have numbers to be less than min_value(\"{self.min_value}\")")
            if self.max_value and self.max_value < self.default[1]:
                raise ValueError(f"Parameter default(\"{self.default}\") of data_type \"{self.data_type}\" cannot have numbers to be more than max_value(\"{self.max_value}\")")
        elif self.data_type == DataType.COLORS:
            if not isinstance(self.default, list):
                raise ValueError(f"Parameter default(\"{self.default}\") of data_type \"{self.data_type}\" must be list of color strings in hex format")
            if self.min_count and len(self.default) < self.min_count:
                raise ValueError(f"Parameter default(\"{self.default}\") of data_type \"{self.data_type}\" cannot have less than min_count(\"{self.min_count}\") colors")
            if self.max_count and len(self.default) > self.max_count:
                raise ValueError(f"Parameter default(\"{self.default}\") of data_type \"{self.data_type}\" cannot have more than max_count(\"{self.max_count}\") colors")
            hex_digits = set("0123456789abcdefABCDEF")
            for default_value in self.default:
                hex_color = default_value.lstrip('#')
                if len(hex_color) != 8 and len(hex_color) != 6:
                    raise ValueError(f"Parameter default(\"{self.default}\") of data_type \"{self.data_type}\" must be list of color strings in hex format")
                for char in hex_color:
                    if char not in hex_digits:
                        raise ValueError(f"Parameter default(\"{self.default}\") of data_type \"{self.data_type}\" must be list of color strings in hex format")
        elif self.data_type == DataType.BOOL:
            if not isinstance(self.default, bool):
                raise ValueError(f"Parameter default(\"{self.default}\") of data_type \"{self.data_type}\" must be bool")
        elif self.data_type == DataType.ENUM_LIST:
            values = [possible_value["value"] for possible_value in self.possible_values]
            if self.default not in values:
                raise ValueError(f"Parameter default(\"{self.default}\") of data_type \"{self.data_type}\" must be in possible_values(\"{self.possible_values}\")")

    def __check_data_type_visible_type(self) -> None:
        if self.data_type == DataType.INTEGER or self.data_type == DataType.FLOAT:
            if self.visible_type != VisibleType.FIELD and self.visible_type != VisibleType.SLIDER:
                raise ValueError(f"Parameter visible_type(\"{self.visible_type}\") of data_type \"{self.data_type}\" must be \"{VisibleType.FIELD}\" or \"{VisibleType.SLIDER}\"")
        elif self.data_type == DataType.INTEGER_TUPLE or self.data_type == DataType.FLOAT_TUPLE:
            if self.visible_type != VisibleType.RANGE_SLIDER:
                raise ValueError(f"Parameter visible_type(\"{self.visible_type}\") of data_type \"{self.data_type}\" must be \"{VisibleType.RANGE_SLIDER}\"")
        elif self.data_type == DataType.COLORS:
            if self.visible_type != VisibleType.COLORS:
                raise ValueError(f"Parameter visible_type(\"{self.visible_type}\") of data_type \"{self.data_type}\" must be \"{VisibleType.COLORS}\"")
        elif self.data_type == DataType.ENUM_LIST:
            if self.visible_type != VisibleType.SELECTOR:
                raise ValueError(f"Parameter visible_type(\"{self.visible_type}\") of data_type \"{self.data_type}\" must be \"{VisibleType.SELECTOR}\"")
        elif self.data_type == DataType.BOOL:
            if self.visible_type != VisibleType.CHECKBOX:
                raise ValueError(f"Parameter visible_type(\"{self.visible_type}\") of data_type \"{self.data_type}\" must be \"{VisibleType.CHECKBOX}\"")

    def __check_possible_values(self) -> None:
        if self.data_type == DataType.ENUM_LIST:
            if not isinstance(self.possible_values, list):
                raise ValueError(f"Parameter possible_values(\"{self.possible_values}\") of data_type \"{self.data_type}\" must be list of EnumValueDict")
            required_keys = {"value", "visible_value"}
            for possible_value in self.possible_values:
                if not isinstance(possible_value, dict):
                    raise ValueError(f"Parameter possible_values(\"{self.possible_values}\") of data_type \"{self.data_type}\" must be list of EnumValueDict")
                if not required_keys.issubset(possible_value.keys()):
                    raise ValueError(f"Parameter possible_values(\"{self.possible_values}\") of data_type \"{self.data_type}\" must be list of EnumValueDict")
                if not isinstance(possible_value["visible_value"], str):
                    raise ValueError(f"Parameter possible_values(\"{self.possible_values}\") of data_type \"{self.data_type}\" must be list of EnumValueDict")
        else:
            if self.possible_values is not None:
                raise ValueError(f"Parameter possible_values(\"{self.possible_values}\") of data_type \"{self.data_type}\" must be None")


    def __check_min_value_max_value(self) -> None:
        if self.data_type == DataType.INTEGER or self.data_type == DataType.INTEGER_TUPLE:
            if not isinstance(self.min_value, int):
                raise ValueError(f"Parameter min_value(\"{self.min_value}\") of data_type \"{self.data_type}\" must be int")
            if not isinstance(self.max_value, int):
                raise ValueError(f"Parameter max_value(\"{self.max_value}\") of data_type \"{self.data_type}\" must be int")
            if self.min_value > self.max_value:
                raise ValueError(f"Parameter min_value(\"{self.min_value}\") can not be bigger than max_value(\"{self.max_value}\")")
        elif self.data_type == DataType.FLOAT or self.data_type == DataType.FLOAT_TUPLE:
            if not isinstance(self.min_value, float):
                raise ValueError(f"Parameter min_value(\"{self.min_value}\") of data_type \"{self.data_type}\" must be float")
            if not isinstance(self.max_value, float):
                raise ValueError(f"Parameter max_value(\"{self.max_value}\") of data_type \"{self.data_type}\" must be float")
            if self.min_value > self.max_value:
                raise ValueError(f"Parameter min_value(\"{self.min_value}\") can not be bigger than max_value(\"{self.max_value}\")")
        else:
            if self.min_value is not None:
                raise ValueError(f"Parameter min_value(\"{self.min_value}\") of data_type \"{self.data_type}\" must be None")
            if self.max_value is not None:
                raise ValueError(f"Parameter max_value(\"{self.max_value}\") of data_type \"{self.data_type}\" must be None")

    def __check_min_count_max_count(self) -> None:
        if self.visible_type == VisibleType.FIELD or self.visible_type == VisibleType.COLORS:
            if not isinstance(self.min_count, int):
                raise ValueError(f"Parameter min_count(\"{self.min_count}\") of visible_type \"{self.visible_type}\" must be int")
            if not isinstance(self.max_count, int):
                raise ValueError(f"Parameter max_count(\"{self.max_count}\") of visible_type \"{self.visible_type}\" must be int")
            if self.min_count > self.max_count:
                raise ValueError(f"Parameter min_count(\"{self.min_count}\") can not be bigger than max_count(\"{self.max_count}\")")
        else:
            if self.min_count is not None:
                raise ValueError(f"Parameter min_count(\"{self.min_count}\") of visible_type \"{self.visible_type}\" must be None")
            if self.max_count is not None:
                raise ValueError(f"Parameter max_count(\"{self.max_count}\") of visible_type \"{self.visible_type}\" must be None")


    def check_value(self,
                    value: Union[int, float, str, List[str], Tuple[int, int], Tuple[float, float], bool]) -> None:
        pass

    def random_value(self) -> Union[int, float, str, List[str], Tuple[int, int], Tuple[float, float], bool]:
        pass


def check_values(parameters: List[Parameter],
                 values: Dict[str, Any]) -> None:
    for parameter in parameters:
        if parameter.name in values:
            parameter.check_value(values[parameter.name])


def fill_default_values(parameters: List[Parameter],
                        values: Dict[str, Any]) -> Dict[str, Any]:
    filled_values = values.copy()
    for parameter in parameters:
        if parameter.name not in values:
            filled_values[parameter.name] = parameter.default
    return filled_values


def filter_values(parameters: List[Parameter],
                  values: Dict[str, Any],
                  allow_list: List[str] = []) -> Dict[str, Any]:
    filtered_values: Dict[str, Any] = {}
    for parameter in parameters:
        if parameter.name in values:
            filtered_values[parameter.name] = values[parameter.name]
    for parameter_name in allow_list:
        if parameter_name in values:
            filtered_values[parameter_name] = values[parameter_name]
    return filtered_values


def check_parameters_unique_names(parameters: List[Parameter]) -> None:
    parameters_names = set()
    for parameter in parameters:
        if parameter.name in parameters_names:
            raise ValueError(f"Parameters have same name: \"{parameter.name}\"")
        parameters_names.add(parameter.name)
