import random
import string


class ResultSummaryId:
    """
    A class to represent the result summary ID.
    Attributes
    ----------
    id : str
        The ID of the result summary.
    Methods
    -------
    __str__():
        Returns the string representation of the ResultSummaryId object.
    """

    def __init__(self, id: str = None):
        """
        Constructs all the necessary attributes for the ResultSummaryId object.
        Parameters
        ----------
        id : str
        The ID of the result summary.
        """
        if id and len(id) != 12:
            raise ValueError("Result Summary ID must be 12 characters long.")
        if id and not id.startswith("RS-"):
            raise ValueError("Result Summary ID must start with 'RS-'.")
        if id and not id[3:].isalnum():
            raise ValueError("Result Summary ID must contain only alphanumeric characters after 'RS-'.")
        if id and not id[3:].isdigit():
            raise ValueError("Result Summary ID must contain only digits after 'RS-'.")
        self.id = id

    def __str__(self) -> str:
        """Returns the string representation of the ResultSummaryId object."""
        return self.id

    def generate(self):
        """Generates a new ID for the ResultSummaryId object."""
        prefix = "RS-"
        suffix = ''.join(random.choices(string.digits, k=10))
        self.id = prefix + suffix
        return self

    def __eq__(self, other):
        """Checks if two ResultSummaryId objects are equal."""
        if not isinstance(other, ResultSummaryId):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        """Returns the hash of the ResultSummaryId object."""
        return hash(self.id)

    def value(self) -> str:
        """Returns the value of the ResultSummaryId object."""
        return self.id
