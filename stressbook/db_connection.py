import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize DynamoDB client
session = boto3.Session(
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    aws_session_token=os.environ.get('AWS_SESSION_TOKEN'),
    region_name=os.environ.get('AWS_REGION')
)
dynamodb = session.resource('dynamodb')

# Define table names
USERS_TABLE = 'users'
EVENTS_TABLE = 'events'
SEATS_TABLE = 'seats'
BOOKINGS_TABLE = 'bookings'

# Create tables if they don't exist
def create_tables():
    try:
        # Users table
        users_table = dynamodb.create_table(
            TableName=USERS_TABLE,
            KeySchema=[
                {'AttributeName': 'email', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'email', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )

        # Events table
        events_table = dynamodb.create_table(
            TableName=EVENTS_TABLE,
            KeySchema=[
                {'AttributeName': 'event_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'event_id', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )

        # Seats table
        seats_table = dynamodb.create_table(
            TableName=SEATS_TABLE,
            KeySchema=[
                {'AttributeName': 'seat_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'seat_id', 'AttributeType': 'S'},
                {'AttributeName': 'event_id', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'event_id_index',
                    'KeySchema': [
                        {'AttributeName': 'event_id', 'KeyType': 'HASH'},
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print("Created SEATS table")  # Debug print

        # Bookings table
        bookings_table = dynamodb.create_table(
            TableName=BOOKINGS_TABLE,
            KeySchema=[
                {'AttributeName': 'booking_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'booking_id', 'AttributeType': 'S'},
                {'AttributeName': 'user_id', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'user_id_index',
                    'KeySchema': [
                        {'AttributeName': 'user_id', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )

        print("Tables created successfully")
        
        # Return table references
        return {
            'users_table': dynamodb.Table(USERS_TABLE),
            'events_table': dynamodb.Table(EVENTS_TABLE),
            'seats_table': dynamodb.Table(SEATS_TABLE),
            'bookings_table': dynamodb.Table(BOOKINGS_TABLE)
        }
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print("Tables already exist")
            # Return existing table references
            return {
                'users_table': dynamodb.Table(USERS_TABLE),
                'events_table': dynamodb.Table(EVENTS_TABLE),
                'seats_table': dynamodb.Table(SEATS_TABLE),
                'bookings_table': dynamodb.Table(BOOKINGS_TABLE)
            }
        else:
            print(f"Error creating tables: {e}")
            raise e

# Get table references
tables = create_tables()
users_table = tables['users_table']
events_table = tables['events_table']
seats_table = tables['seats_table']
bookings_table = tables['bookings_table']