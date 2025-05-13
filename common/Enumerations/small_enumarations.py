from enum import Enum


class DivisionEnum(str, Enum):
    """
    Enumeration for the division of NECTA results.
    """
    I = "I"
    II = "II"
    III = "III"
    IV = "IV"
    ZERO = "0"  # Zero Division
    ABS = "ABS"  # Absent
    RESULT_WITHHELD = "*R"  # Referred, results withheld
    E_STAR = "*E"
    WITHDRAWN = "*W"  # Withdrawn
    S_STAR = "*S"  # Special Pass

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
        raise ValueError(f"No SubjectEnum member found with value or abbreviation '{identifier}'")


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
        raise ValueError(f"No SubjectEnum member found with value or abbreviation '{identifier}'")


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
