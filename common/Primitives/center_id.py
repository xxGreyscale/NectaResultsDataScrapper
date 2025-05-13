import random
import string


class CenterId:
    """
    Class to represent the center ID of a centers
    should be 8 characters
    should have a generate function
    with a prefix of CE-
    """

    def __init__(self, center_id: str = None):
        """
        Initializes a CenterId object.
        :param center_id:
        If provided, validate then use this as the center ID.
        """
        if center_id and len(center_id) != 12:
            raise ValueError("Center ID must be 12 characters long.")
        if center_id and not center_id.startswith("CE-"):
            raise ValueError("Center ID must start with 'CE-'.")
        if center_id and not center_id[3:].isalnum():
            raise ValueError("Center ID must contain only alphanumeric characters after 'CE-'.")
        self.id = center_id

    def __str__(self):
        return self.id

    def generate(self):
        prefix = "CE-".upper()
        suffix = ''.join(random.choices(string.digits, k=10))
        self.id = prefix + suffix
        return self

    def __eq__(self, other):
        if not isinstance(other, CenterId):
            return NotImplemented
        return self.id == other.id

    def value(self) -> str:
        return self.id

    def __hash__(self):
        return hash(self.id)
