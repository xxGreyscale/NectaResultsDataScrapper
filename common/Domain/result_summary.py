from common.Primitives.result_summary_id import ResultSummaryId


class PerDivisionSummary:
    def __init__(self, males: int = 0, females: int = 0, total: int = 0):
        self.males = males
        self.females = females
        self.total = total

    def to_dict(self):
        return {
            "females": self.females,
            "males": self.males,
            "total": self.total
        }

    @staticmethod
    def from_dict(data: dict) -> 'PerDivisionSummary':
        return PerDivisionSummary(
            females=data["females"],
            males=data["males"],
            total=data["total"]
        )


class CandidatesResultSummary:
    """"
    Here we include stuff like total students, division I, II, III, IV, and Zero
    """""

    def __init__(self,
                 id: ResultSummaryId,
                 division_one: PerDivisionSummary = None,
                 division_two: PerDivisionSummary = None,
                 division_three: PerDivisionSummary = None,
                 division_four: PerDivisionSummary = None,
                 division_zero: PerDivisionSummary = None,
                 absent: PerDivisionSummary = None,
                 result_withheld: PerDivisionSummary = None,
                 e_star: PerDivisionSummary = None,
                 withdrawn: PerDivisionSummary = None,
                 special_pass: PerDivisionSummary = None
                 ):
        self.id = id
        self.division_one = division_one
        self.division_two = division_two
        self.division_three = division_three
        self.division_four = division_four
        self.division_zero = division_zero
        self.absent = absent
        self.result_withheld = result_withheld
        self.e_star = e_star
        self.withdrawn = withdrawn
        self.special_pass = special_pass

    def __str__(self):
        return (f"id: {self.id}, "
                f"Division I: {self.division_one},"
                f" Division II: {self.division_two}, "
                f"Division III: {self.division_three}, "
                f"Division IV: {self.division_four}, "
                f"Division Zero: {self.division_zero}"
                f" Division Absent: {self.absent}, "
                f" Division Result Withheld: {self.result_withheld}, "
                f" Division E*: {self.e_star}," 
                f" Division Withdrawn: {self.withdrawn}, "
                f" Division Special Pass: {self.special_pass}")

    def to_dict(self):
        return {
            "id": self.id.value(),
            "divisionOne": self.division_one.to_dict() if self.division_one else None,
            "divisionTwo": self.division_two.to_dict() if self.division_two else None,
            "divisionThree": self.division_three.to_dict() if self.division_three else None,
            "divisionFour": self.division_four.to_dict() if self.division_four else None,
            "divisionZero": self.division_zero.to_dict() if self.division_zero else None,
            "absent": self.absent.to_dict() if self.absent else None,
            "resultWithheld": self.result_withheld.to_dict() if self.result_withheld else None,
            "eStar": self.e_star.to_dict() if self.e_star else None,
            "withdrawn": self.withdrawn.to_dict() if self.withdrawn else None,
            "specialPass": self.special_pass.to_dict() if self.special_pass else None
        }

    @staticmethod
    def from_dict(data: dict) -> 'CandidatesResultSummary':
        return CandidatesResultSummary(
            id=ResultSummaryId(data["id"]),
            division_one=PerDivisionSummary.from_dict(data["divisionOne"]),
            division_two=PerDivisionSummary.from_dict(data["divisionTwo"]),
            division_three=PerDivisionSummary.from_dict(data["divisionThree"]),
            division_four=PerDivisionSummary.from_dict(data["divisionFour"]),
            division_zero=PerDivisionSummary.from_dict(data["divisionZero"]),
            absent=PerDivisionSummary.from_dict(data["absent"]),
            result_withheld=PerDivisionSummary.from_dict(data["resultWithheld"]),
            e_star=PerDivisionSummary.from_dict(data["eStar"]),
            withdrawn=PerDivisionSummary.from_dict(data["withdrawn"]),
            special_pass=PerDivisionSummary.from_dict(data["specialPass"])
        )

    def __eq__(self, other):
        if not isinstance(other, CandidatesResultSummary):
            return NotImplemented
        return self.id == other.id and \
            self.division_one == other.division_one and \
            self.division_two == other.division_two and \
            self.division_three == other.division_three and \
            self.division_four == other.division_four and \
            self.division_zero == other.division_zero and \
            self.absent == other.absent and \
            self.result_withheld == other.result_withheld and \
            self.e_star == other.e_star and \
            self.withdrawn == other.withdrawn and \
            self.special_pass == other.special_pass
