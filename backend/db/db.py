from neo4j import GraphDatabase
import os

# Set up the connection details
uri = f"bolt://{ os.getenv("NEO4J_HOSTNAME", "localhost") }:7687"  # Bolt URI of your Neo4j server
 
username, password = os.getenv("NEO4J_AUTH").split('/')  # Your Neo4j username

# Initialize the driver
def run_query(query: str, **kwarws):
    with GraphDatabase.driver(uri, auth=(username, password)) as driver:
        return driver.execute_query(query, kwarws, database_="neo4j")



# Example function to run a simple query
def get_all_nodes():
    query = "MATCH (n) RETURN n LIMIT 25"  # Cypher query to retrieve all nodes
    result = run_query(query)
    return result
            
