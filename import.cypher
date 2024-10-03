CREATE CONSTRAINT pieza_pk IF NOT EXISTS FOR (n:piezas) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT pais_pk IF NOT EXISTS FOR (n:pais) REQUIRE n.name IS UNIQUE;
CREATE CONSTRAINT localidad_pk IF NOT EXISTS FOR (n:localidad) REQUIRE n.name IS UNIQUE;

LOAD CSV WITH HEADERS FROM 'file:///all.csv' AS row
MERGE (n :componente {id: row.component_id})
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
    n.estado_de_conservacion = row.estado_de_conservacion;
    
LOAD CSV WITH HEADERS FROM 'file:///forma.csv' AS row
WITH row, SPLIT(row.labels, ',') AS labeles
CALL {
    WITH row, labeles
    MERGE (a: forma {id: row.id})
    SET a.labels = labeles[1], a.alto = toFloat(row.alto_cm), a.ancho = toFloat(row.ancho_cm), a.profundidad = toFloat(row.profundidad_cm), a.diametro = toFloat(row.diametro_cm)
    RETURN a
}
WITH a, row
MATCH (b:componente {id: row.id_componente})
CREATE (a)-[:tiene_forma]->(b);

LOAD CSV WITH HEADERS FROM 'file:///pais.csv' AS row
CREATE (:pais {id: row.pais_id, name: row.pais});

LOAD CSV WITH HEADERS FROM 'file:///localidad.csv' AS row
MERGE (:localidad {name: row.localidad});

LOAD CSV WITH HEADERS FROM 'file:///filiacion_cultural.csv' AS row
CREATE (:cultura {name: row.filiacion_cultural});

LOAD CSV WITH HEADERS FROM 'file:///ubicaciones.csv' AS row
WITH row, SPLIT(row.labels, ',') AS labeles
CREATE (:ubicacion {id: row.id, name: row.value, label: labeles[1]});

LOAD CSV WITH HEADERS FROM 'file:///ubicacion_objetos.csv' AS row
MATCH (a:componente {id: row.id_componente}), (b:ubicacion {id: row.id_ubicacion})
CREATE (a)-[:ubicacion_componente ]->(b);

LOAD CSV WITH HEADERS FROM 'file:///ubicaciones_rel.csv' AS row
MATCH (a:ubicacion {id: row.id_contenedor}), (b:ubicacion {id: row.id_contenido})
CREATE (a)-[:ubicacion_contiene ]->(b);

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
    n.fecha_ingreso =               row.fecha;


LOAD CSV WITH HEADERS FROM 'file:///piezas.csv' AS row
MATCH (a:pieza {id: row.numero_de_inventario}), (b:pais {name: row.pais})
CREATE (a)-[:de_pais ]->(b);

LOAD CSV WITH HEADERS FROM 'file:///piezas.csv' AS row
MATCH (a:pieza {id: row.numero_de_inventario}), (b:localidad {name: row.localidad})
CREATE (a)-[:de_localidad ]->(b);

LOAD CSV WITH HEADERS FROM 'file:///piezas.csv' AS row
MATCH (a:pieza {id: row.numero_de_inventario}), (b:cultura {name: row.filiacion_cultural})
CREATE (a)-[:de_cultura ]->(b);
    

LOAD CSV WITH HEADERS FROM 'file:///all.csv' AS row
MATCH (a:pieza {id: row.numero_de_inventario}), (b:componente {id: row.component_id})
CREATE (a)-[:compuesto_por ]->(b);

LOAD CSV WITH HEADERS FROM 'file:///exposiciones.csv' AS row
CREATE (:exposicion {id: row.exposiciones_id, name: row.exposiciones});