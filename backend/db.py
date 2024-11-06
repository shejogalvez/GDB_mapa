from neo4j import EagerResult, GraphDatabase, Record, Transaction, Driver, Result
from models import PieceCreate, NodeCreate, SubNode, Log, QueryFilter, Filter, NODES_RELATIONS
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

def parse_labels(labels: list[str]) -> str:
    return f":{' :'.join(labels)} " if labels else ""

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

def pydict_to_neo(parameters: dict|None) -> str:
    if (not parameters): return ""
    return ', '.join(f'{key}: {val if type(val) is not str else f'"{val}"'}' for key, val in parameters.items())

# creates query to connect each node to the main node
def parse_subnode(n: SubNode, main_node_key: str, main_node_label: str):
    relation_label = NODES_RELATIONS[(main_node_label, n.node_label)]
    CREATE_QUERY = f"""MERGE (k:{n.node_label} {{{n.id_key}: \"{n.node_id}\"}}) 
        WITH DISTINCT {main_node_key}, k
        SET k += {{{pydict_to_neo(n.properties)}}}
        CREATE ({main_node_key}) -[:{relation_label}]-> (k)""" if n.node_id else ""
    match n.method:
        case 'CREATE':
            return CREATE_QUERY
        case 'UPDATE':
            return f"optional MATCH ({main_node_key}) -[relation]- (:{n.node_label}) DELETE relation " + CREATE_QUERY
        case 'DELETE':
            return f"optional MATCH ({main_node_key}) -- (k :{n.node_label} {{{n.id_key}: \"{n.node_id}\"}}) DETACH DELETE k"
        case 'DETACH':
            f"optional MATCH ({main_node_key}) -[relation]- (k :{n.node_label} {{{n.id_key}: \"{n.node_id}\"}}) DELETE relation"


def parse_subnodes(subnodes: list[SubNode], main_node_key: str, main_node_label: str):
    return "\n".join(
    [f"""WITH DISTINCT {main_node_key}
        {parse_subnode(n, main_node_key, main_node_label)}""" for n in subnodes])

def parse_operation(operation_str: str, key: str) -> str:
    match operation_str:
        case "=":
            return f"= ${key}"
        case ">=":
            return f">= ${key}"
        case ">":
            return f"> ${key}"
        case "<=":
            return f"<= ${key}"
        case "<":
            return f"< ${key}"
        case "contains":
            return f"contains(${key})"

def parse_filters(args: dict[str, list[Filter]]) -> tuple[dict[str, str], dict[str, Any]]:
    if (not args): return ""
    # for each node type store WHERE statements filtering properties
    query_expressions = dict()
    query_kwargs = dict()
    for label, filters in args.items():
        # list of filters may be empty
        if not filters: continue
        # create WHERE statement and append to dict
        query_expression = "WHERE "
        # concatenates conditions and uses the token f"{label}_{x.key}" to encode the arg value as query argument
        query_expression += " AND ".join((f"{label}.{x.key} {parse_operation(x.operation, f"{label}_{x.key}")}" for x in filters)) + "\n"
        query_expressions[label] = query_expression
        # create kwargs to add to execute_query() and merge them with previous labels
        query_kwargs = dict([(f"{label}_{x.key}", x.val) for x in filters]) | query_kwargs
    return query_expressions, query_kwargs

def match_clause_from_label(query_expressions: dict[str, str], label: str) -> str:
    return f"MATCH (pieza) --> ({label}:{label}) {query_expressions[label]}" if label in query_expressions else f"OPTIONAL MATCH (pieza) --> ({label}:{label})"

def where_clause_from_label(query_expressions: dict[str, str], label: str) -> str:
    return query_expressions[label] if label in query_expressions else ""

def skip_limit_clause(limit: int) -> str:
    return "SKIP $skip " + "LIMIT $limit" if limit>0 else ""

## DB QUERIES ##

def get_all_nodes_property_filter(tag: str | None = None, properties_filter: list[Filter] = None, limit: int = 100, skip:int=0):
    properties_filter_clause, query_kwargs = parse_filters({"n": properties_filter})
    query = f"MATCH (n {f":{tag}" if tag else ""}) {properties_filter_clause["n"]} RETURN elementid(n) as id, properties(n) as props SKIP $skip LIMIT $limit" 
    # print(query, query_kwargs)
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

