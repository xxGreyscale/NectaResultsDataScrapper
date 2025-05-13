from enum import Enum


class ActionToChangeEnum(str, Enum):
    CREATE = ("CREATE", "Create")
    UPDATE = ("UPDATE", "Update")
    DELETE = ("DELETE", "Delete")

    def __new__(cls, value, label):
        member = str.__new__(cls, value)
        member._value_ = value
        member.label = label
        return member

    def __str__(self):
        return self.label
