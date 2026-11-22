# proyecto-blog-neo4j

Proyecto de blog que usa Neo4j para guardar datos como nodos y relaciones. Incluye operaciones CRUD para usuarios, etiquetas, artículos, categorías y comentarios.

## Estructura

| Archivo o carpeta | Responsabilidad |
| --- | --- |
| `app/config.py` | Carga los parámetros de conexión desde el entorno o el archivo local `.env`. |
| `app/database.py` | Comparte el controlador de Neo4j y devuelve los registros que generan las consultas. |
| `app/crud/user.py` | Crea, consulta, actualiza y borra usuarios por correo. |
| `app/crud/tags.py` | Crea, consulta, renombra y borra etiquetas por nombre. |
| `app/crud/articles.py` | Gestiona artículos por título y fecha. La fecha se recibe como `AAAA-MM-DD` y se guarda como `DATE` en Neo4j. |
| `app/crud/categories.py` | Gestiona categorías por nombre. |
| `app/crud/comments.py` | Gestiona comentarios por URL. |
| `app/main.py` y `app/ui/` | Punto de entrada e interfaz pendientes de implementación. |
| `cypher/` | Restricciones del grafo y archivos reservados para datos de prueba y consultas de ejemplo. |

## Configuración local

Instala el controlador de Neo4j y el lector de archivos `.env`.

```bash
python -m pip install -r requirements.txt
```

Copia `.env.example` a `.env` en la raíz del proyecto si aún no tienes un archivo local. Estas son las variables que lee `app/config.py`.

```dotenv
NEO4J_URI=neo4j+s://TU_INSTANCIA.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=
NEO4J_DATABASE=neo4j
```

Para Neo4j Aura, usa la URI y las credenciales de tu instancia. Si ejecutas Neo4j localmente, usa `bolt://localhost:7687`. `NEO4J_DATABASE` es opcional y su valor por defecto es `neo4j`.

Aplica las sentencias de `cypher/01_constraints.cypher` en la misma base antes de usar el CRUD. Las restricciones garantizan que los identificadores de cada tipo de nodo sean únicos.

## Cómo funciona el CRUD

Los módulos CRUD construyen consultas Cypher y pasan los valores por separado a `db.query()`. La conexión ejecuta la consulta en la base configurada y devuelve sus registros.

- Crear devuelve el nodo creado.
- Las etiquetas admiten una URL opcional. Al actualizar una etiqueta, omitir la URL conserva la existente.
- Listar devuelve una lista de nodos. Las etiquetas se ordenan por nombre.
- Buscar y actualizar devuelven el nodo encontrado o `None` si no existe.
- Borrar devuelve `True` si se eliminó el nodo y `False` si no existía. Neo4j rechaza el borrado de nodos que tienen relaciones.

Puedes probar los módulos desde la raíz del proyecto con `PYTHONPATH=app python`.

```python
from crud.tags import getTags
from crud.user import getUsers
from database import db

try:
    print(getUsers())
    print(getTags())
finally:
    db.close()
```
