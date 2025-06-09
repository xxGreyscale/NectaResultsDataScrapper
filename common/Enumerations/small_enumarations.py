from enum import Enum


class DivisionEnum(str, Enum):
    """
    Enumeration for the division of NECTA results.
    """
    I = "I"
    II = "II"
    III = "III"
    IV = "IV"
    ZERO = "0"
    ABS = "ABS"  # Absent
    RESULT_WITHHELD = "*R"  # Referred, results withheld
    E_STAR = "*E"
    WITHDRAWN = "*W"  # Withdrawn
    S_STAR = "*S"  # Special Pass

    @classmethod
    def from_string(cls, input_string: str):
        """
        Converts an input string to a DivisionEnum member.
        Handles aliases like 'FLD' for ZERO.
        """
        if not isinstance(input_string, str):
            # Or raise a TypeError, depending on desired behavior
            return None  # Or raise ValueError("Input must be a string")

        return cls._lookup_map.get(input_string, None)  # Return None if not found

    def __new__(cls, value):
        if not isinstance(value, str):
            # This check helps catch issues early if non-string values are passed during enum definition
            raise TypeError(f"Enum member value must be a string, got {type(value)}")
        member = str.__new__(cls, value)
        member._value_ = value
        return member

    def __str__(self):
        return self._value_

    def __eq__(self, other):
        if not isinstance(other, DivisionEnum):
            return NotImplemented
        return self._value_ == other._value_

    def __hash__(self):
        return hash(self._value_)


DivisionEnum._lookup_map = {
    "I": DivisionEnum.I,
    "II": DivisionEnum.II,
    "III": DivisionEnum.III,
    "IV": DivisionEnum.IV,
    "0": DivisionEnum.ZERO,
    "FLD": DivisionEnum.ZERO,  # Alias for ZERO
    "ABS": DivisionEnum.ABS,
    "*R": DivisionEnum.RESULT_WITHHELD,
    "*E": DivisionEnum.E_STAR,
    "*W": DivisionEnum.WITHDRAWN,
    "*S": DivisionEnum.S_STAR,
}


class GradeEnum(str, Enum):
    """
    Enumeration for the grades of NECTA results.
    """
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    S = "S"  # Subsidiary
    F = "F"  # Fail
    X = "X"  # Absent
    R = "*R"  # Referred, results withheld
    I = "I"  # Referred to as Incomplete

    def __new__(cls, value, label=None):
        member = str.__new__(cls, value)
        member._value_ = value
        member.label = label
        return member

    def __str__(self):
        return self.label if self.label else self._value_

    @classmethod
    def from_value_or_abbr(cls, identifier):
        for member in cls:
            if member._value_ == identifier or member.label == identifier:
                return member
        raise ValueError(f"No GradeEnum member found with value or abbreviation '{identifier}'")


class InstitutionTypeEnum(str, Enum):
    """
    Enumeration for the types of institutions.
    """
    SCHOOL = "School"
    CENTER = "Center"

    def __new__(cls, value, label=None):
        member = str.__new__(cls, value)
        member._value_ = value
        member.label = label
        return member

    def __str__(self):
        return self.label if self.label else self._value_
