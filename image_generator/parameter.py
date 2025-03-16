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
        self.check()
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

    def check(self) -> None:
        pass

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
