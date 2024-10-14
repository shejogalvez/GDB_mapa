from neo4j import EagerResult, GraphDatabase, Record, Transaction, Driver, Result
from models import PieceCreate, NodeCreate, SubNode, Log, NODE_KEYS, QueryFilter, Filter
from typing import Any
import os

# Set up the connection details
uri = f"bolt://{ os.getenv("NEO4J_HOSTNAME", "localhost") }:7687"  # Bolt URI of your Neo4j server
 
username, password = os.getenv("NEO4J_AUTH").split('/')  # Your Neo4j username

def _get_data_only(result: Result):
    return result.data()

# returns instance of driver to be used on backend
def get_db_driver() -> Driver:
    return GraphDatabase.driver(uri, auth=(username, password))

# Initialize the driver
def run_query(query: str, database_="neo4j", **kwarws) -> EagerResult:
    with GraphDatabase.driver(uri, auth=(username, password)) as driver:
        return driver.execute_query(query, kwarws, database_=database_, result_transformer_=_get_data_only)

## UTILS ##
# Parse dict and returns str to match properties in cypher query
def parse_properties(**properties):
    return "{"+{", ".join([f"{key}:${key}" for key in properties])}+"}"

def _get_forma_properties(properties: dict[str, str]) -> dict[str, str]: # TODO: mover esto al backend(?)
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

# creates query to connect each node to the main node
def parse_subnodes(subnodes: list[SubNode], main_node_key: str):
    return "\n".join(
    [f"""WITH DISTINCT {main_node_key}
        optional MATCH ({main_node_key}) -[relation :{n.relation_label}]- ()
        DELETE relation 
        MERGE (k:{n.node_label} {{id: \"{n.node_id}\"}}) 
        WITH DISTINCT {main_node_key}, k
        SET k += {{{pydict_to_neo(n.properties)}}}
        CREATE ({main_node_key}) -[:{n.relation_label}]-> (k)""" for n in subnodes])

def parse_operation(operation_str: str, key: str) -> str:
    match operation_str:
        case "=":
            return f"= ${key}"
        case ">=":
            return f">= ${key}"
        case "<":
            return f"< ${key}"
        case "contains":
            return f"contains(${key})"

def parse_filters(args: dict[str, list[Filter]]) -> tuple[dict[str, str], dict[str, Any]]:
    if (not args): return ""
    # for each node type store WHERE statements filtering properties
    query_expressions = dict()
    for label, filters in args.items():
        # create WHERE statement and append to dict
        query_expression = "WHERE "
        query_expression += " AND ".join((f"{label}.{x.key} {parse_operation(x.operation, f"{label}_{x.key}")}" for x in filters)) + "\n"
        query_expressions[label] = query_expression
        # create kwargs to add to execute_query()
        query_kwargs = dict([(f"{label}_{x.key}", x.val) for x in filters])
    return query_expressions, query_kwargs

def where_clause_from_label(query_expressions: dict[str, str], label: str) -> str:
    return query_expressions[label] if label in query_expressions else ""

## DB QUERIES ##

def get_all_nodes_property_filter(tag: str | None = None, properties_filter: dict[str, list[Filter]] = None, limit: int = 100, skip:int=0):
    properties_filter_clause, query_kwargs = parse_filters(properties_filter)
    query = f"MATCH (pieza {f":{tag}" if tag else ""}) {properties_filter_clause[tag]} RETURN pieza SKIP $skip LIMIT $limit" 
    print(query, query_kwargs)
    result = run_query(query, limit=limit, skip=skip, **query_kwargs)
    return result

def get_nodes_without_tag_connected_to_node(exclude_tag: str, node_tag = "", **match_properties):
    properties = parse_properties(**match_properties)
    query = f"""MATCH (n {f":{node_tag}" if node_tag else ""} {properties}) -[]-> (c)
                WHERE NOT (c: {exclude_tag})
                RETURN c""" 
    print(query)
    result = run_query(query, **match_properties)
    return result

def get_nodes_paginated(labels: str, skip: int, limit: int): #TODO: verify labels
    query = f"""MATCH (i {labels})
            RETURN i
            SKIP $skip
            LIMIT $limit"""
    result = run_query(query, skip=skip, limit=max(limit, 0))
    return result

