import json

CREATE_PIECE_BODY = {
    "properties": {
      "coleccion": "string",
      "numero_de_registro_anterior": "string"
    },
    "connected_nodes": [
      {
        "node_id": "Chile",
        "properties": {
        },
        "relation_label": "de_pais",
        "node_label": "pais",
        "id_key": "name",
      },
      {
        "node_id": "Mapuche",
        "properties": {
        },
        "relation_label": "de_cultura",
        "node_label": "cultura",
        "id_key": "name",
      }
    ],
    "id": "12345",
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
            "properties": {
            },
            "relation_label": "ubicacion_componente",
            "node_label": "ubicacion",
            "id_key": "name",
          },
        ]
      }
    ]
  }
CREATE_PIECE_FORM = { 
  "node_create": json.dumps(CREATE_PIECE_BODY)
}

CREATE_COMPONENT_BODY = {
  "components": [
    {
      "properties": {
        "funcion": "Simbólica-utilitaria",
        "nombre_comun": "Alfiler",
        "nombre_especifico": "Ketawue",
        "alto": "7"
      },
      "connected_nodes": [
          ""
      ]
    }
  ]
}
CREATE_COMPONENT_BODY

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