from common.Domain.result_summary import PerDivisionSummary


class CandidatesResultSummaryDocument:
    """"
    Here we include stuff like total students, division I, II, III, IV, and Zero
    """""

    def __init__(self,
                 division_one: PerDivisionSummary = None,
                 division_two: PerDivisionSummary = None,
                 division_three: PerDivisionSummary = None,
                 division_four: PerDivisionSummary = None,
                 division_zero: PerDivisionSummary = None,
                 ):
        self.division_one = division_one
        self.division_two = division_two
        self.division_three = division_three
        self.division_four = division_four
        self.division_zero = division_zero

    def __str__(self):
        return (
                f"Division I: {self.division_one},"
                f" Division II: {self.division_two}, "
                f"Division III: {self.division_three}, "
                f"Division IV: {self.division_four}, "
                f"Division Zero: {self.division_zero}")

    def to_dict(self):
        return {
            "divisionOne": self.division_one.to_dict() if self.division_one else None,
            "divisionTwo": self.division_two.to_dict() if self.division_two else None,
            "divisionThree": self.division_three.to_dict() if self.division_three else None,
            "divisionFour": self.division_four.to_dict() if self.division_four else None,
            "divisionZero": self.division_zero.to_dict() if self.division_zero else None
        }

    @staticmethod
    def from_dict(data: dict) -> 'CandidatesResultSummaryDocument':
        return CandidatesResultSummaryDocument(
            division_one=PerDivisionSummary.from_dict(data["divisionOne"]),
            division_two=PerDivisionSummary.from_dict(data["divisionTwo"]),
            division_three=PerDivisionSummary.from_dict(data["divisionThree"]),
            division_four=PerDivisionSummary.from_dict(data["divisionFour"]),
            division_zero=PerDivisionSummary.from_dict(data["divisionZero"])
        )

    def __eq__(self, other):
        if not isinstance(other, CandidatesResultSummaryDocument):
            return NotImplemented
        return self.division_one == other.division_one and \
            self.division_two == other.division_two and \
            self.division_three == other.division_three and \
            self.division_four == other.division_four and \
            self.division_zero == other.division_zero
