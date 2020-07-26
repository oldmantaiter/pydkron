# pydkron - Python Library for Interacting with [Dkron](http://dkron.io)

[![Build Status](https://travis-ci.org/oldmantaiter/pydkron.svg?branch=master)](https://travis-ci.org/oldmantaiter/pydkron)

## Requirements

requests

## Installing
### Pip
```
pip install pydkron
```
### Manually
```
git clone https://github.com/oldmantaiter/pydkron
cd pydkron
python setup.py install
```

## Usage Examples

```python
from pydkron.client import DkronClient

# Return all the configured jobs
client = DkronClient(hosts=["dkron01:8080", "dkron02:8080"])
for job in client.jobs():
    print "%s runs %s" % (job.name, job.schedule)

# Get a job by name
job = client.get_job("job1")

# Delete a job
job.delete()

# Create a new job
data = {
    "name": "job2",
    "schedule": "@every 2m",
    "command": "run stuff",
    "owner": "Tait Clarridge",
    "tags": {
        "role": "dkron:1",
    }
}

job = client.create_job(data)

# Update a job (change the schedule)

job.schedule = "@every 2m"
job.save()

# Run a job
job.run()

# List executions
print job.executions()
```
