# GDB_MAPA
 Trabajo de titulo

## Requisitos

- Docker

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

## Correr la aplicación

Para correr la aplicación primero se debe realizar un build de los containers de Docker. Para ello se debe ejecutar el comando `docker-compose up` en la misma carpeta que está el archivo `docker-compose.yml` para buildear y correr la aplicación.

Es necesario tener un archivo `.env` que debe tener el formato (Las credenciales de NEO4J_AUTH pueden ser cualquiera al momento de inicializar la db):
```
NEO4J_AUTH="{user}/{password}"
dbms.security.procedures.unrestricted=apoc.*
apoc.import.file.enabled=true
dbms.security.allow_csv_import_from_file_urls=true

API_SECRET= "{string}"
UPLOAD_PATH="{path}"
```

## Testing
Backend: 

Se pueden correr los tests hechos corriendo el comando ``pytest`` desde la terminal del contenedor de docker para backend. Actualmente
no existe una bd aparte para testeo por lo correr los tests puede generar cambios en la base de datos principal