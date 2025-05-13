from enum import Enum


class SexEnum(str, Enum):
    MALE = ("M", "Male")
    FEMALE = ("F", "Female")

    def __new__(cls, value, label):
        member = str.__new__(cls, value)
        member._value_ = value
        member.label = label
        return member

    def __str__(self):
        return self.label

