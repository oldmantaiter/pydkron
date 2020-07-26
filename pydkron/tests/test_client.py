"""
campfire.lib.archiver test functions
"""
import unittest
import json
import os

import requests_mock

from pydkron.client import DkronClient, DkronJobNotFound, DkronClientException
from pydkron.job import DkronJob


class DkronClientTestCase(unittest.TestCase):
    """
    Test cases for pydkron.client
    """
    def setUp(self):
        self.client = DkronClient(hosts=["localhost:8080"])

    def test_init(self):
        """
        DkronClient: Test __init__ has list
        """
        client = DkronClient(hosts="localhost:8080")
        self.assertEqual(
            client.hosts,
            ["localhost:8080"],
            "Exp: '%s', Got: '%s'" % (['localhost:8080'], client.hosts)
        )

    def test_status(self):
        """
        DkronClient: Test status
        """
        exp = {'awesome': 'stuff'}
        with requests_mock.Mocker() as mocker:
            mocker.register_uri(
                requests_mock.GET,
                "http://localhost:8080/v1/",
                text=json.dumps(exp),
                status_code=200
            )
            got = self.client.status()
            self.assertEqual(
                got,
                exp,
                "Exp: '%s', Got: '%s'" % (exp, got)
            )

    def test_jobs(self):
        """
        DkronClient: Test jobs
        """
        data = [
            {
                "name": "job1",
                "schedule": "@every 5h",
                "command": "testcommand"
            },
            {
                "name": "job2",
                "schedule": "@every 5h",
                "command": "testcommand2"
            }
        ]
        with requests_mock.Mocker() as mocker:
            mocker.register_uri(
                requests_mock.GET,
                "http://localhost:8080/v1/jobs",
                text=json.dumps(data),
                status_code=200,
            )
            jobs = self.client.jobs()
            self.assertEqual(
                jobs[0].name,
                "job1",
                "Incorrect job name, exp: 'job1' got '%s'" % jobs[0].name,
            )

            self.assertEqual(
                jobs[1].name,
                "job2",
                "Incorrect job name, exp: 'job2' got '%s'" % jobs[0].name,
            )

    def test_get_job(self):
        """
        DkronClient: Test get_job
        """
        data = {
            "name": "job1",
            "schedule": "@every 5h",
            "command": "testcommand"
        }

        with requests_mock.Mocker() as mocker:
            mocker.register_uri(
                requests_mock.GET,
                "http://localhost:8080/v1/jobs/job1",
                text=json.dumps(data),
                status_code=200,
            )

            job = self.client.get_job("job1")
            self.assertEqual(
                job.command,
                "testcommand",
                "Incorrect job command, exp: 'testcommand' got '%s'" % job.command
            )

    def test_get_job_not_found(self):
        """
        DkronClient: Test get_job DkronJobNotFound exception
        """
        with requests_mock.Mocker() as mocker:
            mocker.register_uri(
                requests_mock.GET,
                "http://localhost:8080/v1/jobs/job1",
                status_code=404,
            )
            self.assertRaises(DkronJobNotFound, self.client.get_job, "job1")

    def test_save_job(self):
        """
        DkronClient: Test save_job
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

            got = json.dumps(self.client.save_job(job))
            self.assertEqual(
                exp,
                got,
                "Exp: '%s', Got: '%s'" % (exp, got)
            )

    def test_save_job_exception(self):
        """
        DkronClient: Test save_job raises DkronClientException
        """
        job = DkronJob(self.client, name="job1")
        with requests_mock.Mocker() as mocker:
            mocker.register_uri(
                requests_mock.POST,
                "http://localhost:8080/v1/jobs",
                status_code=200,
            )
        self.assertRaises(DkronClientException, self.client.save_job, job)

    def test_run_job(self):
        """
        DkronClient: Test run_job
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
            got = json.dumps(self.client.run_job("job1"))
            self.assertEqual(
                exp,
                got,
                "Exp: '%s', Got: '%s'" % (exp, got)
            )

    def test_run_job_not_found(self):
        """
        DkronClient: Test run_job raises DkronJobNotFound exception
        """
        with requests_mock.Mocker() as mocker:
            mocker.register_uri(
                requests_mock.POST,
                "http://localhost:8080/v1/jobs/job1",
                status_code=404,
            )
            self.assertRaises(DkronJobNotFound, self.client.run_job, "job1")

    def test_delete_job(self):
        """
        DkronClient: Test delete_job
        """
        with requests_mock.Mocker() as mocker:
            exp = "[]"
            mocker.register_uri(
                requests_mock.DELETE,
                "http://localhost:8080/v1/jobs/job1",
                text=exp,
                status_code=200,
            )
            got = json.dumps(self.client.delete_job("job1"))
            self.assertEqual(
                exp,
                got,
                "Exp: '%s', Got: '%s'" % (exp, got)
            )

    def test_delete_job_not_found(self):
        """
        DkronClient: Test delete_job raises DkronJobNotFound exception
        """
        with requests_mock.Mocker() as mocker:
            mocker.register_uri(
                requests_mock.DELETE,
                "http://localhost:8080/v1/jobs/job1",
                status_code=404,
            )
            self.assertRaises(DkronJobNotFound, self.client.delete_job, "job1")

    def test_create_job(self):
        """
        DkronClient: Test create_job
        """
        data = {
            "name": "job1",
            "schedule": "@every 5m",
            "command": "testcommand",
            "shell": True,
            "tags": {
                "role": "dkron:1",
            }
        }
        with requests_mock.Mocker() as mocker:
            mocker.register_uri(
                requests_mock.POST,
                "http://localhost:8080/v1/jobs",
                text=json.dumps(data),
                status_code=201,
            )
            got = json.loads(self.client.create_job(data).marshal())
            self.assertEqual(
                data,
                got,
                "Exp: '%s', Got: '%s'" % (data, got)
            )

    def test_get_executions(self):
        """
        DkronClient: Test get_executions
        """
        with requests_mock.Mocker() as mocker:
            exp = "[]"
            mocker.register_uri(
                requests_mock.GET,
                "http://localhost:8080/v1/jobs/job1/executions/",
                text=exp,
                status_code=200,
            )
            got = json.dumps(self.client.get_executions("job1"))
            self.assertEqual(
                exp,
                got,
                "Exp: '%s', Got: '%s'" % (exp, got)
            )

    def test_get_executions_not_found(self):
        """
        DkronClient: Test get_executions raises DkronJobNotFound exception
        """
        with requests_mock.Mocker() as mocker:
            mocker.register_uri(
                requests_mock.GET,
                "http://localhost:8080/v1/jobs/job1/executions/",
                status_code=404,
            )
            self.assertRaises(DkronJobNotFound, self.client.get_executions, "job1")

    def test_toggle(self):
        """
        DkronClient: Test toggle
        """
        data = {
            "name": "job1",
            "displayname": "string",
            "schedule": "@every 10s",
            "timezone": "Europe/Berlin",
            "owner": "Platform Team",
            "owner_email": "platform@example.com",
            "success_count": 0,
            "error_count": 0,
            "last_success": "2020-07-26T01:44:06.459Z",
            "last_error": "2020-07-26T01:44:06.459Z",
            "disabled": True,
            "tags": {
                "server": "true"
            },
            "metadata": {
                "office": "Barcelona"
            },
            "retries": 2,
            "parent_job": "parent_job",
            "dependent_jobs": [
                "dependent_job"
            ],
            "processors": {
                "files": {
                    "forward": True
                }
            },
            "concurrency": "allow",
            "executor": "shell",
            "executor_config": {
                "command": "echo 'Hello from Dkron'"
            },
            "status": "success"
        }
        with requests_mock.Mocker() as mocker:
            mocker.register_uri(
                requests_mock.POST,
                "http://localhost:8080/v1/jobs/job1/toggle",
                text=json.dumps(data),
                status_code=200,
            )
            job = self.client.toggle("job1")
            exp = data["name"]
            got = job.name
            self.assertEqual(
                got,
                exp,
                "Incorrect job command, exp: '%s' got '%s'" % (exp, got)
            )

    def test_toggle_not_found(self):
        """
        DkronClient: Test toggle DkronJobNotFound exception
        """
        with requests_mock.Mocker() as mocker:
            mocker.register_uri(
                requests_mock.POST,
                "http://localhost:8080/v1/jobs/job1/toggle",
                status_code=404,
            )
            self.assertRaises(DkronJobNotFound, self.client.toggle, "job1")
