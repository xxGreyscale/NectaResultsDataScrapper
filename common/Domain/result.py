from datetime import datetime

from common.Enumerations.sex import SexEnum
from common.Enumerations.small_enumarations import DivisionEnum, GradeEnum
from common.Enumerations.subject import ACSEESubjectEnum, CSEESubjectEnum


class SubjectAndGrade:
    def __init__(self, subject, grade):
        self.subject = subject
        self.grade: GradeEnum = grade

    def __str__(self):
        return f"{self.subject}: {self.grade}"

    def get_name(self):
        return self.subject

    def get_grade(self):
        return self.grade

    def to_dict(self):
        return {
            "subject": self.subject.value,
            "grade": self.grade.value
        }

    def __eq__(self, other):
        if not isinstance(other, SubjectAndGrade):
            return NotImplemented
        return self.subject == other.subject

    def __hash__(self):
        return hash(self.subject)

    @staticmethod
    def from_dict(data: dict):
        return SubjectAndGrade(
            subject=data["subject"],
            grade=data["grade"],
        )


class ACSEESubjectAndGrade(SubjectAndGrade):
    def __init__(self, subject: ACSEESubjectEnum, grade: GradeEnum):
        super().__init__(subject, grade)


class CSEESubjectAndGrade(SubjectAndGrade):
    def __init__(self, subject: CSEESubjectEnum, grade: GradeEnum):
        super().__init__(subject, grade)


class NectaACSEEResult:
    def __init__(self,
                 exam_center,
                 sex: SexEnum,
                 aggregate: int,
                 index_number: str,
                 year: int,
                 subjects: list[ACSEESubjectAndGrade],
                 division: DivisionEnum = None,
                 created_at: datetime = None,
                 updated_at: datetime = None,
                 ):
        """
        Initializes a NectaCSEEResult object.

        Args: index_number (str): The student's index number. year (int): The year the examination was taken.
        subject_grades (dict): A dictionary where keys are subject names (str) and values are the grades obtained (
        str, e.g., 'A', 'B', 'C', 'D', 'E', 'S', 'F'). division (str, optional): The overall division achieved (e.g.,
        'I', 'II', 'III', 'IV', '0'). Defaults to None.
        """

        self.index_number = index_number
        self.exam_center = exam_center
        self.year = year
        self.sex = sex
        self.aggregate = aggregate
        self.division = division
        self.created_at = created_at if created_at else datetime.now()
        self.updated_at = updated_at if updated_at else datetime.now()

        # Validate subject
        self._validate_subject(subjects)
        self.subjects: list[ACSEESubjectAndGrade] = subjects

    def __str__(self):
        subject_grade_str = ", ".join(str(sg) for sg in self.subjects)
        return (f"Year: {self.year}, Index Number: {self.index_number}, "
                f"Exam center: {self.exam_center}, "
                f"Sex: {self.sex}, "
                f"Division: {self.division if self.division else 'N/A'} ,"
                f"Aggregate: {self.aggregate}, "
                f"Subjects and Grades: [{subject_grade_str}], "
                f"Created At: {self.created_at}, "
                f"Updated At: {self.updated_at}"
                )

    @staticmethod
    def _validate_subject(subjects: list[ACSEESubjectAndGrade]):
        """""
        There should not be more than one subject with the same name
        """""
        seen_subjects = set()
        for subject_grade in subjects:
            subject_name = subject_grade.get_name()
            if subject_name in seen_subjects:
                raise ValueError(f"Duplicate subject found: {subject_name}")
            seen_subjects.add(subject_name)

    def get_grade(self, subject_name):
        for sg in self.subjects:
            if sg.subject == subject_name:
                return sg.grade
        return None

    def to_dict(self):
        return {
            "year": self.year,
            "index_number": self.index_number,
            "exam_center": self.exam_center,
            "sex": self.sex,
            "division": self.division,
            "aggregate": self.aggregate,
            "subjects": [subject.to_dict() for subject in self.subjects],
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
