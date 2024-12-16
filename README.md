# GDB_MAPA
 Trabajo de titulo

## Requisitos

- Docker
- Python + pandas

### Librerías y Frameworks

Frontend:

- [Vue](https://vuejs.org/)
- [Vue-Router](https://router.vuejs.org/)
- [axios](https://axios-http.com/docs/intro)

Backend:

- [FastAPI](https://fastapi.tiangolo.com/)
- [Neo4j python driver](https://neo4j.com/docs/api/python-driver/current/api.html#driver)
- [python-jose](https://python-jose.readthedocs.io/en/latest/)
- [pytest](https://docs.pytest.org/)

## Poblar la BDD

se debe ubicar en la carpeta base del proyecto GDB_MAPA, tener listo el archivo excel que se quiere utilizar y correr el comando
`python excel_to_neo4j_csv.py {ruta_del_archvo_xlsx} ; docker exec backend python db.py` 
python excel_to_neo4j_csv.py "2024 Inventario Colecciones MAPA-PCMAPA (1).xlsx" ; docker exec backend python db.py

## Correr la aplicación

Para correr la aplicación primero se debe realizar un build de los containers de Docker. Para ello se debe ejecutar el comando `docker-compose up` en la misma carpeta que está el archivo `docker-compose.yml` para buildear y correr la aplicación.

Es necesario tener un archivo `.env` que debe tener el formato (Las credenciales de NEO4J_AUTH, ADMIN_USER y ADMIN_PASSWORD pueden ser cualquiera al momento de inicializar la db, pero estos se mantienen una vez inicializada la aplicación):
```
NEO4J_AUTH="{user}/{password}"
dbms.security.procedures.unrestricted=apoc.*
apoc.import.file.enabled=true
dbms.security.allow_csv_import_from_file_urls=true

ADMIN_USER="{user}"
ADMIN_PASSWORD="{password}"

API_SECRET= "{string}"
UPLOAD_PATH="{path}"
```

## Testing
Backend: 

Se pueden correr los tests hechos corriendo el comando ``pytest`` desde la terminal del contenedor de docker para backend. Actualmente
no existe una bd aparte para testeo por lo correr los tests puede generar cambios en la base de datos principal