"""
Dkron Client Object
"""
from random import shuffle

import requests
import requests.exceptions

from six.moves import xrange

from pydkron.job import DkronJob

_GET = "get"
_POST = "post"
_DELETE = "delete"


class DkronClientException(Exception):
    """
    Generic client exception
    """
    pass

class DkronJobNotFound(Exception):
    """
    Job not found
    """
    pass


class DkronClient(object):
    """
    DkronClient is an API client for DKRON
    """
    def __init__(self, hosts):
        """
        Creates a new API client

        :param hosts: List of hosts (including port)
        """
        if not isinstance(hosts, list):
            hosts = [hosts]
        self.hosts = hosts

    def _call(self, method, endpoint, payload=None):
        """
        Call the endpoint and return the response
        """
        resp = None
        shuffle(self.hosts)
        for index in xrange(len(self.hosts)):
            url = "http://%s/v1%s" % (self.hosts[index], endpoint)
            req_args = {'timeout': 10, 'headers': {'Content-Type': 'application/json'}}
            try:
                if method == _GET:
                    resp = requests.get(url, **req_args)
                elif method == _POST:
                    resp = requests.post(
                        url, data=payload, **req_args)
                elif method == _DELETE:
                    resp = requests.delete(url, **req_args)
                break
            except requests.exceptions.RequestException:
                continue
        if resp is None:
            raise DkronClientException("No valid host found")
        return resp

    def status(self):
        """
        Return the general status of the DKRON cluster
        """
        return self._call(_GET, "/").json()

    def jobs(self):
        """
        Returns a list of jobs
        """
        data = self._call(_GET, "/jobs").json()
        return [DkronJob.from_dict(job_data, self) for job_data in data]


    def get_job(self, name):
        """
        Return a job by name
        """
        resp = self._call(_GET, "/jobs/%s" % name)
        if resp.status_code == 404:
            raise DkronJobNotFound("Job %s was not found" % name)
        return DkronJob.from_dict(resp.json(), self)

    def save_job(self, job):
        """
        Save a job to the cluster
        """
        resp = self._call(_POST, "/jobs", job.marshal())
        if resp.status_code != 201:
            raise DkronClientException("Job could not be saved [status=%d]" % resp.status_code)
        return resp.json()

    def run_job(self, name):
        """
        Run the job by name
        """
        resp = self._call(_POST, "/jobs/%s" % name)
        if resp.status_code == 404:
            raise DkronJobNotFound("Job %s was not found" % name)
        return resp.json()

    def delete_job(self, name):
        """
        Delete the job by name
        """
        resp = self._call(_DELETE, "/jobs/%s" % name)
        if resp.status_code == 404:
            raise DkronJobNotFound("Job %s was not found" % name)
        return resp.json()

    def create_job(self, data):
        """
        Create/update a job
        """
        job = DkronJob.from_dict(data, self)
        self.save_job(job)
        return job

    def get_executions(self, name):
        """
        Get the job executions for a named job
        """
        resp = self._call(_GET, "/jobs/%s/executions/" % name)
        if resp.status_code == 404:
            raise DkronJobNotFound("Job %s was not found" % name)
        return resp.json()

    def toggle(self, name):
        '''
        Enable/disable a job

        Arguments:
            name {string} -- the name of job

        Raises:
            DkronJobNotFound -- raise if the job not exists

        Returns:
            DkronJob -- a job of Dkron
        '''
        resp = self._call(_POST, "/jobs/%s/toggle" % name)
        if resp.status_code == 404:
            raise DkronJobNotFound("Job %s was not found" % name)
        return DkronJob.from_dict(resp.json(), self)