def get_nodes_paginated(labels: str, skip: int, limit: int):
    query = f"""MATCH (i {parse_labels(labels)})
            RETURN elementid(i) as id, properties(i) as properties 
            {skip_limit_clause(limit)}"""
    result = run_query(query, skip=skip, limit=limit)
    return result

def get_nodes_as_tree(labels: list[str], relation_label: str, root_val: Any = "root"):
    query = f"""MATCH p=(n {parse_labels(labels)} {{name: $root}})-[:{relation_label}*]->(m)
        WITH COLLECT(p) AS ps
        CALL apoc.paths.toJsonTree(ps) yield value
        RETURN value;"""
    result = run_query(query, root=root_val)
    return result

PIEZAS_RELATED_NODES = ["pais", "localidad", "exposicion", "cultura", "imagen"]
MATCH_RELATED_NODES = "\n".join(f"OPTIONAL MATCH (pieza) --> ({label}:{label})" for label in PIEZAS_RELATED_NODES)
RETURN_RELATED_NODES = ",".join(PIEZAS_RELATED_NODES)

def get_pieces_info_paginated(skip: int, limit: int):
    pre_query= f"MATCH (pieza: pieza) {MATCH_RELATED_NODES}"
    post_query = f"RETURN elementid(pieza) as id, pieza, {RETURN_RELATED_NODES} {skip_limit_clause(limit)}"
    query = pre_query + post_query
    result = run_query(query, skip=skip, limit=limit)
    query_count = pre_query + "RETURN count(*) as count"
    count = run_query(query_count, skip=skip, limit=limit)[0]
    return result, count

def get_pieces_info_paginated_filtered(query_filters: dict[str, list[Filter]], skip: int, limit: int):
    """ obtiene propiedades de piezas y de nodos relacionados de `limit` piezas, saltandose los primeros `skip` resultados
    
    se pueden filtrar los elementos por propiedades de cada nodo asociando a un ``label:str`` una lista de 
    ``filtros:tuple[key:str, operation:str, val:Any]`` retornando finalmente solo los valores que cumplan operation(key, val) para cada filtro

    Returns
    -------
    ``list(id:str, pieza:dict, pais:dict, localidad:dict, exposicion:dict, cultura:dict, imagen:dict``)"""
    properties_filter_clauses, query_kwargs = parse_filters(query_filters)
    print(properties_filter_clauses, query_kwargs)
    match_nodes_statement = f"MATCH (pieza: pieza) {where_clause_from_label(properties_filter_clauses, "pieza")}"
    for label in PIEZAS_RELATED_NODES:
        match_nodes_statement += f"{match_clause_from_label(properties_filter_clauses, label)}"
    query= f"""
    {match_nodes_statement}
    RETURN elementid(pieza) as id, pieza, {RETURN_RELATED_NODES}
    {skip_limit_clause(limit)}"""
    result = run_query(query, skip=skip, limit=limit, **query_kwargs)
    query_count = match_nodes_statement + "RETURN count(*) as count"
    count = run_query(query_count, skip=skip, limit=limit, **query_kwargs)[0]
    return result, count

def get_pieces_with_components_paginated(skip: int, limit: int):
    pre_query= f"MATCH (pieza: pieza) {MATCH_RELATED_NODES}"
    get_components_sub_query = """
    CALL {
        WITH *
        MATCH (pieza) -[:compuesto_por]-> (componente:componente)
        OPTIONAL MATCH (componente) -[]-> (forma:forma)
        OPTIONAL MATCH (componente) -[]-> (ubicacion:ubicacion)
        OPTIONAL MATCH (componente) -[]-> (imagen:imagen)
        WITH componente, forma, ubicacion, collect(imagen) as imagenes
        RETURN DISTINCT {id:elementid(componente), componente:componente, forma:forma, ubicacion:ubicacion, imagenes:imagenes} as componentes
    }
    """
    post_query = f"RETURN elementid(pieza) as id, pieza, {RETURN_RELATED_NODES}, componentes {skip_limit_clause(limit)}"
    query = pre_query + get_components_sub_query + post_query
    result = run_query(query, skip=skip, limit=limit)
    query_count = "MATCH (pieza:pieza) RETURN count(*) as count"
    count = run_query(query_count, skip=skip, limit=limit)[0]
    return result, count

