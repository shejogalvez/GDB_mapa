from db import get_db_driver

queries = """
CREATE CONSTRAINT pieza_pk IF NOT EXISTS FOR (n:pieza) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT componente_pk IF NOT EXISTS FOR (n:componente) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT user_pk IF NOT EXISTS FOR (n:user) REQUIRE n.username IS UNIQUE;
CREATE CONSTRAINT pais_pk IF NOT EXISTS FOR (n:pais) REQUIRE n.name IS UNIQUE;
CREATE CONSTRAINT localidad_pk IF NOT EXISTS FOR (n:localidad) REQUIRE n.name IS UNIQUE;
CREATE CONSTRAINT cultura_pk IF NOT EXISTS FOR (n:cultura) REQUIRE n.name IS UNIQUE;

LOAD CSV WITH HEADERS FROM 'file:///pais.csv' AS row
MERGE (:pais {name: row.pais});

LOAD CSV WITH HEADERS FROM 'file:///localidad.csv' AS row
MERGE (:localidad {name: row.localidad});

LOAD CSV WITH HEADERS FROM 'file:///filiacion_cultural.csv' AS row
MERGE (:cultura {name: row.filiacion_cultural});

LOAD CSV WITH HEADERS FROM 'file:///piezas.csv' AS row
CREATE (n:pieza {id: row.numero_de_inventario})
SET n.numero_de_registro_anterior = row.`numero_de registro_anterior`,
    n.coleccion =                   row.coleccion,
    n.clasificacion =               row.clasificacion,
    n.conjunto =                    row.conjunto,
    n.autor =                       row.autor,
    n.fecha_de_creacion =           row.fecha_de_creacion,
    n.contexto_historico =          row.contexto_historico,
    n.notas_investigacion =         row.notas_investigacion,
    n.bibliografia =                row.bibliografia,
    n.avaluo =                      row.avaluo,
    n.procedencia =                 row.tipo,
    n.donante =                     row.procedencia,
    n.fecha_ingreso =               row.fecha_ingreso,
    n.fecha_ingreso_text =          row.fecha_ingreso_text
WITH n, row
MATCH (b:pais {name: row.pais})
CREATE (n)-[:de_pais ]->(b)
WITH n, row
MATCH (b:localidad {name: row.localidad})
CREATE (n)-[:de_localidad ]->(b)
WITH n, row
MATCH (b:cultura {name: row.filiacion_cultural})
CREATE (n)-[:de_cultura ]->(b);

LOAD CSV WITH HEADERS FROM 'file:///all.csv' AS row
CREATE (n :componente {id: row.component_id})
SET n.nombre_comun =           row.nombre_comun,
    n.nombre_especifico =      row.nombre_especifico,
    n.materialidad =           row.materialidad,
    n.peso_grs =               row.`peso_(gr)`,
    n.tecnica =                row.tecnica,
    n.marcas_o_inscripciones = row.marcas_o_inscripciones,
    n.descripcion_fisica =     row.descripcion_fisica,
    n.tipologia =              row.tipologia,
    n.funcion =                row.funcion,
    n.iconografia =            row.iconografia,
    n.estado_de_conservacion = row.estado_genral_de_conservacion,
    n.descripcion_col =        row.descripcion_col,
    n.descripcion_cr =         row.descripcion_cr,
    n.responsable_coleccion =  row.responsable_coleccion,
    n.fecha_ultima_modificacion = row.fecha_ultima_modificacion
WITH n, row
MATCH (pieza:pieza {id: row.numero_de_inventario})
CREATE (pieza)-[:compuesto_por ]->(n);
    
LOAD CSV WITH HEADERS FROM 'file:///forma.csv' AS row
MATCH (b:componente {id: row.id_componente})
MERGE (b)-[:tiene_forma]->(a:forma)
SET a.forma = row.forma,
    a.alto = toFloat(row.alto_cm),
    a.ancho = toFloat(row.ancho_cm),
    a.profundidad = toFloat(row.profundidad_cm),
    a.diametro = toFloat(row.diametro_cm);

LOAD CSV WITH HEADERS FROM 'file:///ubicaciones.csv' AS row
CREATE (:ubicacion {id: row.id, name: row.name, label: row.label});

LOAD CSV WITH HEADERS FROM 'file:///ubicacion_objetos.csv' AS row
MATCH (a:componente {id: row.id_componente}), (b:ubicacion {id: row.id_ubicacion})
CREATE (a)-[:ubicacion_componente ]->(b);

LOAD CSV WITH HEADERS FROM 'file:///ubicaciones_rel.csv' AS row
MATCH (a:ubicacion {id: row.id_contenedor}), (b:ubicacion {id: row.id_contenido})
CREATE (a)-[:ubicacion_contiene ]->(b);"""

queries = queries.split(";\n")

with get_db_driver() as driver:
    for query in queries:
            _, summary, _ = driver.execute_query(query, database_="neo4j")
            print(f"{summary.query} completed in {summary.result_available_after} ms")

print("data imported to neo4j")