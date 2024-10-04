import uuid
import pytz
import datetime

def set_metadata_fields(resource):

    timestamp = str(datetime.datetime.now(tz=pytz.timezone('Europe/Copenhagen')))

    resource['metadata']['uid']=str(uuid.uuid4())
    resource['metadata']['creationTimestamp'] = timestamp
    resource['metadata']['updatedTimestamp'] = timestamp

    if not resource['metadata'].get('labels'):
        resource['metadata']['labels'] = {}

    if not resource['metadata'].get('annotations'):
        resource['metadata']['annotations'] = {}


    return resource