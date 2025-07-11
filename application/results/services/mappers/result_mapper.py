from application.results.repository.entities.results_document import ResultDocument, ResultDocumentIdentifiers, \
    CurrentResultDocument
from common.Domain.result import NectaACSEEResult, ACSEESubjectAndGrade
from common.Enumerations.sex import SexEnum
from common.Enumerations.small_enumarations import DivisionEnum, GradeEnum
from common.Enumerations.subject import ACSEESubjectEnum


class ResultMapper:
    def acsee_result_mapping(self, center_no: str, necta_raw_results: list, year) -> [NectaACSEEResult]:
        try:
            return list(map(lambda result: NectaACSEEResult(
                year=year,
                index_number=result["CNO"].split("/")[1] if len(result.get("CNO").split("/")) > 1 else result.get("CNO"),
                exam_center=center_no,
                division=DivisionEnum.from_string(result.get("DIV")) if result.get("DIV") is not None else None,
                sex = SexEnum(result.get("SEX")) if result.get("SEX") in ("M", "F", "None") else SexEnum.NONE,
                aggregate=result.get("AGGT", 0),
                subjects=self.acsee_subject_grade_mapping(result.get("DETAILED SUBJECTS")),
            ), necta_raw_results))
        except Exception as e:
            raise ValueError(f"Error mapping NECTA results: {e}")

    @staticmethod
    def acsee_subject_grade_mapping(subject_grades: dict) -> list:
        """"
        This function maps the subject grades to a dictionary
        :param subject_grades: The subject grade dictionary
        :return: A dictionary with subject names as keys and grades as values
        """""
        result = []
        for key, value in subject_grades.items() if subject_grades is not None else {}.items():
            result.append(ACSEESubjectAndGrade(subject=ACSEESubjectEnum.from_value_or_abbr(key),
                                               grade=GradeEnum.from_value_or_abbr(value)))
        return result

    @staticmethod
    def acsee_to_document(domain: NectaACSEEResult) -> ResultDocument:
        return ResultDocument(
            identifiers=ResultDocumentIdentifiers(index_number=domain.exam_center + "/" + domain.index_number) if domain.index_number and domain.exam_center else None,
            current=CurrentResultDocument(
                year=domain.year,
                sex=domain.sex,
                aggregate=domain.aggregate,
                division=domain.division,
                subjects=domain.subjects
            ),
            data_version=1.0,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
        )

    @staticmethod
    def acsee_from_document(document: ResultDocument) -> NectaACSEEResult:
        return NectaACSEEResult(
            index_number=document.identifiers.index_number.split("/")[1],
            exam_center=document.identifiers.index_number.split("/")[0],
            division=document.current.division,
            aggregate=document.current.aggregate,
            created_at=document.created_at,
            updated_at=document.updated_at,
            sex=document.current.sex,
            year=document.current.year,
            subjects=document.current.subjects
        )
