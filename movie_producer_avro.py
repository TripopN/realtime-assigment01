from confluent_kafka.avro import AvroProducer
from confluent_kafka.avro import CachedSchemaRegistryClient
import random
from datetime import datetime
import time
import mysql.connector

# Set up schema registry client
schema_registry = CachedSchemaRegistryClient('http://localhost:8081')  # Change this to your Schema Registry URL
my_schema = schema_registry.get_by_id(4) 
print("my_schema = ",my_schema)

# Define the Avro schema #Avro is protocal of data schema
'''new_schema_str = 
{
    "type": "record",
    "name": "TicketSale",
    "namespace": "test",
    "fields": [
        {"name":"cid","type":"string","default":""},
        {"name": "title", "type": "string"},
        {"name": "sale_ts", "type": "string"},
        {"name": "ticket_total_value", "type": "int"}
    ]
}'''

#register the new schema
'''schema_id = schema_registry.register("TicketSale", new_schema_str)
print(f"New schema registered with id: {schema_id}") '''

# Define the Avro producer
avro_producer = AvroProducer(
    {
        'bootstrap.servers': 'localhost:8097',  # Change this to your Kafka broker address
        'schema.registry.url': 'http://localhost:8081',  # Change this to your Schema Registry URL
    },
    default_value_schema=my_schema
)

topic = 'movie'

# Generate sample records
titles = ["ET", "Hulk", "Spiderman"]
prices = [12, 24, 36]
cids = ["c001","c002","c003"]

records = []
for _ in range(10):
    current_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    record = {
        'cid': random.choice(cids),
        'title': random.choice(titles),
        'sale_ts': current_time,
        'ticket_total_value': random.choice(prices),
    }
    records.append(record)

# Produce records to Kafka
for record in records:
    avro_producer.produce(topic=topic, value=record)
    print(f"Produced record: {record}")
    time.sleep(random.randint(1,2))

avro_producer.flush()


# Insert the records into MySQL
# Establish MySQL connection
db_conn = mysql.connector.connect(
    host="localhost",
    port = 3307,
    user="confluent",
    password="confluent",
    database="connect_test"
)

cursor = db_conn.cursor()

# Create an insert query for MySQL
insert_query = "INSERT INTO movie_tb (cid, title, sale_ts, ticket_total_value) VALUES (%s, %s, %s, %s)"

# Insert records into MySQL
for record in records:
    cursor.execute(insert_query, (record['cid'], record['title'], record['sale_ts'], record['ticket_total_value']))
    db_conn.commit()

cursor.close()
db_conn.close()


# Close SchemaRegistryClient
schema_registry.close()