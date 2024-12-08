import pandas as pd
import os
import sys
from pydantic import BaseModel, Field
from uuid import UUID, uuid4

from datetime import datetime

# Nombres de columnas excel que contine
COL_PAIS      = "pais"
COL_LOCALIDAD = "localidad"
COL_CULTURA   = "filiacion_cultural"
COL_UBICACION = "ubicacion"
COL_DEPOSITO  = "deposito"
COL_ESTANTE   = "estante"
COL_CAJA      = "caja_actual"
COL_EXPO      = "exposiciones"

ATRIBUTOS_COMPONENTES = [
    "nombre_comun", 
    "nombre_especifico",
    "descripcion_fisica",
    'descripcion_col',
    'descripcion_cr',
    "tipologia",
    "funcion",
    "materialidad", 
    "tecnica",
    "peso_(gr)", 
    "marcas_o_inscripciones",
    "estado_genral_de_conservacion",
    'responsable_coleccion',
    'fecha_ultima_modificacion'
]

ATRIBUTOS_PIEZAS = [
    #"numero_de_inventario", #ID
    "conjunto",
    "coleccion",
    "SURDOC",
    "clasificacion",
    "avaluo",
    "numero_de registro_anterior",
    "contexto_historico",
    "iconografia",
    "notas_investigacion",
    "fecha_de_creacion",
    "autor",
    "bibliografia",
    "procedencia",
    "donante",
    "fecha_ingreso"
]

total = ["numero_de_inventario","letra","Revisión","numero_de registro_anterior","SURDOC","ubicacion","deposito","estante","caja_anterior","caja_actual","tipologia","coleccion","clasificacion","conjunto","nombre_comun","nombre_especifico","autor","filiacion_cultural","pais","localidad","fecha_de_creacion","descripcion_col","marcas_o_inscripciones","tecnica","materialidad","descripcion_cr","alto_o_largo_(cm)","ancho_(cm)","profundidad_(cm)","diametro_(cm)","espesor_(mm)","peso_(gr)","funcion","contexto_historico","bibliografia","iconografia","notas_investigacion","estado_genral_de_conservacion","responsable_conservacion","fecha_actualizacion_cr","comentarios_cr","exposiciones","avaluo","procedencia","donante","fecha_ingreso","responsable_coleccion","fecha_ultima_modificacion"]


DATE_COLUMNS = ["fecha_ultima_modificacion", "fecha_ingreso"]

def transform_date(date_obj: str):
    admited_date_formats = ["%Y-%m-%d %H:%M:%S", "%Y", "ca. %Y", "ca.%Y","c.%Y", "%b. %Y","%d-%m-%Y", "00-%m-%Y", "00-00-%Y",
                            "%d/%m/%Y","%Y/%m/%d", "%Y-%m-%d", "%Y-%m-00", "%Y-00-00"]
    # remain null values unchanged
    if (pd.isna(date_obj)): return date_obj

    # pass number values to string and remove spaces
    date_obj = str(date_obj).strip()
    
    # Parse the input string into a datetime object (local timezone assumed)
    for format in admited_date_formats:
        try: 
            date_obj = datetime.strptime(date_obj, format)
            break
        except ValueError as e:
            continue
    
    if type(date_obj) != datetime:
        if (type(date_obj) == str):
            print(date_obj)
            pass
        return date_obj

    # Get the current local timezone
    local_tz = datetime.now().astimezone().tzinfo

    # Localize the datetime object to the local timezone
    localized_date = date_obj.replace(tzinfo=local_tz)

    # Format the datetime object to the desired output format
    formatted_date = localized_date.strftime("%Y-%m-%d")  
    
    # Append the "Z" to indicate UTC offset
    return formatted_date

# untracked = [x for x in total if x not in ATRIBUTOS_COMPONENTES + ATRIBUTOS_PIEZAS]
# print(untracked)
# dataframe = pd.read_excel("2024 Inventario Colecciones MAPA-PCMAPA (1).xlsx")
# dataframe = dataframe.reset_index()
# # cleans spaces in string fields
# dataframe = dataframe.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

