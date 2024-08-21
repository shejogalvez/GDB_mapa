import pandas as pd
import os

WB_PATH = "2024 Muestra inventario colecciones MAPA (1).xlsx"

dataframe = pd.read_excel(WB_PATH)
dataframe = dataframe.reset_index()

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
    "peso_grs", 
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
def count_blank_values(row) -> int:
    return row.isna().sum() + (row == '').sum()

def get_row_piece_id(row) -> str:
    return f'P{row["numero_de_inventario"]}'

def get_row_component_id(row) -> str:
    return f'C{row["numero_de_inventario"]}{row["letra"] if not pd.isna(row["letra"]) else "a"}'

def get_attributes(row, atributes_columns: list[str], replace_dict: dict = None) -> str:
    result = ""
    for att in atributes_columns:
        element = row[att]
        if pd.isna(element):
            continue
        if isinstance(element, str):
            for old, new in replace_dict.items():
                element = element.replace(old, new)
            result += f' {att}:"{element}"'
        else:
            result += f' {att}:{element}'
    return result

pg_query = ""
pg_edges = ""


piezas_df = dataframe

# Sort the DataFrame by the ID column and then by the count of blank values
piezas_df['blank_count'] = piezas_df.apply(count_blank_values, axis=1)
piezas_df = piezas_df.sort_values(by=['numero_de_inventario', 'blank_count'])

# Drop duplicates, keeping the row with the least number of blank columns
drop_duplicate_piezas_df = piezas_df.drop_duplicates(subset='numero_de_inventario', keep='first').drop(columns='blank_count')


# TODO: Cambiar en mapa conceptual los campos de funcion, tipologia, iconografía, bibliografia(?), 
for index, line in drop_duplicate_piezas_df.iterrows() :
    id = get_row_piece_id(line)
    attributes = get_attributes(line, ATRIBUTOS_PIEZAS, {'\n': '', '"': "'"})
    piece_node_line = f'{id} :pieza {attributes}\n'
    pg_query += piece_node_line

for index, line in dataframe.iterrows() :
    # create componentes nodes
    id = get_row_component_id(line)
    attributes = get_attributes(line, ATRIBUTOS_COMPONENTES, {'\n': '', '"': "'"})
    comp_node_line = f'{id} :componente {attributes}\n'
    pg_query += comp_node_line

    pg_edges += f'{get_row_piece_id(line)}->{id} :compuesto_por\n'

# extract distinct values from column pais
pais_col_df = dataframe[COL_PAIS].drop_duplicates().dropna()
pais_name_id = {name: f"pa{index+1}" for index, name in enumerate(pais_col_df)}
for name, id in pais_name_id.items():
    pg_query += f'{id} :pais name:"{name}"\n'

# extract distinct values from column localidad
loc_col_df = dataframe[COL_LOCALIDAD].drop_duplicates().dropna()
loc_name_id = {name: f"loc{index+1}" for index, name in enumerate(loc_col_df)}
for name, id in loc_name_id.items():
    pg_query += f'{id} :localiudad name:"{name}"\n'


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
            c_id = f"B{len(caja_name_id) + 1}"
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


# parse relations between ubicacion nodes
for contenedor, contenido in ubicacion_dict.items() :
    for elemento in contenido: 
        pg_edges += f"{contenedor}->{elemento} :contiene_ubicacion\n"

# parse relations between ubicacion and components
for index, line in dataframe.iterrows() :
    # obtain id
    id = get_row_component_id(line)
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

# parse relations between pais and piezas
for index, line in drop_duplicate_piezas_df.iterrows() :
    # create pieza nodes
    id = f'P{line["numero_de_inventario"]}'
    if not pd.isna(line[COL_PAIS]):
        id2 = pais_name_id[line[COL_PAIS]]
    pg_edges += f"{id}->{id2} :de_pais\n"

# parse relations between loc and piezas
for index, line in drop_duplicate_piezas_df.iterrows() :
    # create pieza nodes
    id = f'P{line["numero_de_inventario"]}'
    if not pd.isna(line[COL_LOCALIDAD]):
        id2 = loc_name_id[line[COL_LOCALIDAD]]
    pg_edges += f"{id}->{id2} :de_localidad\n"


# Detrminar forma de cada pieza y linkear

ATRIBUTOS_FORMAS = [
    "alto_cm",
    "ancho_cm",
    "profundidad_cm",
    "diametro_cm"
]
for index, row in dataframe.iterrows():
    alto =     ATRIBUTOS_FORMAS[0]
    diametro = ATRIBUTOS_FORMAS[3]
    if not pd.isna(row[diametro]):
        d_id = f"D{len(deposito_name_id) + 1}"
        ubicacion_dict[d_id] = set()
        deposito_name_id[deposito] = d_id
        if not pd.isna(row[alto]):
            forma = "cilindro"
        else:
            forma = "esfera"
    else:
        blanks = count_blank_values(row[ATRIBUTOS_FORMAS])
        # print(f"{blanks=}\n", row[ATRIBUTOS_FORMAS])
        match blanks:
            case 1:
                forma = "prisma"
            case 2:
                forma = "plano"
            case 3:
                forma = "cuerda"
            case _:
                continue
    atributos = get_attributes(row, ATRIBUTOS_FORMAS)
    self_id = f"F{index}"
    pg_query += f"{self_id} :forma :{forma} {atributos}\n"
    pg_edges += f"{get_row_component_id(row)}->{self_id} :tiene_forma\n"
pg_query += pg_edges

# Open the file in write mode ('w') and write the string to it
with open(os.path.join("C:/Users/shejo/Documents/GitHub/MillenniumDB/data", "MAPA-DB.txt"), "w", encoding="utf-8") as file:
    file.write(pg_query)
with open(os.path.join("MAPADB.txt"), "w", encoding="utf-8") as file:
    file.write(pg_query)

print("File created successfully!")

