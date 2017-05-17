__author__ = 'yaseen'

from django.shortcuts import get_object_or_404
from casereport.models import AuthorizedRep
from casereport.models import CaseReport
from casereport.models import Institution
from casereport.models import MolecularAbberation
from casereport.models import Physician
from casereport.models import CaseReportHistory
from casereport.models import Treatment



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
        result.treatment_intent = treatment_intent
        if status:
            result.status = status
        result.duration = duration
        result.objective_response = objective_response
        result.notes = notes
        result.save()
        return result



