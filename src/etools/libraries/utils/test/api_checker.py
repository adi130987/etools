# -*- coding: utf-8 -*-
import datetime

from drf_api_checker.unittest import ApiCheckerMixin as BaseApiCheckerMixin, ApiCheckerBase
from rest_framework.response import Response

from etools.applications.users.tests.factories import UserFactory


class ApiCheckerMixin(BaseApiCheckerMixin):
    def setUp(self):
        super().setUp()
        self.user = UserFactory(username='user', is_staff=True)
        self.client.login(username='user', password='test')


class ViewSetChecker(ApiCheckerBase):
    mixin = ApiCheckerMixin


class AssertTimeStampedMixin:
    def assert_modified(self, response: Response, stored: Response, path: str):
        value = response['modified']
        assert datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')

    def assert_created(self, response: Response, stored: Response, path: str):
        value = response['created']
        assert datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
