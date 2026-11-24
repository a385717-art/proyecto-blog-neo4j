# proyecto-blog-neo4j

Aplicación en Python para administrar un blog guardado en Neo4j (AuraDB). Tiene el CRUD de usuarios, artículos, comentarios, etiquetas y categorías, las relaciones entre ellos, una interfaz gráfica hecha con Tkinter y unos archivos de Cypher con datos de prueba y consultas.

## Modelo

Los nodos son `User`, `Article`, `Comment`, `Tag` y `Category`. Estas son las relaciones que usamos:

| Relación | Tipo |
| --- | --- |
| `(User)-[:WROTE]->(Article)` | 1-N, cada artículo tiene un solo autor |
| `(User)-[:WROTE]->(Comment)` | 1-N |
| `(Article)-[:HAS_COMMENT]->(Comment)` | 1-N |
| `(Article)-[:HAS_TAG]->(Tag)` | N-N |
| `(Article)-[:IN_CATEGORY]->(Category)` | N-N |

Cada nodo se busca por un identificador. El usuario por su correo, la etiqueta y la categoría por su nombre, el comentario por su URL y el artículo por su título y su fecha juntos. Puede haber dos artículos con el mismo título si tienen fecha distinta.

## Estructura

| Archivo o carpeta | Qué tiene |
| --- | --- |
| `app/main.py` | Abre la ventana. Antes revisa que se pueda conectar a Neo4j y si no, muestra un mensaje. |
| `app/config.py` | Lee los datos de conexión del archivo `.env`. |
| `app/database.py` | La conexión a Neo4j. Todas las consultas pasan por `db.query()` con parámetros. |
| `app/crud/user.py`, `tags.py`, `categories.py`, `comments.py`, `articles.py` | Crear, listar, buscar, actualizar y borrar cada tipo de nodo. |
| `app/crud/relations.py` | Las relaciones: asignar autor, agregar comentarios, poner y quitar etiquetas y categorías, el detalle de un artículo y los listados por usuario, etiqueta y categoría. |
| `app/ui/menu.py` | La ventana principal con una pestaña por entidad. |
| `app/ui/users_tab.py` | Pestaña de usuarios. |
| `app/ui/articles_tab.py` | Pestaña de artículos con el panel de detalle. |
| `app/ui/comments_tab.py` | Pestaña de comentarios. |
| `app/ui/name_url_tab.py` | Pestaña que se usa para categorías y para etiquetas, porque las dos solo tienen nombre y URL. |
| `app/ui/common.py` | Cosas que usan todas las pestañas: mensajes de error y validar campos vacíos y fechas. |
| `cypher/01_constraints.cypher` | Restricciones para que no se repitan los identificadores. |
| `cypher/02_datos_prueba.cypher` | Datos de prueba: 4 usuarios, 6 artículos, 8 comentarios, 5 etiquetas y 3 categorías. |
| `cypher/03_consultas.cypher` | 10 consultas de ejemplo sobre esos datos. |

## Instalación

Se necesita Python 3.10 o más nuevo.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

En fish el entorno se activa con `source .venv/bin/activate.fish` y en Windows con `.venv\Scripts\activate`.

La interfaz usa Tkinter. En Windows ya viene con Python, pero en Linux a veces hay que instalarlo aparte:

```bash
sudo pacman -S tk            # Arch o CachyOS
sudo apt install python3-tk  # Ubuntu o Debian
```

Para revisar que quedó, `python -c "import tkinter"` no debe marcar error.

## Archivo .env

Copia `.env.example` a `.env` en la raíz del proyecto y llena los datos de tu instancia de Aura:

```dotenv
NEO4J_URI=neo4j+s://TU_ID_DE_INSTANCIA.databases.neo4j.io
NEO4J_USER=TU_ID_DE_INSTANCIA
NEO4J_PASSWORD=
NEO4J_DATABASE=TU_ID_DE_INSTANCIA
```