PIEZAS_RELATED_NODES = ["pais", "localidad", "exposicion", "cultura", "imagen"]

def get_pieces_info_paginated(skip: int, limit: int):
    query= f"""
    MATCH (pieza: pieza)
    {"\n".join(f"OPTIONAL MATCH (pieza) --> ({label}:{label})" for label in PIEZAS_RELATED_NODES)}
    RETURN elementid(pieza) as id, pieza, pais, localidad, cultura, exposicion, imagen
    SKIP $skip
    {f"LIMIT $limit" if limit>0 else ""}"""
    result = run_query(query, skip=skip, limit=limit)
    return result

def get_pieces_info_paginated_filtered(query_filters: dict[str, list[Filter]], skip: int, limit: int):
    properties_filter_clauses, query_kwargs = parse_filters(query_filters)
    match_nodes_statement = f"MATCH (pieza: pieza) {where_clause_from_label(properties_filter_clauses)}"
    for label in PIEZAS_RELATED_NODES:
        match_nodes_statement += f"OPTIONAL MATCH (pieza) --> ({label}:{label}) {where_clause_from_label(properties_filter_clauses, label)}"
    query= f"""
    {match_nodes_statement}
    RETURN elementid(pieza) as id, pieza, pais, localidad, cultura, exposicion, imagen
    SKIP $skip
    {f"LIMIT $limit" if limit>0 else ""}"""
    result = run_query(query, skip=skip, limit=limit, **query_kwargs)
    return result

def get_piece_components(piece_id):
    #TODO: save piece_id as int
    query = f"""
    MATCH (:pieza {{id: "{piece_id}"}}) -[:compuesto_por]-> (componente:componente)
    OPTIONAL MATCH (componente) -[]-> (forma:forma)
    OPTIONAL MATCH (componente) -[]-> (ubicacion:ubicacion)
    OPTIONAL MATCH (componente) -[]-> (imagen:imagen)
    RETURN  elementid(componente) as id, componente, forma, ubicacion, imagen"""
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

def create_user(username: str, hashed_password: str, salt: str, role: str):
    query = f"CREATE (n :user {{username: '{username}', hashed_password: '{hashed_password}', salt: '{salt}', role: '{role}'}})"
    run_query(query)

def create_node(tags: list[str] | None = None, **properties):
    tags = f"".join(map(lambda x : f" :{x}", tags))
    properties_query = parse_properties(properties)
    query = f"CREATE (n{tags} {properties_query})"
    run_query(query, **properties)

def get_user(username: str) -> Record | None:
    query = f"""MATCH (n:user {{username:"{username}"}})
    RETURN n"""
    records = run_query(query)
    return records[0]['n'] if records else None

def create_update_component(piece_id: str, component_id: str | None, subnodes: list[SubNode], properties: dict[str, str], tx:Transaction =None):
    fp: dict = _get_forma_properties(properties)
    if (component_id):
        clause = "MATCH (c :componente)<-[:compuesto_por]-(p) WHERE elementid(n) = $component_id"
    else:
        clause = "CREATE (c :componente)<-[:compuesto_por]-(p)"
    query = f"""
            MATCH (p :pieza) WHERE elementid(p) = $piece_id
            {clause}
            MERGE (c) -[:tiene_forma]-> (f :forma)
            WITH *, $properties AS mainProps
            UNWIND mainProps AS properties
            SET c += properties
            WITH c, f, $f_properties AS fProps 
            UNWIND fProps AS f_properties
            SET f += f_properties
            """ + parse_subnodes(subnodes, "c") + "RETURN c"
    print(query)
    if tx:
        return tx.run(query, piece_id=piece_id, nodeId=component_id, properties=properties, f_properties=fp)
    else:
        return run_query(query, piece_id=piece_id, nodeId=component_id, properties=properties, f_properties=fp)

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
                        """ + parse_subnodes(subnodes, "p") + "RETURN elementid(p), p"
                print(query)
                results.append(tx.run(query, nodeId=piece_id, properties=properties).single())
                for component in components:
                    result = create_update_component(piece_id, component.id, component.connected_nodes, component.properties, tx)
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
