from datetime import datetime
from db_connection import dynamodb, dynamodb_client, BOOKINGS_TABLE, EVENTS_TABLE , SEATS_TABLE
from botocore.exceptions import ClientError
import uuid

# Instead, just get the table reference
bookings_table = dynamodb.Table(BOOKINGS_TABLE)
events_table = dynamodb.Table(EVENTS_TABLE)
seats_table = dynamodb.Table(SEATS_TABLE)

def create_booking(user_id, event_id, section, quantity, price_per_ticket, event_name, event_location):
    """Create a new booking using DynamoDB transactions"""
    try:
        booking_id = str(uuid.uuid4())
        booking = {
            'booking_id': {'S': booking_id},  # ✅ Convert to DynamoDB format
            'user_id': {'S': user_id},
            'event_id': {'S': event_id},
            'status': {'S': 'completed'},
            'timestamp': {'S': datetime.now().isoformat()},
            'total_price': {'N': str(price_per_ticket * quantity)},  # ✅ Convert number to string
            'seat_details': {
                'M': {  # ✅ Nested dict should be converted to "M"
                    'section': {'S': section},
                    'quantity': {'N': str(quantity)},
                    'price_per_ticket': {'N': str(price_per_ticket)}
                }
            },
            'event_name': {'S': event_name},
            'event_location': {'S': event_location}
        }

        # Use DynamoDB transactions
        response = dynamodb_client.transact_write_items(
            TransactItems=[
                {
                    'Put': {
                        'TableName': bookings_table.name,
                        'Item': booking,
                        'ConditionExpression': 'attribute_not_exists(booking_id)'
                    }
                },
                {
                    'Update': {
                        'TableName': events_table.name,
                        'Key': { 'event_id': {'S': event_id} },
                        'UpdateExpression': 'SET available_tickets = available_tickets - :qty, sold_tickets = sold_tickets + :qty',
                        'ConditionExpression': 'available_tickets >= :qty',
                        'ExpressionAttributeValues': { ':qty': {'N': str(quantity)} }
                    }
                },
                {
                    'Update': {
                        'TableName':  seats_table.name,   
                        'Key': { 'seat_id': {'S': f'seat_section_{event_id}_{section}'} }, 
                        'UpdateExpression': 'SET available_tickets = available_tickets - :qty, sold_tickets = sold_tickets + :qty',
                        'ConditionExpression': 'available_tickets >= :qty',
                        'ExpressionAttributeValues': { ':qty': {'N': str(quantity)} }
                    }  
                }
            ]
        )
        return {"success": True, "event_id": event_id , "section:" : section , "Amount Of Tickets:": quantity}
    except ClientError as e:
        if e.response['Error']['Code'] == 'TransactionCanceledException':
            return {"error": "Not enough tickets available"}
        return {"error": str(e)}

def get_user_bookings(user_id):
    """Get all bookings for a specific user"""
    try:
        response = bookings_table.query(
            IndexName='user_id_index',
            KeyConditionExpression='user_id = :uid',
            ExpressionAttributeValues={':uid': user_id}
        )
        return response.get('Items', [])
    except ClientError as e:
        print(f"Error fetching user bookings: {e}")
        return []