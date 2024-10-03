import pandas as pd
import os
from backend.db import db

WB_PATH = "2024 Inventario Colecciones MAPA-PCMAPA (1).xlsx"

dataframe = pd.read_excel(WB_PATH)
dataframe = dataframe.reset_index()
# cleans spaces in string fields
dataframe = dataframe.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

COL_PAIS      = "pais"
COL_LOCALIDAD = "localidad"
COL_CULTURA   = "filiacion_cultural"
COL_DEPOSITO  = "deposito"
COL_ESTANTE   = "estante"
COL_CAJA      = "caja_actual"
COL_EXPO   = "exposiciones"


ATRIBUTOS_COMPONENTES = [
    "nombre_comun", 
    "nombre_especifico",
    "materialidad", 
    "peso_(gr)", 
    "tecnica",
    "marcas_o_inscripciones",
    "descripcion_fisica",
    "tipologia",
    "funcion",
    "iconografia",
    "estado_de_conservacion"
]

ATRIBUTOS_PIEZAS = [
    #"numero_de_inventario", #ID
    "numero_de registro_anterior",
    "coleccion",
    "clasificacion",
    "conjunto",
    "autor",
    "fecha_de_creacion",
    "contexto_historico",
    "notas_investigacion",
    "bibliografia",
    "avaluo",
    "procedencia",
    "donante",
    "fecha_ingreso"
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

def dataframe_to_csv(df : pd.DataFrame, filename) -> None:
    df.to_csv(f"neo4j/import/{filename}", index=False)

def column_to_name_id_dict(df: pd.DataFrame, column_name: str, prefix="A"):
    column_data = df[column_name].drop_duplicates().dropna()
    return {name: f"{prefix}{index+1}" for index, name in enumerate(column_data)}


def column_to_dataframe(df: pd.DataFrame, column_name, prefix="A") -> pd.DataFrame:
    data = {
        "id" : [f"{prefix}{index+1}" for _ in df[column_name].dropna()],
        "name" : list(df[column_name].dropna())
    }
    return pd.DataFrame(data)

def insert_id_column_to_df(df: pd.DataFrame, column_name: str, name_id_dict: dict, column_id_name="id", loc = 0) -> None:
    id_data = [None if pd.isna(x) else name_id_dict[x] for x in df[column_name]]
    df.insert(loc, column_id_name, id_data)

def extract_name_id_from_df(df: pd.DataFrame, column_name, column_id_name) -> pd.DataFrame:
    return df[[column_name, column_id_name]]

def multi(df: pd.DataFrame, column_name, prefix):
    name_id_dict = column_to_name_id_dict(df, column_name, prefix)

    column_id_name = f"{column_name}_id"
    insert_id_column_to_df(df, column_name, name_id_dict, column_id_name)
    result_df = df[[column_name, column_id_name]].drop_duplicates().dropna()
    dataframe_to_csv(result_df, f"{column_name}.csv")

def add_reference_and_create_table(df: pd.DataFrame, column_name, name_id_dict):
    column_id_name = f"{column_name}_id"
    insert_id_column_to_df(df, column_name, name_id_dict, column_id_name)
    result_df = df[[column_name, column_id_name]].drop_duplicates()
    dataframe_to_csv(result_df, f"{column_name}.csv")

# Initialize an empty dictionary to store ids where differences are found per column
different_values_ids = {col: [] for col in ATRIBUTOS_PIEZAS}

# Group by 'id' column
grouped = dataframe.groupby('numero_de_inventario')

# Iterate through each group
for group_id, group in grouped:
    for col in ATRIBUTOS_PIEZAS:
        # Check if the values in the current column vary within the group
        if group[col].nunique(True) > 1:
            # If they do, add the id to the corresponding list for that column
            different_values_ids[col].append(group_id)

print(different_values_ids)

piezas_df = dataframe

# Sort the DataFrame by the ID column and then by the count of blank values
piezas_df['blank_count'] = piezas_df.apply(count_blank_values, axis=1)
piezas_df = piezas_df.sort_values(by=['numero_de_inventario', 'blank_count'])

# Drop duplicates, keeping the row with the least number of blank columns
drop_duplicate_piezas_df = piezas_df.drop_duplicates(subset='numero_de_inventario', keep='first').drop(columns='blank_count')

# add id to single components
component_id_column = [get_row_component_id(row) for _, row in dataframe.iterrows()]
dataframe.insert(1, "component_id", component_id_column)


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
ubicacion_df = pd.concat([
    pd.DataFrame(list(deposito_name_id.items()), columns=['value', 'id']).assign(labels='ubicacion,deposito'),
    pd.DataFrame(list(estante_name_id.items()), columns=['value', 'id']).assign(labels='ubicacion,estante'),
    pd.DataFrame(list(caja_name_id.items()), columns=['value', 'id']).assign(labels='ubicacion,caja')
])
dataframe_to_csv(ubicacion_df, 'ubicaciones.csv')
# dataframe_to_csv(pd.DataFrame(list(deposito_name_id.items()), columns=['id', 'value']), "depositos.csv")
# dataframe_to_csv(pd.DataFrame(list(estante_name_id.items()), columns=['id', 'value']) , "estantes.csv")
# dataframe_to_csv(pd.DataFrame(list(caja_name_id.items()), columns=['id', 'value'])    , "cajas.csv")

# parse relations between ubicacion nodes
contenedor_list = []
for contenedor, contenido in ubicacion_dict.items():
    for elemento in contenido: 
        contenedor_list.append((contenedor, elemento))
dataframe_to_csv(pd.DataFrame(list(contenedor_list), columns=['id_contenedor', 'id_contenido']), "ubicaciones_rel.csv")

# parse relations between ubicacion and components
componenteId_ubicacion = []
for index, line in dataframe.iterrows():
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
    componenteId_ubicacion.append((id, ubicacion))
dataframe_to_csv(pd.DataFrame(list(componenteId_ubicacion), columns=['id_componente', 'id_ubicacion']), "ubicacion_objetos.csv")


# Detrminar forma de cada pieza y linkear

ATRIBUTOS_FORMAS = [
    "alto_o_largo_(cm)",
    "ancho_(cm)",
    "profundidad_(cm)",
    "diametro_(cm)",
    'espesor_(mm)'
]
formas_propiedades = []
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
    atributos = list(row[ATRIBUTOS_FORMAS])
    self_id = f"F{index}"
    atributos.extend([self_id, get_row_component_id(row), f"forma,{forma}"])
    formas_propiedades.append(atributos)

# export formas info
dataframe_to_csv(pd.DataFrame(list(formas_propiedades), 
                                columns=ATRIBUTOS_FORMAS + ['id', 'id_componente','labels']), 
                                f"forma.csv"
                            )
multi(drop_duplicate_piezas_df, COL_PAIS, "PA")
multi(drop_duplicate_piezas_df, COL_LOCALIDAD, "LOC")
multi(drop_duplicate_piezas_df, COL_CULTURA, "CUL")
dataframe_to_csv(drop_duplicate_piezas_df, "piezas.csv")

dataframe.drop(columns=dataframe.columns[0], axis=1, inplace=True)
dataframe_to_csv(dataframe, "all.csv")


print("Files created successfully!")


with open("import.cypher") as file:
    queries = file.read().split(";\n")
    for query in queries:
        db.run_query(query)

print("data imported to neo4j")