import json

CREATE_PIECE_BODY = {
  "properties": {
    "id": "12345",
    "coleccion": "string",
    "numero_de_registro_anterior": "string",
    "fecha_de_creacion": "siglo XX",
  },
  "connected_nodes": [
    {
      "node_id": "Chile",
      "relation_label": "de_pais",
      "node_label": "pais",
      "id_key": "name",
    },
    {
      "node_id": "Mapuche",
      "relation_label": "de_cultura",
      "node_label": "cultura",
      "id_key": "name",
    }
  ],
  "components": [
    {
      "properties": {
        "funcion": "Simbólica-utilitaria",
        "nombre_comun": "Alfiler",
        "nombre_especifico": "Ketawue",
        "alto": "7"
      },
      "connected_nodes": [
        {
          "node_id": "Caja Fuerte",
          "node_label": "ubicacion",
          "id_key": "name",
        },
      ]
    }
  ]
}
  
CREATE_PIECE_FORM = { 
  "node_create": json.dumps(CREATE_PIECE_BODY),
}

CREATE_COMPONENT_BODY = {
    "properties": {
      "funcion": "Simbólica-utilitaria",
      "nombre_comun": "Alfiler",
      "nombre_especifico": "Ketawue",
      "alto": "7"
    },
    "connected_nodes": [
    ]
}

CREATE_PIECE_BODY_2 = {
  "properties": {
    "id": "12346",
    "conjunto": "Bola de rompecabezas con pilar",
    "coleccion": "Colección China",
    "fecha_de_creacion": "ca. 1953",
    "notas_investigacion": "Se puede atribuir el ingreso de esta pieza a la colección por medio de la donación realizada por la delegación china encabezada por Li I Mang en 1953 durante el Congreso Continental de la Cultura debido a su precencia en el listado de objetos de la exposición de 1955.",
    "procedencia": "Donación",
    "dondante": "Li I  Mang, representante de la delegación china dona una colección al MAPA luego del Congreso Continental de la Cultura, donde se incluye esta pieza",
    "fecha_ingreso": "1953",
  },
  "connected_nodes": [
    {
      "node_id": "China",
      "node_label": "pais",
      "id_key": "name",
    },
    {
      "node_id": "Guangzhou; Provincia de Guangdong",
      "node_label": "localidad",
      "id_key": "name",
    }
  ],
  "components": [
    {
      "properties": {
        "id": "C12346a",
        "funcion": "Simbólica-utilitaria",
        "nombre_comun": "Bola de rompecabezas",
        "nombre_especifico": "El árbol de la vida",
        "funcion": "Ornamental",
        "tipologia": "Asta",
      },
      "connected_nodes": [
        {
          "node_label": "forma",
          "method": "MERGE",
          "properties": {
              "profundidad": 1,
              "diametro": 1,
              "peso": 1
          }
        },
      ]
    },
    {
      "properties": {
        "id": "C12346b",
        "funcion": "Simbólica-utilitaria",
        "nombre_comun": "Parte del pilar",
        "nombre_especifico": "El árbol de la vida",
        "funcion": "Ornamental",
        "tipologia": "Asta",
      }
    },
    {
      "properties": {
        "id": "C12346c",
        "funcion": "Simbólica-utilitaria",
        "nombre_comun": "Parte del pilar",
        "nombre_especifico": "El árbol de la vida",
        "funcion": "Ornamental",
        "tipologia": "Asta",
      }
    },
  ]
}

CREATE_COMPONENT_FORM = {
    "node_create": json.dumps(CREATE_COMPONENT_BODY),
    "piece_id": "12345"
}

LOGIN_ADMIN = {
    "username": "admin",
    "password": "admin"
}
CREATE_USER = {
    "username": "test_reader",
    "password": "testpwd123",
    "role": "reader",
}
CREATE_USER_2 = {
    "username": "test_writer",
    "password": "testpwd123",
    "role": "writer",
}
LOGIN_USER = {
    "username": "test_reader",
    "password": "testpwd123"
}
WRONG_USER = {
    "username": "test_reader",
    "password": "wrong_password"
}

FILTERS_1 = {
  "pieza": [
    {
      "key": "string",
      "operation": "<",
      "val": "string"
    },
    {
      "key": "string",
      "operation": ">",
      "val": "string"
    }
  ],
  "pais": [
    {
      "key": "string",
      "operation": "=",
      "val": "string"
    }
  ]
}

FILTERS_0 = {
    "pieza": [
      {
        "key": "id",
        "operation": "=",
        "val": "12345"
      }
    ]
}