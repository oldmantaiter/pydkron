"""
Dkron Job Object
"""
import json


JOB_VALID_FIELDS = [
    "name",
    "schedule",
    "shell",
    "command",
    "owner",
    "owner_email",
    "success_count",
    "error_count",
    "last_success",
    "last_error",
    "disabled",
    "tags",
    "retries",
    "dependent_jobs",
    "parent_job",
    "processors",
    "concurrency"
]

JOB_READ_ONLY_FIELDS = [
    "success_count",
    "error_count",
    "last_success",
    "last_error",
    "dependent_jobs",
]


class DkronJob(dict):
    """
    Object that represents a DkronJob
    """
    def __init__(self, client, **kwargs):
        super(DkronJob, self).__init__(**kwargs)
        self._client = client

    def __getattr__(self, name):
        if name in JOB_VALID_FIELDS or name.startswith("_"):
            return self[name]
        raise KeyError("%s not a valid job field" % name)


    def __setattr__(self, name, value):
        if name in JOB_VALID_FIELDS or name.startswith("_"):
            if name in JOB_READ_ONLY_FIELDS:
                raise KeyError("%s is a read only field" % name)
            self[name] = value
            return
        raise KeyError(
            "%s not a valid job field [valid=%s]" % (
                name, ",".join(JOB_VALID_FIELDS)))

    @classmethod
    def from_dict(cls, data, client):
        """
        Unmarshal the dict into a DkronJob object
        """
        return cls(client, **data)

    def save(self):
        """
        Save the job to the provided API endpoint
        """
        return self._client.save_job(self)

    def marshal(self):
        """
        Marshal the job to a dict that can be uploaded to the server
        """
        data = {}
        for key, value in self.items():
            if key.startswith("_"):
                continue
            data[key] = value
        return json.dumps(data)

    def executions(self):
        """
        Return the executions for this rule
        """
        return self._client.get_executions(self.name)

    def run(self):
        """
        Runs this job
        """
        return self._client.run_job(self.name)

    def delete(self):
        """
        Delete this job
        """
        return self._client.delete_job(self.name)