En Aura el usuario y el nombre de la base son el ID de la instancia, o sea lo que sale en la URI antes de `.databases.neo4j.io`. Si usas Neo4j instalado en tu computadora en lugar de Aura, la URI es `bolt://localhost:7687` y ahí el usuario y la base sí son `neo4j` (si quitas la línea de `NEO4J_DATABASE` también se usa `neo4j`). El `.env` está en el `.gitignore` para que la contraseña no se suba.

## Cargar la base con los archivos de cypher/

Los archivos se corren en orden. Abre tu instancia en la consola de Aura, entra a Query, pega el contenido del archivo y córrelo.

1. `01_constraints.cypher` crea las restricciones: no se pueden repetir correos, nombres de etiquetas o categorías, URLs de comentarios ni artículos con el mismo título y fecha. Si ya existen no pasa nada.
2. `02_datos_prueba.cypher` carga los datos de prueba con todas sus relaciones. Usa `MERGE`, así que si se corre dos veces no se duplica nada.
3. `03_consultas.cypher` tiene 10 consultas y cada una tiene arriba un comentario de qué busca. Conviene correrlas de una en una para ver el resultado de cada una.

## Abrir la interfaz

Desde la raíz del proyecto y con el entorno activado:

```bash
python app/main.py
```

Si falta algo en el `.env`, la contraseña está mal o no hay internet, sale un mensaje en lugar de la ventana.

La ventana tiene cinco pestañas: Usuarios, Artículos, Categorías, Etiquetas y Comentarios. Cada una tiene una tabla y botones para Crear, Actualizar, Borrar, Refrescar y Limpiar. Para editar algo primero se selecciona en la tabla. El identificador no se puede cambiar desde la interfaz (el correo del usuario, el nombre de la etiqueta o categoría, la URL del comentario y el título y fecha del artículo).

En la pestaña de Artículos, al seleccionar uno aparece a la derecha su detalle con el autor, las etiquetas, las categorías y los comentarios. Desde ahí se le asigna autor, se le ponen o quitan etiquetas y categorías y se le agregan comentarios.

Las fechas se escriben como `AAAA-MM-DD`, por ejemplo `2026-11-24`. Si la fecha está mal escrita o no existe, la interfaz avisa antes de mandarla a Neo4j.

## Borrar nodos con relaciones

Las funciones de borrar del CRUD (`deleteUser`, `deleteArticle`, `deleteTag`, `deleteCategory` y `deleteComment`) tienen un parámetro `detach`.

- Con `detach=False`, que es el valor por defecto, Neo4j no deja borrar un nodo que todavía tiene relaciones y regresa un error.
- Con `detach=True` se borran sus relaciones y después el nodo. Al borrar un artículo también se borran sus comentarios para que no queden comentarios sueltos.

En la interfaz primero se pregunta si de verdad quieres borrar. Si el nodo tiene relaciones sale otra pregunta que dice qué va a pasar, y solo si contestas que sí se borra con `detach=True`. Al borrar un usuario sus artículos y comentarios se quedan sin autor, y al borrar una etiqueta o una categoría los artículos solo se quedan sin ella. Los comentarios se borran directo con sus relaciones porque siempre están ligados a un autor y a un artículo.

## Otras cosas del CRUD

- Crear regresa el nodo creado.
- Buscar y actualizar regresan el nodo, o `None` si no existe.
- Borrar regresa `True` si se borró y `False` si no existía.
- La URL de las etiquetas es opcional. Si se actualiza una etiqueta con `url=None` se le quita la URL.
- Las fechas de los artículos se guardan como `DATE`. Neo4j las regresa como `neo4j.time.Date` y para mostrarlas se pasan a texto con `.iso_format()`.

## Probar el CRUD desde la consola

Desde la raíz del proyecto se puede abrir Python con `PYTHONPATH=app python` (en fish es igual) y probar las funciones:

```python
from crud import getTags, getUsers
from database import db

try:
    print(getUsers())
    print(getTags())
finally:
    db.close()
```
