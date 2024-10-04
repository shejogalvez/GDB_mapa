from neo4j import EagerResult, GraphDatabase, Record, Transaction, Driver
from models import PieceCreate, NodeCreate, SubNode, Log
import os

# Set up the connection details
uri = f"bolt://{ os.getenv("NEO4J_HOSTNAME", "localhost") }:7687"  # Bolt URI of your Neo4j server
 
username, password = os.getenv("NEO4J_AUTH").split('/')  # Your Neo4j username

# returns instance of driver to be used on backend
def get_db_driver() -> Driver:
    return GraphDatabase.driver(uri, auth=(username, password))

# Initialize the driver
def run_query(query: str, **kwarws) -> EagerResult:
    with GraphDatabase.driver(uri, auth=(username, password)) as driver:
        return driver.execute_query(query, kwarws, database_="neo4j")

def parse_properties(**properties):
    return f", ".join([f"{key}:{f'"val"' if type(val)==str else val}" for key, val in properties.items()])

# Example function to run a simple query
def get_all_nodes():
    query = "MATCH (n) RETURN n LIMIT 25"  # Cypher query to retrieve all nodes
    result = run_query(query)
    return result

def get_all_nodes_with_tag(tag: str | None = None, limit: int = 25):
    query = f"MATCH (n {f":{tag}" if tag else ""}) RETURN n LIMIT {limit}" 
    result = run_query(query)
    return result

def get_nodes_without_tag_connected_to_node(exclude_tag: str, node_tag = "", **match_properties):
    properties = parse_properties(match_properties)
    query = f"""MATCH (n {f":{node_tag}" if node_tag else ""} {{{properties}}}) -[]-> (c)
                WHERE NOT (c: {exclude_tag})
                RETURN c""" 
    result = run_query(query)
    return result

def get_nodes_paginated(labels: str, skip: int, limit: int):
    query = f"""MATCH (i {labels})
            RETURN i
            SKIP {skip}
            {f"LIMIT {limit}" if limit>0 else ""}"""
    result = run_query(query)
    return result

def get_piece_components(piece_id):
    #TODO: save piece_id as int
    query = f"""MATCH (:pieza {{id: "{piece_id}"}}) -[:compuesto_por]-> (i:componente)
            RETURN i"""
    result = run_query(query)
    return result

def filter_by_nodes_names_connected(name_array: list, tag: str, other_label: str = "", skip: int = 0, limit: int = 0):
    if other_label != "":
        other_label = f" :{other_label}" 
    query = f"""MATCH (n:{tag})-[r]-(connectedNode{other_label})
            WHERE connectedNode.name IN {name_array}
            RETURN DISTINCT n;
            SKIP {skip}
            {f"LIMIT {limit}" if limit>0 else ""} """
    print(query)
    result = run_query(query)
    return result

""" to leave property as dict key in results:
It's not possible with the default Cypher syntax, however if you have the apoc library installed, you can do this :

MATCH (n:A)
RETURN apoc.map.setKey({}, n.id, n{.*})"""

def create_user(username: str, hashed_password: str, salt: str, role: str):
    query = f"CREATE (n :user {{username: '{username}', hashed_password: '{hashed_password}', salt: '{salt}', role: '{role}'}})"
    run_query(query)

def create_node(tags: list[str] | None = None, **properties):
    tags = f"".join(map(lambda x : f" :{x}", tags))
    properties = parse_properties(properties)
    query = f"CREATE (n{tags} {{{properties}}})"
    run_query(query)

def get_user(username: str) -> Record | None:
    query = f"""MATCH (n:user {{username:"{username}"}})
    RETURN n"""
    records = run_query(query).records
    return records[0]['n'] if records else None

def get_forma_properties(properties: dict[str, str]) -> dict[str, str]: # TODO: mover esto al backend(?)
    FORMA_KEYS = ["alto", "ancho", "profundidad", "peso"]
    forma_properties = {}
    to_delete = []
    for key, val in properties.items():
        if key in FORMA_KEYS:
            forma_properties[key] = val
            to_delete.append(key)
    for key in to_delete:
        properties.pop(key)
    return forma_properties

def pydict_to_neo(parameters: dict) -> str:
    return ', '.join(f'{key}: {val if type(val) is not str else f'"{val}"'}' for key, val in parameters.items())

def create_component(tx, piece_id: str, component_id: str, subnodes: list[SubNode], properties: dict[str, str]):
    fp: dict = get_forma_properties(properties)
    query = """
            MATCH (p :pieza {id: $piece_id})
            MERGE (c :componente {id: $nodeId}) <-[:compuesto_por]-(p)
            MERGE (c) -[:tiene_forma]-> (f :forma)
            WITH *, $properties AS mainProps
            UNWIND mainProps AS properties
            SET c += properties
            WITH f, $f_properties AS fProps 
            UNWIND fProps AS f_properties
            SET f += f_properties
            """ + "\n".join([f"MATCH k:{n.node_label} {{id: \"{n.node_id}\"}} WITH c, k MERGE (c) -[:{n.relation_label}]- (k) SET k += {{{pydict_to_neo(n.properties)}}}"] for n in subnodes)
    #print(query)
    return tx.run(query, piece_id=piece_id, nodeId=component_id, properties=properties, f_properties=fp)

def create_update_piece(piece_id: str, components: list, subnodes: list[SubNode], properties: list[dict] ):
    results = []
    for index, component in enumerate(components):
        if not component.id:
            component.id = f"C{piece_id}_{index}"
    with GraphDatabase.driver(uri, auth=(username, password)) as driver:
        with driver.session() as session:
            with session.begin_transaction() as tx:
                query = """
                        MERGE (p :pieza {id: $nodeId})
                        WITH p, $properties AS mainProps
                        UNWIND mainProps as properties
                        SET p += properties
                        """ + "\n".join([f"WITH p MERGE (p) -[:{n.relation_label}]- (k:{n.node_label} {{id: \"{n.node_id}\"}}) SET k += {{{pydict_to_neo(n.properties)}}}" for n in subnodes])
                #print(query)
                results.append(tx.run(query, nodeId=piece_id, properties=properties).single())
                for component in components:
                    result = create_component(tx, piece_id, component.id, component.connected_nodes, component.properties)
                    results.append(result.single())
                tx.commit()
    return results

def delete_component(tx: Transaction, component_id: str, labels_to_delete: list[str]):
    query = """
            MATCH (c {id: $nodeId})
            OPTIONAL MATCH (c)--(f :forma)
            DETACH DELETE f, c
            """
    return tx.run(query, nodeId=component_id, allowerLabels=labels_to_delete)

def detete_piece(tx: Transaction, id: str, labels_to_delete: list[str]):
    query = """
            MATCH (n {id: $nodeId})
            OPTIONAL MATCH (n)--(c: componente)
            OPTIONAL MATCH (c)--(f :forma)
            DETACH DELETE f, n, c
            """
    return tx.run(query, nodeId=id, allowedLabels=labels_to_delete)

def create_log(log: Log):
    query = """
            MATCH (n :user {username: $username})
            CREATE (l :log {endpoint: $endpoint, request_method: $request_method, request_body: $request_body}) <-[:change]- (n)
            RETURN l
            """
    result = run_query(query, username=log.username, endpoint=log.endpoint, request_method=log.request_method, request_body=log.request_body)
    return result
