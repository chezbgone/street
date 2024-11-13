from datetime import datetime

from common.database import the_table

_SORT_KEY = 'most_recent_stream_message_time'

def get_last_stream_message_time(id: int) -> datetime | None:
    table = the_table()
    response = table.get_item(
        Key={
            'id': id,
            'sk': _SORT_KEY,
        },
        ProjectionExpression='#t',
        ExpressionAttributeNames={
            '#t': 'timestamp'
        },
    )
    if 'Item' not in response:
        return None
    timestamp = response['Item']['timestamp']
    assert(type(timestamp) is str)
    return datetime.fromisoformat(timestamp)

def set_last_stream_message_time(id: int, timestamp: datetime):
    the_table().put_item(
        Item={
            'id': id,
            'sk': _SORT_KEY,
            'timestamp': timestamp.isoformat(),
        },
    )