def get_pieces_with_components_paginated_filtered(query_filters: dict[str, list[Filter]], skip: int, limit: int):

    properties_filter_clauses, query_kwargs = parse_filters(query_filters)
    print(properties_filter_clauses, query_kwargs)
    match_nodes_statement = f"MATCH (pieza: pieza) {where_clause_from_label(properties_filter_clauses, "pieza")}"
    for label in PIEZAS_RELATED_NODES:
        match_nodes_statement += f"{match_clause_from_label(properties_filter_clauses, label)}"
    get_components_sub_query = """
    CALL {
        WITH *
        MATCH (pieza) -[:compuesto_por]-> (componente:componente)
        OPTIONAL MATCH (componente) -[]-> (forma:forma)
        OPTIONAL MATCH (componente) -[]-> (ubicacion:ubicacion)
        OPTIONAL MATCH (componente) -[]-> (imagen:imagen)
        WITH componente, forma, ubicacion, collect(imagen) as imagenes
        RETURN DISTINCT {id:elementid(componente), componente:componente, forma:forma, ubicacion:ubicacion, imagenes:imagenes} as componentes
    }
    """
    query= f"""
    {match_nodes_statement} {get_components_sub_query}
    RETURN elementid(pieza) as id, pieza, {RETURN_RELATED_NODES}, componentes
    {skip_limit_clause(limit)}"""
    result = run_query(query, skip=skip, limit=limit, **query_kwargs)
    query_count = match_nodes_statement + "RETURN count(*) as count"
    count = run_query(query_count, skip=skip, limit=limit, **query_kwargs)[0]
    return result, count

def get_piece_components(piece_id):
    """ obtiene pieza con sus componentes y sus nodos relacionados
    Parameters
    ----------
    piece_id:str
        propiedad `id` de pieza

    Returns
    -------
    ``list(id:str, componente:node, forma:node, ubicacion:node, imagen:node)``"""
    query = f"""
    MATCH (p) -[:compuesto_por]-> (componente:componente) WHERE elementid(p) = $piece_id
    OPTIONAL MATCH (componente) -[]-> (forma:forma)
    OPTIONAL MATCH (componente) -[]-> (ubicacion:ubicacion)
    OPTIONAL MATCH (componente) -[]-> (imagen:imagen)
    WITH componente, forma, ubicacion, collect(imagen) as imagenes
    RETURN DISTINCT elementid(componente) as id, componente, forma, ubicacion, imagenes"""
    with GraphDatabase.driver(uri, auth=(username, password)) as driver:
        with driver.session() as session:
            with session.begin_transaction() as tx:
                components = tx.run(query, piece_id=piece_id).data()
                piece = get_piece_by_elementid(piece_id, tx)
                print(piece, components)
    return piece, components

def get_piece_by_elementid(piece_id, tx:Transaction=None):
    query = f"""
    MATCH (pieza) WHERE elementid(pieza) = $piece_id
    {MATCH_RELATED_NODES}
    WITH pieza, pais, localidad, exposicion, cultura, collect(imagen) as imagenes
    RETURN DISTINCT elementid(pieza) as id, pieza, pais, localidad, exposicion, cultura, imagenes"""
    if tx:
        result = tx.run(query, piece_id=piece_id).data()
    else: 
        result = run_query(query, piece_id=piece_id)
    return result[0] if result else None

def filter_by_nodes_names_connected(name_array: list, tag: str, other_label: str = "", skip: int = 0, limit: int = 0):
    if other_label:
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
    "crea usuario en db con `username: str, hashed_password: str, salt: str, role: str`"
    query = f"CREATE (n :user {{username: '{username}', hashed_password: '{hashed_password}', salt: '{salt}', role: '{role}'}})"
    run_query(query)

def create_node(tags: list[str] | None = None, **properties):
    # TODO: validate tags (labels)
    tags = f"".join(map(lambda x : f" :{x}", tags))
    properties_query = parse_properties(properties)
    query = f"CREATE (n{tags} {properties_query})"
    run_query(query, **properties)

def get_user(username: str) -> Record | None:
    "Retorna el primer usuario con user.username == ``username``, None si no existe"
    query = f"""MATCH (n:user {{username:"{username}"}})
    RETURN n"""
    records = run_query(query)
    return records[0]['n'] if records else None

