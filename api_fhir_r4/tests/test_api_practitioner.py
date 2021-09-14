from rest_framework import status
from rest_framework.test import APITestCase

from fhir.resources.practitioner import Practitioner
from api_fhir_r4.tests import GenericFhirAPITestMixin, FhirApiCreateTestMixin, FhirApiReadTestMixin


class PractitionerAPITests(GenericFhirAPITestMixin, FhirApiCreateTestMixin, APITestCase):

    base_url = '/api_fhir_r4/Practitioner/'
    _test_json_path = "/test/test_practitioner.json"
    _TEST_EXPECTED_NAME = "UPDATED_NAME"

    def setUp(self):
        super(PractitionerAPITests, self).setUp()

    def verify_updated_obj(self, updated_obj):
        self.assertTrue(isinstance(updated_obj, Practitioner))
        self.assertEqual(self._TEST_EXPECTED_NAME, updated_obj.name[0].family)

    def update_resource(self, data):
        data['name'][0]['family'] = self._TEST_EXPECTED_NAME
