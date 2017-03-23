__author__ = 'yaseen'

from django.shortcuts import get_object_or_404
from casereport.constants import CASE_STATUS
from casereport.constants import STATUS
from casereport.models import AuthorizedRep
from casereport.models import CaseFile
from casereport.models import CaseReport
from casereport.models import Institution
from casereport.models import MolecularAbberation
from casereport.models import Physician
from casereport.models import CaseReportHistory
from casereport.models import Treatment


class CaseReportListResource:

    def _get(self):
        pass

    def _post(self, physicians, title=None, file_name=None,  age=None,
              gender=None, pathology=None, subtype=None, presentation=None,
              aberrations=None, biomarkers=None, additional_comment=None,
              document=None, details=None):
        """

        :type clinical_outcome: object
        """

        if document:
            document = CaseFile(document=document, name=file_name)
            document.save()

        result = CaseReport(title=title, age=age, gender=gender,
                            casefile_f=document, subtype=subtype,
                            presentation=presentation, aberrations=aberrations,
                            biomarkers=biomarkers, pathology=pathology,
                            additional_comment=additional_comment,
                            primary_physician=physicians[0])
        result.save()
        for physician in physicians:
            result.referring_physician.add(physician)
        return result


class CaseReportInstanceResource:

    def update(self, case_id, title=None, age=None, gender=None, sarcoma_type=None):
        """

        :type clinical_outcome: object
        """
        case = get_object_or_404(CaseReport, id=case_id)
        if title:
            case.title = title
        if age:
            case.age = age
        if title:
            case.title = title
        if gender:
            case.gender = gender
        if sarcoma_type:
            case.sarcoma_type = sarcoma_type
        case.status = CASE_STATUS['E']
        case.save()
        return case

    def approve(self, case_id):
        """
        :type clinical_outcome: object
        """

        case = get_object_or_404(CaseReport, id=case_id)
        case.status = CASE_STATUS['A']
        case.save()
        return case


    def _addabberations(self,casereport, abbrations):
        """
        :param casereport: is an casereport object
        :param abbrations: is a list of abbration objects
        :return:
        """
        for abb in abbrations:
            casereport.molecular_abberations.add(abb)
        return casereport

    def _addauthor(self,casereport, author_list):
        """

        :param casereport: is an casereport object
        :param abbrations: is a list of abbration objects
        :return:
        """
        for author in author_list:
            casereport.authorized_reps.add(author)
        return casereport



class PhysicianInstanceResource:

    def _get(self):
        pass

    def _post(self, name, email):
        phy, created = Physician.objects.get_or_create(name=name, email=email)
        return phy


class InstitutionInstanceResource:

    def _get(self):
        pass

    def _post(self, name, city, country):
        institution, created = Institution.objects.get_or_create(name=name,
            city=city, country=country )
        return institution


class AbberationInstanceResource:

    def _get(self):
        pass

    def _post(self,test,test_result):
        pass




class AbberationListResource:

    def _get(self):
        pass

    def _post(self,molecule,abberation):
        m_abbs = []
        for i,abb in enumerate(abberation):
            obj, status = MolecularAbberation.objects.get_or_create(name=abb, molecule=molecule[i])
            m_abbs.append(obj)
        return m_abbs




class AuthorizedListResource:

    def _get(self):
        pass

    def _post(self,email):
        p_doc = []
        for i in email:
            phy, created = AuthorizedRep.objects.get_or_create(email=i)
            p_doc.append(phy)
        return p_doc


class CaseReportHistoryInstanceResource:

    def get(self):
        pass

    def post(self, case, diagnosis=None, physician=None, tests=None,
              molecular_abberations=None, treatments=None):
        """

        :create the update history object for a case report
        """
        result = CaseReportHistory(case=case, physician=physician, tests=tests,
                            molecular_abberations=molecular_abberations,
                            treatments=treatments,
                            diagnosis=diagnosis)
        result.save()
        return result


class TreatmentInstanceResource:

    def _get(self):
        pass

    def _post(self, casereport, name, duration=None, treatment_type=None,
              treatment_intent=None, objective_response=None, status=None,
              notes=None):
        """

        :type Treatment: object
        """
        result = Treatment()
        result.casereport_f = casereport
        result.name = name
        result.treatment_type = treatment_type
        result.status = status
        result.duration = duration
        result.objective_response = objective_response
        result.notes = notes
        result.save()
        return result