# # Initialize an empty dictionary to store ids where differences are found per column
# different_values_ids = {col: [] for col in ATRIBUTOS_PIEZAS}

# # Group by 'id' column
# grouped = dataframe.groupby('numero_de_inventario')

# # Iterate through each group
# for group_id, group in grouped:
#     for col in ATRIBUTOS_PIEZAS:
#         # Check if the values in the current column vary within the group
#         if group[col].nunique(True) > 1:
#             # If they do, add the id to the corresponding list for that column
#             different_values_ids[col].append(group_id)

# print(different_values_ids)

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
    result_df = result_df[result_df[column_name] != ""]
    # print(result_df)
    dataframe_to_csv(result_df, f"{column_name}.csv")

def add_reference_and_create_table(df: pd.DataFrame, column_name, name_id_dict):
    column_id_name = f"{column_name}_id"
    insert_id_column_to_df(df, column_name, name_id_dict, column_id_name)
    result_df = df[[column_name, column_id_name]].drop_duplicates()
    dataframe_to_csv(result_df, f"{column_name}.csv")


def main(WB_PATH):
    dataframe = pd.read_excel(WB_PATH)
    dataframe = dataframe.reset_index()
    
    dataframe['fecha_ingreso_text'] = dataframe['fecha_ingreso']
    for column in DATE_COLUMNS:
        #dataframe[column] = pd.to_datetime(dataframe[column], errors='ignore')
        dataframe[column] = dataframe[column].apply(transform_date)
    #print(dataframe[DATE_COLUMNS])

    # cleans spaces in string fields
    dataframe = dataframe.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    piezas_df = dataframe

    # Sort the DataFrame by the ID column and then by the count of blank values
    piezas_df['blank_count'] = piezas_df.apply(count_blank_values, axis=1)
    piezas_df = piezas_df.sort_values(by=['numero_de_inventario', 'blank_count'])

    # Drop duplicates, keeping the row with the least number of blank columns
    drop_duplicate_piezas_df = piezas_df.drop_duplicates(subset='numero_de_inventario', keep='first').drop(columns='blank_count')

    # add id to single components
    component_id_column = [get_row_component_id(row) for _, row in dataframe.iterrows()]
    dataframe.insert(1, "component_id", component_id_column)
    duplicated_components_id = dataframe[dataframe[['component_id']].duplicated() == True]["component_id"]
    if (len(duplicated_components_id) > 0):
        print("Existen pares de componentes/letra repetidos, datos no se van a cargar correctamente\n", duplicated_components_id)

    
    # Estructura recursiva para ubicaciones
    class Ubicacion(BaseModel):
        label: str
        name: str
        id: UUID|str = Field(default_factory=uuid4)
        children: dict[str, 'Ubicacion'] = {}

    # lista principal de ubicaciones
    ubicacion_root: Ubicacion = Ubicacion(name="root", label="")
    
    # lista de columnas que hacen referencia a ubicaciones, ordenadas de más general a más particular
    nombres_columnas_ubicacion = [COL_UBICACION, COL_DEPOSITO, COL_ESTANTE, COL_CAJA]

    # lista donde se guardan conexiones entre ubicacion y componentes
    componenteId_ubicacion = []
    # 
    for index, row in dataframe.iterrows():
        # se inicia desde el nodo base*
        current_node = ubicacion_root
        new_ubicacion: Ubicacion = None
        # itera columnas que representan ubicaciones
        for col_name in nombres_columnas_ubicacion:
            col_val = row[col_name]
            if pd.isna(col_val): continue
            #print(f"{col_name}{index}: {col_val}")
            col_val = str(col_val)
            if col_val == "":
                continue
            ubicacion_token = col_val + col_name # token identifica hijos de un mismo nodo
            if ubicacion_token not in current_node.children:
                new_ubicacion = Ubicacion(label=col_name, name=col_val)
                current_node.children[ubicacion_token] = new_ubicacion
            else:
                new_ubicacion = current_node.children[ubicacion_token]
            current_node = new_ubicacion
        # componente se conecta a la ultima ubicación sobre la que se pasó/creó en el arbol 
        if new_ubicacion:
            #print(new_ubicacion)
            componenteId_ubicacion.append({'id_componente': row['component_id'], 'id_ubicacion': new_ubicacion.id})

    ubicacion_df_list = []
    ubicacion_connection_list = []
    def recursive_parse_tree(parent: Ubicacion) -> None:
        # se añade a lista para crear nodo ubicacion
        ubicacion_df_list.append({"name": parent.name, "label": parent.label, "id": parent.id})
        for key, node in parent.children.items():
            # se añade a lista para conectar {node} con {parent}
            ubicacion_connection_list.append({'id_contenedor': parent.id, 'id_contenido': node.id})
            recursive_parse_tree(node)
    recursive_parse_tree(ubicacion_root)

    dataframe_to_csv(pd.DataFrame(ubicacion_df_list), "ubicaciones.csv")
    dataframe_to_csv(pd.DataFrame(ubicacion_connection_list), "ubicaciones_rel.csv")
    dataframe_to_csv(pd.DataFrame(componenteId_ubicacion), "ubicacion_objetos.csv")


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
        atributos.extend([get_row_component_id(row), forma])
        formas_propiedades.append(atributos)

    minimal_distinct_expo: set[str] = set()
    dict_expo_pieza = dict()
    for _, row in dataframe.iterrows():
        row_exposicion = str(row[COL_EXPO])
        if row_exposicion == 'nan': continue
        if row_exposicion in minimal_distinct_expo:
            continue
        to_add = []
        to_delete = []
        for expo in minimal_distinct_expo:
            if expo in row_exposicion:
                to_delete.append(expo)
                to_add.append(row_exposicion)
                to_add.append(expo.replace(row_exposicion, ''))
        if len(to_add) > 0:
            for elem in to_delete:
                minimal_distinct_expo.remove(elem)
            for elem in to_add:
                minimal_distinct_expo.add(elem)
            continue
        minimal_distinct_expo.add(row_exposicion)

    #print(minimal_distinct_expo)
    for expo in minimal_distinct_expo:
        dict_expo_pieza[expo] = []
    for _, row in dataframe.iterrows():
        row_exposicion = str(row[COL_EXPO])
        for expo in minimal_distinct_expo:
            if expo in row_exposicion:
                dict_expo_pieza[expo].append(row['numero_de_inventario'])
    #print(dict_expo_pieza)

    # export formas info
    dataframe_to_csv(pd.DataFrame(list(formas_propiedades), 
                                    columns=ATRIBUTOS_FORMAS + ['id_componente','forma']), 
                                    f"forma.csv"
                                )
    multi(drop_duplicate_piezas_df, COL_PAIS, "PA")
    multi(drop_duplicate_piezas_df, COL_LOCALIDAD, "LOC")
    multi(drop_duplicate_piezas_df, COL_CULTURA, "CUL")
    dataframe_to_csv(drop_duplicate_piezas_df, "piezas.csv")

    dataframe.drop(columns=dataframe.columns[0], axis=1, inplace=True)
    dataframe_to_csv(dataframe, "all.csv")


    print("Files created successfully!")


    # with open("import.cypher") as file:
    #     queries = file.read().split(";\n")
    #     with GraphDatabase.driver(uri, auth=(username, password)) as driver:
    #         for query in queries:
    #                 _, summary, _ = driver.execute_query(query, database_="neo4j")
    #                 print(f"{summary.query} completed in {summary.result_available_after} ms")

    # print("data imported to neo4j")

if __name__ == "__main__":
    args = sys.argv
    # print(args)
    if len(args) < 2:
        print("ingresar ruta de archivo excel a cargar")
        exit(-1)
    main(WB_PATH=args[1])