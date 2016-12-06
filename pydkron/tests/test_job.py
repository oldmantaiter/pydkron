"""
campfire.lib.archiver test functions
"""
import unittest
import json
import os

import requests_mock

from pydkron.job import DkronJob
from pydkron.client import DkronClient


class DkronJobTestCase(unittest.TestCase):
    """
    Test cases for pydkron.client
    """

    def setUp(self):
        self.client = DkronClient(hosts=["localhost:8080"])

    def test_get_invalid_field(self):
        """
        DkronJob: Test getting invalid field
        """
        job = DkronJob(None, name="job1")
        with self.assertRaises(KeyError):
            _ = job.awesome

    def test_set_invalid_field(self):
        """
        DkronJob: Test setting invalid field
        """
        job = DkronJob(None, name="job1")
        with self.assertRaises(KeyError):
            job.awesome = True

    def test_set_read_only_field(self):
        """
        DkronJob: Test setting invalid field
        """
        job = DkronJob(None, name="job1")
        with self.assertRaises(KeyError):
            job.success_count = 1000

    def test_save(self):
        """
        DkronJob: Test saving job
        """
        job = DkronJob(self.client, name="job1")
        with requests_mock.Mocker() as mocker:
            exp = job.marshal()
            mocker.register_uri(
                requests_mock.POST,
                "http://localhost:8080/v1/jobs",
                text=exp,
                status_code=201,
            )

            got = json.dumps(job.save())
            self.assertEqual(
                exp,
                got,
                "Exp: '%s', Got: '%s'" % (exp, got)
            )

    def test_get_executions(self):
        """
        DkronJob: Test executions
        """
        job = DkronJob(self.client, name="job1")
        with requests_mock.Mocker() as mocker:
            exp = "[]"
            mocker.register_uri(
                requests_mock.GET,
                "http://localhost:8080/v1/executions/job1",
                text=exp,
                status_code=200,
            )
            got = json.dumps(job.executions())
            self.assertEqual(
                exp,
                got,
                "Exp: '%s', Got: '%s'" % (exp, got)
            )

    def test_run_job(self):
        """
        DkronJob: Test run
        """
        job = DkronJob(self.client, name="job1")
        with requests_mock.Mocker() as mocker:
            exp = job.marshal()
            mocker.register_uri(
                requests_mock.POST,
                "http://localhost:8080/v1/jobs/job1",
                text=exp,
                status_code=200,
            )
            got = json.dumps(job.run())
            self.assertEqual(
                exp,
                got,
                "Exp: '%s', Got: '%s'" % (exp, got)
            )

    def test_delete_job(self):
        """
        DkronJob: Test delete
        """
        job = DkronJob(self.client, name="job1")
        with requests_mock.Mocker() as mocker:
            exp = job.marshal()
            mocker.register_uri(
                requests_mock.DELETE,
                "http://localhost:8080/v1/jobs/job1",
                text=exp,
                status_code=200,
            )
            got = json.dumps(job.delete())
            self.assertEqual(
                exp,
                got,
                "Exp: '%s', Got: '%s'" % (exp, got)
            )
