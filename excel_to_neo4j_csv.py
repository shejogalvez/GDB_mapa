import pandas as pd
import os
import sys
from pydantic import BaseModel, Field
from uuid import UUID, uuid4

# Set up the connection details
uri = f"bolt://{ os.getenv("NEO4J_HOSTNAME", "localhost") }:7687"  # Bolt URI of your Neo4j server
 
username, password = os.getenv("NEO4J_AUTH").split('/')  # Your Neo4j username

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
    "materialidad", 
    "peso_(gr)", 
    "tecnica",
    "marcas_o_inscripciones",
    "descripcion_fisica",
    'descripcion_col',
    'descripcion_cr',
    "tipologia",
    "funcion",
    "iconografia",
    "estado_genral_de_conservacion",
    'responsable_coleccion',
    'fecha_ultima_modificacion'
]

ATRIBUTOS_PIEZAS = [
    #"numero_de_inventario", #ID
    "numero_de registro_anterior",
    "coleccion",
    "SURDOC",
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
        id: UUID = Field(default_factory=uuid4)
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
            if col_val not in current_node.children:
                new_ubicacion = Ubicacion(label=col_name, name=str(col_val))
                current_node.children[new_ubicacion.name] = new_ubicacion
            else:
                new_ubicacion = current_node.children[col_val]
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
    print(args)
    if len(args) < 2:
        print("ingresar ruta de archivo excel a cargar")
        exit(-1)
    main(WB_PATH=args[1])