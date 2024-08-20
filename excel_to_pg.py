import pandas as pd
import math
import os

WB_PATH = "2024 Muestra inventario colecciones MAPA.xlsx"

dataframe = pd.read_excel(WB_PATH)
dataframe = dataframe.reset_index()

COLS = [
    "numero_de_inventario",
    "letra",
    "ubicacion ",
    "numero_de_registro_anterior",
    "SURDOC",
    "deposito",
    "estante",
    "caja_anterior",
    "caja_actual",
    "coleccion",
    "clasificacion",
    "conjunto",
    "nombre_comun",
    "titulo_o_nombre_atribuido",
    "autor",
    "filiacion_cultural",
    "pais",
    "localidad",
    "tipologia",
    "fecha_de_creacion",
    "descripcion_fisica",
    "marcas_o_inscripciones",
    "alto_(cm)",
    "ancho_(cm)",
    "profundidad_(cm)",
    "diametro_(cm)",
    "peso_(grs)",
    "tecnica",
    "materialidad",
    "funcion",
    "contexto_historico",
    "bibliografia",
    "iconografia",
    "notas",
    "exposiciones",
    "responsable",
    "fecha_ultima_modificacion",
    "avaluo",
    "tipo",
    "procedencia",
    "fecha",
    "estado_de_conservacion",
    "intervenciones",
    "Embalaje"
]

COL_PAIS = "pais"
COL_LOCALIDAD = "localidad"
COL_DEPOSITO = "deposito"
COL_ESTANTE     = "estante"
COL_CAJA    = "caja_actual"

ATRIBUTOS_UBICACION = [
    "deposito",
    "estante",
    "caja_anterior",
    "caja_actual"
]

ATRIBUTOS_COMPONENTES = [
    "nombre_comun", 
    "materialidad", 
    #"peso_(grs)", 
    "tecnica",
    "marcas_o_inscripciones",
    "descripcion_fisica",
    "tipologia",
    "funcion",
    "iconografia",
    "bibliografia",
    "estado_de_conservacion"
]

ATRIBUTOS_PIEZAS = [
    #"numero_de_inventario", #ID
    "numero_de_registro_anterior",
    "coleccion",
    "clasificacion",
    "conjunto",
    "titulo_o_nombre_atribuido",
    "autor",
    "fecha_de_creacion",
    "contexto_historico",
    "notas",
    "avaluo",
    "tipo",
    "procedencia",
    "fecha",
    "Embalaje"
]


# Function to count blank values (NaN or empty string) in a row
def count_blank_values(row):
    return row.isna().sum() + (row == '').sum()

def dict_to_pg_query(objects, *tags):
    pg_query = ""


pg_query = ""

pg_edges = ""

piezas_df = dataframe[['numero_de_inventario'] + ATRIBUTOS_PIEZAS]

# Sort the DataFrame by the ID column and then by the count of blank values
piezas_df['blank_count'] = piezas_df.apply(count_blank_values, axis=1)
piezas_df = piezas_df.sort_values(by=['numero_de_inventario', 'blank_count'])

# Drop duplicates, keeping the row with the least number of blank columns
drop_duplicate_piezas_df = piezas_df.drop_duplicates(subset='numero_de_inventario', keep='first').drop(columns='blank_count')

# TODO: Filtrar piezas repetidas
# TODO: Cambiar en mapa conceptual los campos de funcion, tipologia, iconografía, bibliografia(?), 
for index, line in drop_duplicate_piezas_df.iterrows() :
    # create pieza nodes
    # print(line)
    # for att in atributos_piezas:
    #     print(type(line[att]), line[att], line[att] == 'NaN')
    piece_node_line = f'P{line["numero_de_inventario"]} :pieza {" ".join([f"{att}:\"{str(line[att]).replace('\n', '').replace('"', "'").strip()}\"" for att in ATRIBUTOS_PIEZAS if not pd.isna(line[att])]) }\n'
    pg_query += piece_node_line

for index, line in dataframe.iterrows() :
    # create componentes nodes
    id = f'C{line["numero_de_inventario"]}{line["letra"] if not pd.isna(line["letra"]) else "a"}'
    comp_node_line = f'{id} :componente {" ".join([f"{att}:\"{str(line[att]).replace('\n', ' ').replace('"', "'").strip()}\"" for att in ATRIBUTOS_COMPONENTES if not pd.isna(line[att])]) }\n'
    pg_query += comp_node_line

    pg_edges += f'P{line["numero_de_inventario"]}->{id} :compuesto_por\n'

