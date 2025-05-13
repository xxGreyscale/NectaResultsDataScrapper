from enum import Enum


class ACSEESubjectEnum(str, Enum):
    """
    Enumeration for the principal subjects of ACSEE results with common abbreviations,
    including Basic Applied Mathematics and Advanced Mathematics,
    with the ability to reference by value or abbreviation.
    """
    PHYSICS = "PHYSICS", "PHY"
    CHEMISTRY = "CHEMISTRY", "CHEM"
    MATHEMATICS = "MATHEMATICS", "MATHS"
    ADVANCED_MATHEMATICS = "ADVANCED MATHEMATICS", "ADV/MATHS"
    BASIC_APPLIED_MATHEMATICS = "BASIC APPLIED MATHEMATICS", "BAM"
    BIOLOGY = "BIOLOGY", "BIOL"
    GEOGRAPHY = "GEOGRAPHY", "GEOGR"
    HISTORY = "HISTORY", "HIST"
    ECONOMICS = "ECONOMICS", "ECON"
    KISWAHILI = "KISWAHILI", "KISW"
    ENGLISH = "ENGLISH", "ENGL"
    LITERATURE_IN_ENGLISH = "LITERATURE IN ENGLISH", "LIT"
    COMMERCE = "COMMERCE", "COMM"
    ACCOUNTANCY = "ACCOUNTANCY", "ACC"
    AGRICULTURE = "AGRICULTURE", "AGRI"
    COMPUTER_SCIENCE = "COMPUTER SCIENCE", "COMP/SCIENCE"
    COMPUTER_STUDIES = "COMPUTER STUDIES", "COMP STUD"
    FRENCH = "FRENCH", "FRE"
    ARABIC = "ARABIC", "ARA"
    FINE_ART = "FINE ART", "FIN"
    MUSIC = "MUSIC", "MUS"
    PHYSICAL_EDUCATION = "PHYSICAL EDUCATION", "PHY EDU"
    GENERAL_STUDIES = "GENERAL STUDIES", "G/STUDIES"
    DIVINITY = "DIVINITY", "DIV"
    ISLAMIC_KNOWLEDGE = "ISLAMIC KNOWLEDGE", "IS/KNOWLEDGE"
    CHINESE_LANGUAGE = "CHINESE", "CHIN"
    THEATRE_ARTS = "THEATRE ARTS", "THA"
    BUSINESS_STUDIES = "BUSINESS STUDIES", "BUS"
    FOOD_AND_HUMAN_NUTRITION = "FOOD AND HUMAN NUTRITION", "HN  NUTRITION"
    EDUCATION = "EDUCATION", "EDU"

    def __new__(cls, value, abbreviation=None):
        member = str.__new__(cls, value)
        member._value_ = value
        member.abbreviation = abbreviation
        return member

    def __str__(self):
        return self.label if hasattr(self, 'label') else self._value_

    @property
    def abbreviation(self):
        return self.label

    @abbreviation.setter
    def abbreviation(self, value):
        self.label = value

    @classmethod
    def from_value_or_abbr(cls, identifier):
        for member in cls:
            if member.value == identifier or member.abbreviation == identifier:
                return member
        raise ValueError(f"No SubjectEnum member found with value or abbreviation '{identifier}'")


class CSEESubjectEnum(str, Enum):
    pass
