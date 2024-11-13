from decimal import Decimal

from common.database import the_table

_SORT_KEY = 'currency'

def get_user_points(id: int) -> int:
    """
    Returns the amount of currency in chatter `id`'s wallet.
    """
    response = the_table().get_item(
        Key={
            'id': id,
            'sk': _SORT_KEY,
        },
        ProjectionExpression='amount',
    )
    if 'Item' not in response:
        return 0
    amount = response['Item']['amount']
    assert(type(amount) is Decimal)
    return int(amount)

def add_to_user(id: int, amount: int) -> int:
    """
    Add `amount` currency to chatter `id`'s wallet.
    Returns the new amount the user has.
    """
    response = the_table().update_item(
        Key={
            'id': id,
            'sk': _SORT_KEY,
        },
        UpdateExpression='ADD amount :amount',
        ExpressionAttributeValues={
            ':amount': amount
        },
        ReturnValues='UPDATED_NEW',
    )
    new_amount = response['Attributes']['amount']
    assert(type(new_amount) is Decimal)
    return int(new_amount)
