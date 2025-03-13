import enum
from typing import Any, Dict, Optional, List


class DataType(enum.Enum):
    INTEGER_TUPLE = "integer_tuple"  # python list of two integer numbers
    FLOAT_TUPLE = "float_tuple"      # python list of two float numbers
    INTEGER = "integer"              # python integer
    FLOAT = "float"                  # python float
    COLORS = "colors"                # python list of two float numbers
    ENUM_LIST = "enum_list"          # python list of dicts{"value": "value", "visible_value": "visible_value"}
    BOOL = "bool"                    # python bool


class VisibleType(enum.Enum):
    FIELD = "field"
    SLIDER = "slider"
    RANGE_SLIDER = "range_slider"
    CHECKBOX = "checkbox"
    COLORS = "colors"
    SELECTOR = "selector"


class Parameter:

    def __init__(self,
                 name: str,
                 visible_name: str,
                 data_type: DataType,
                 visible_type: VisibleType,
                 default: Optional[Any],
                 min_value: Optional[Any] = None,
                 max_value: Optional[Any] = None,
                 possible_values: Optional[List[Any]] = None,
                 min_length: Optional[int] = None,
                 max_length: Optional[int] = None,
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
        self.min_length = min_length
        self.max_length = max_length
        self.min_count = min_count
        self.max_count = max_count
        self.check()

    def check(self) -> None:
        pass

    def check_value(self,
                    value: Any) -> None:
        pass

    def to_dict(self) -> Dict[str, Any]:
        parameter_dict = {}
        for key, value in self.__dict__.items():
            if key == "data_type" or key == "visible_type":
                parameter_dict[key] = value.value
            elif value:
                parameter_dict[key] = value
        return parameter_dict

    def get_random_value(self) -> Any:
        pass