# extract distinct values from column pais
pais_col_df = dataframe[COL_PAIS].drop_duplicates().dropna()
pais_name_id = {name: f"pa{index}" for index, name in enumerate(pais_col_df)}
for name, id in pais_name_id.items():
    pg_query += f"{id} :pais name:{name}\n"
# pg_query += " :pais\n".join(pais for pais in pais_col_df if pd.notna(pais))
# pg_query += " :pais\n"

# extract distinct values from column localidad
loc_col_df = dataframe[COL_LOCALIDAD].drop_duplicates().dropna()
loc_name_id = {name: f"loc{index}" for index, name in enumerate(loc_col_df)}
for name, id in loc_name_id.items():
    pg_query += f"{id} :localiudad name:{name}\n"
# pg_query += " :localidad\n".join(loc for loc in loc_col_df if pd.notna(loc))
# pg_query += " :localidad\n"


deposito_name_id = dict()
estante_name_id = dict()
caja_name_id = dict()
ubicacion_dict = dict()
for index, row in dataframe.iterrows():
    deposito = row[COL_DEPOSITO]
    if not pd.isna(deposito) and deposito not in deposito_name_id:
        d_id = f"D{len(deposito_name_id) + 1}"
        ubicacion_dict[d_id] = set()
        deposito_name_id[deposito] = d_id

    estante = row[COL_ESTANTE]
    if not pd.isna(estante):
        if estante not in estante_name_id:
            e_id = f"E{len(estante_name_id) + 1}"
            ubicacion_dict[e_id] = set()
            estante_name_id[estante] = e_id
        if deposito in deposito_name_id:
            ubicacion_dict[deposito_name_id[deposito]].add(estante_name_id[estante])

    caja = row[COL_CAJA]
    if not pd.isna(caja):
        if caja not in caja_name_id:
            c_id = f"C{len(caja_name_id) + 1}"
            caja_name_id[caja] = c_id
        if estante in estante_name_id:
            ubicacion_dict[estante_name_id[estante]].add(caja_name_id[caja])
        elif deposito in deposito_name_id:
            ubicacion_dict[deposito_name_id[deposito]].add(caja_name_id[caja])

for name, id in deposito_name_id.items():
    pg_query += f"{id} :deposito :ubicacion name:\"{name}\"\n"
for name, id in estante_name_id.items():
    pg_query += f"{id} :estante :ubicacion name:\"{name}\"\n"
for name, id in caja_name_id.items():
    pg_query += f"{id} :caja :ubicacion name:\"{name}\"\n"


# pg_query += " :deposito :ubicacion\n".join(str(x) for x in deposito_name_id if pd.notna(x))
# pg_query += " :deposito :ubicacion\n"
# pg_query += " :estante :ubicacion\n".join(str(x) for x in estante_name_id if pd.notna(x))
# pg_query += " :estante :ubicacion\n"
# pg_query += " :caja :ubicacion\n".join(str(x) for x in caja_name_id if pd.notna(x))
# pg_query += " :caja :ubicacion\n"


# parse relations between ubicacion nodes
for contenedor, contenido in ubicacion_dict.items() :
    for elemento in contenido: 
        pg_edges += f"{contenedor}->{elemento} :contiene_ubicacion\n"

# parse relations between ubicacion and components
for index, line in dataframe.iterrows() :
    # obtain id
    id = f'C{line["numero_de_inventario"]}{line["letra"] if not pd.isna(line["letra"]) else "a"}'
    # obtain leaf node from ubicacion
    if not pd.isna(line[COL_CAJA]):
        ubicacion = caja_name_id[line[COL_CAJA]]
    elif not pd.isna(line[COL_ESTANTE]):
        ubicacion = estante_name_id[line[COL_ESTANTE]]
    elif not pd.isna(line[COL_DEPOSITO]):
        ubicacion = deposito_name_id[line[COL_DEPOSITO]]
    else:
        continue
    pg_edges += f"{id}->{ubicacion} :ubicado_en\n"

pg_query += pg_edges

# Open the file in write mode ('w') and write the string to it
with open(os.path.join("C:/Users/shejo/Documents/GitHub/MillenniumDB/data", "MAPA-DB.txt"), "w", encoding="utf-8") as file:
    file.write(pg_query)

print("File created successfully!")

