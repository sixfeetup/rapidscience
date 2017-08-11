__author__ = 'yaseen'

from django.shortcuts import get_object_or_404
from casereport.models import AuthorizedRep
from casereport.models import CaseReport
from casereport.models import MolecularAbberation
from casereport.models import CaseReportHistory
from casereport.models import Treatment



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