def create_update_component(piece_id: str, component_id: str | None, subnodes: list[SubNode], properties: dict[str, str], tx:Transaction =None):
    """create component for a piece, or edits component properties and connections if component_id is provided
    
    connections are passed ass a list of SubNodes where you indicate a property to match, also properties
    of connected nodes can be updated"""
    fp: dict = _get_forma_properties(properties)
    if (component_id):
        clause = "MATCH (c :componente)<-[:compuesto_por]-(p) WHERE elementid(c) = $component_id"
    else:
        clause = "CREATE (c :componente)<-[:compuesto_por]-(p)"
    query = f"""
            MATCH (p) WHERE elementid(p) = $piece_id
            {clause}
            MERGE (c) -[:tiene_forma]-> (f :forma)
            WITH *, $properties AS mainProps
            UNWIND mainProps AS properties
            SET c += properties
            WITH c, f, $f_properties AS fProps 
            UNWIND fProps AS f_properties
            SET f += f_properties
            """ + parse_subnodes(subnodes, "c", "componente") + "RETURN c"
    print(query)
    if tx:
        return tx.run(query, piece_id=piece_id, component_id=component_id, properties=properties, f_properties=fp)
    else:
        return run_query(query, piece_id=piece_id, component_id=component_id, properties=properties, f_properties=fp)

def create_update_piece(piece_id: str|None, components: list[NodeCreate], subnodes: list[SubNode], properties: list[dict] ):
    """
    creates or update a piece if ``piece_id`` already exists, sets ``properties`` of piece and then creates or update each component

    connections of piece and components are passed as a list of SubNodes where you indicate a property to match, also properties
    of connected nodes can be updated
    """
    results = []
    with GraphDatabase.driver(uri, auth=(username, password)) as driver:
        with driver.session() as session:
            with session.begin_transaction() as tx:
                if (piece_id):
                    start_clause = "MATCH (p) WHERE elementid(p) = $nodeId"
                else:
                    start_clause = "CREATE (p :pieza)"
                query = start_clause + """
                        WITH p, $properties AS mainProps
                        UNWIND mainProps as properties
                        SET p += properties
                        """ + parse_subnodes(subnodes, "p", "pieza") + " RETURN elementid(p), p"
                print(query, components)
                result = tx.run(query, nodeId=piece_id, properties=properties).single().data()
                piece_element_id = result['elementid(p)']
                results.append(result)
                for component in components:
                    result = create_update_component(piece_element_id, component.id, component.connected_nodes, component.properties, tx).single()
                    if result: # TODO: give error message when component update fails
                        results.append(result.data())
                tx.commit()
    return results

def delete_component(tx: Transaction, component_id: str):
    """deletes componente, deletes edges and nodes that depend on componente"""
    query = """
            MATCH (c {id: $nodeId})
            OPTIONAL MATCH (c)--(f :forma)
            OPTIONAL MATCH (c)--(i :imagen)
            DETACH DELETE f, c, i
            """
    return tx.run(query, nodeId=component_id)

def detete_piece(tx: Transaction, id: str):
    """Deletes pieza, deletes edges and nodes that depend on pieza"""
    query = """
            MATCH (n {id: $nodeId})
            OPTIONAL MATCH (n)--(c: componente)
            OPTIONAL MATCH (c)--(f :forma)
            OPTIONAL MATCH (n)--(in :imagen)
            OPTIONAL MATCH (c)--(ic :imagen)
            DETACH DELETE f, n, c, in, ic
            """
    return tx.run(query, nodeId=id)

def delete_user(username: str):
    query = """
            MATCH (n:user {username: $username})
            DETACH DELETE n
            """
    return run_query(query, username=username)

def create_log(log: Log):
    """creates a log connection between"""
    query = """
            MATCH (user :user {username: $username}), (n) WHERE elementid(n) = $node_id
            CREATE (n) <-[l:log {endpoint: $endpoint, request_method: $request_method, request_body: $request_body}]- (user)
            RETURN l
            """
    result = run_query(query, username=log.username, endpoint=log.endpoint, request_method=log.request_method, request_body=log.request_body, node_id=log.node_elementid)
    return result
