from enum import Enum


class SexEnum(str, Enum):
    MALE = ("M", "Male")
    FEMALE = ("F", "Female")
    NONE = ("None", "None")  # No sex defined

    def __new__(cls, value, label):
        member = str.__new__(cls, value)
        member._value_ = value
        member.label = label
        return member

    def __str__(self):
        return self.label

    def __eq__(self, other):
        if not isinstance(other, SexEnum):
            return NotImplemented
        return self._value_ == other._value_

    def __hash__(self):
        return hash(self._value_)

