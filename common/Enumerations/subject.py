from enum import Enum


class ACSEESubjectEnum(str, Enum):
    """
    Enumeration for the principal subjects of ACSEE results with common abbreviations,
    including Basic Applied Mathematics and Advanced Mathematics,
    with the ability to reference by value or abbreviation.
    """
    PHYSICS = "PHYSICS", ("PHY", "SC. & P")
    CHEMISTRY = "CHEMISTRY", ("CHEM", "CHEMIST")
    MATHEMATICS = "MATHEMATICS", ("MATHS",)
    ADVANCED_MATHEMATICS = "ADVANCED MATHEMATICS", ("ADV/MATHS", "ADVANCE")
    BASIC_APPLIED_MATHEMATICS = "BASIC APPLIED MATHEMATICS", ("BAM", "BASIC A")
    BIOLOGY = "BIOLOGY", ("BIOL",)
    GEOGRAPHY = "GEOGRAPHY", ("GEOGR", "GEOGRAP")
    HISTORY = "HISTORY", ("HIST",)
    ECONOMICS = "ECONOMICS", ("ECON", "ECONOMI")
    KISWAHILI = "KISWAHILI", ("KISW", "KISWAHI")
    ENGLISH = "ENGLISH", ("ENGL",)
    LITERATURE_IN_ENGLISH = "LITERATURE IN ENGLISH", ("LIT",)
    COMMERCE = "COMMERCE", ("COMM", "COMMERC")
    ACCOUNTANCY = "ACCOUNTANCY", ("ACC", "ACCOUNT")
    AGRICULTURE = "AGRICULTURE", ("AGRI",)
    COMPUTER_SCIENCE = "COMPUTER SCIENCE", ("COMP/SCIENCE", "COMPUTE")
    COMPUTER_STUDIES = "COMPUTER STUDIES", ("COMP STUD",)
    FRENCH = "FRENCH", ("FRE", "FREN")
    ARABIC = "ARABIC", ("ARA",)
    FINE_ART = "FINE ART", ("FIN",)
    MUSIC = "MUSIC", ("MUS",)
    PHYSICAL_EDUCATION = "PHYSICAL EDUCATION", ("PHY EDU",)
    GENERAL_STUDIES = "GENERAL STUDIES", ("G/STUDIES", "GENERAL")
    DIVINITY = "DIVINITY", ("DIV", "DIVINIT")
    ISLAMIC_KNOWLEDGE = "ISLAMIC KNOWLEDGE", ("IS/KNOWLEDGE", "ISLAMIC", "E/D/KIISLAMU", "ED/KIISLAMU", "KIISLAMU")
    CHINESE_LANGUAGE = "CHINESE", ("CHIN",)
    THEATRE_ARTS = "THEATRE ARTS", ("THA",)
    BUSINESS_STUDIES = "BUSINESS STUDIES", ("BUS",)
    FOOD_AND_HUMAN_NUTRITION = "FOOD AND HUMAN NUTRITION", ("HN  NUTRITION", "FOOD &", "NUTRITION")
    EDUCATION = "EDUCATION", ("EDU",)

    def __new__(cls, value, abbreviations=()):
        member = str.__new__(cls, value)
        member._value_ = value
        member.abbreviations = abbreviations
        return member

    def __str__(self):
        return self.value

    @property
    def abbreviation(self):
        return self.abbreviations[0] if self.abbreviations else None

    @classmethod
    def from_value_or_abbr(cls, identifier):
        for member in cls:
            if member.value == identifier or identifier in member.abbreviations:
                return member
        raise ValueError(f"No SubjectEnum member found with value or abbreviation '{identifier}'")

    @property
    def all_abbreviations(self):
        return self.abbreviations


class CSEESubjectEnum(str, Enum):
    """
    Enumeration for the principal subjects of CSEE results with common abbreviations.
    """
    BASIC_MATHEMATICS = "BASIC MATHEMATICS", ("B/MATH", "B/MATHS", "BASIC MATH")
    MATHEMATICS = "MATHEMATICS", ("MATH", "MATHS")
    ENGLISH = "ENGLISH", ("ENGL", "ENG", "ENGLISH LANG")
    KISWAHILI = "KISWAHILI", ("KISW", "KISWAHI", "KIS")
    BIOLOGY = "BIOLOGY", ("BIOL", "BIO")
    CHEMISTRY = "CHEMISTRY", ("CHEM", "CHE")
    PHYSICS = "PHYSICS", ("PHY", "PHYS", "PHYSICS")
    GEOGRAPHY = "GEOGRAPHY", ("GEOGR", "GEO")
    HISTORY = "HISTORY", ("HIST", "HIS")
    CIVICS = "CIVICS", ("CIV", "CIVIC")
    COMMERCE = "COMMERCE", ("COMM",)
    BOOK_KEEPING = "BOOK KEEPING", ("B/K", "B/KEEPING", "BK", "BOOK-KEEPING")
    AGRICULTURE = "AGRICULTURE", ("AGRI",)
    ARCHITECTURAL_DRAUGHTING = "ARCHITECTURAL DRAUGHTING", ("ARCH DRAUGHT", "ARCH DRAFT", "ARCHITECTURAL DRAUGHT")
    COMPUTER_STUDIES = "COMPUTER STUDIES", ("COMP STUD", "COMP/STD", "COMPUTER")
    ENGINEERING_SCIENCE = "ENGINEERING SCIENCE", ("ENG SC", "ENG. SC", "ENGINEERING SCI")
    INFORMATION_AND_COMPUTER_STUDIES = "INFORMATION AND COMPUTER STUDIES", ("ICS",)
    HOME_ECONOMICS = "HOME ECONOMICS", ("HOME ECO", "H.ECO")
    FINE_ART = "FINE ART", ("F/ART", "FINE ART", "ART")
    MUSIC = "MUSIC", ("MUS",)
    FRENCH = "FRENCH", ("FRE", "FREN")
    ARABIC = "ARABIC", ("ARA",)
    LITERATURE_IN_ENGLISH = "LITERATURE IN ENGLISH", ("LIT", "LIT ENG")
    BIBLE_KNOWLEDGE = "BIBLE KNOWLEDGE", ("BIBLE", "B/KNO", "BKN")
    DIVINITY = "DIVINITY", ("DIV",)
    ISLAMIC_KNOWLEDGE = "ISLAMIC KNOWLEDGE", ("IS/KNOWLEDGE", "ISLAMIC", "E/D/KIISLAMU", "ED/KIISLAMU", "KIISLAMU")
    PHYSICAL_EDUCATION = "PHYSICAL EDUCATION", ("P/EDU", "P.E", "PHY EDU")

    def __new__(cls, value, abbreviations=()):
        member = str.__new__(cls, value)
        member._value_ = value
        member.abbreviations = abbreviations
        return member

    def __str__(self):
        return self.value

    @property
    def abbreviation(self):
        return self.abbreviations[0] if self.abbreviations else None

    @classmethod
    def from_value_or_abbr(cls, identifier):
        for member in cls:
            if member.value == identifier or identifier in member.abbreviations:
                return member
        raise ValueError(f"No SubjectEnum member found with value or abbreviation '{identifier}'")

    @property
    def all_abbreviations(self):
        return self.abbreviations
