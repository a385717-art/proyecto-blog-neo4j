// Datos de prueba para el blog.
// Todo usa MERGE, así que se puede correr varias veces sin duplicar nodos ni relaciones.
// Hay que correr antes 01_constraints.cypher.

// Usuarios (Miguel no escribe artículos, solo comenta)
UNWIND [
  {name: 'Ana López', email: 'ana.lopez@example.com'},
  {name: 'Carlos Méndez', email: 'carlos.mendez@example.com'},
  {name: 'Laura Ruiz', email: 'laura.ruiz@example.com'},
  {name: 'Miguel Torres', email: 'miguel.torres@example.com'}
] AS d
MERGE (u:User {email: d.email})
SET u.name = d.name;

// Etiquetas
UNWIND [
  {name: 'neo4j', url: 'https://miblog.com/tags/neo4j'},
  {name: 'cypher', url: 'https://miblog.com/tags/cypher'},
  {name: 'python', url: 'https://miblog.com/tags/python'},
  {name: 'tkinter', url: 'https://miblog.com/tags/tkinter'},
  {name: 'linux', url: 'https://miblog.com/tags/linux'}
] AS d
MERGE (t:Tag {name: d.name})
SET t.url = d.url;

// Categorías
UNWIND [
  {name: 'Bases de Datos', url: 'https://miblog.com/categorias/bases-de-datos'},
  {name: 'Programación', url: 'https://miblog.com/categorias/programacion'},
  {name: 'Tutoriales', url: 'https://miblog.com/categorias/tutoriales'}
] AS d
MERGE (c:Category {name: d.name})
SET c.url = d.url;

// Artículos con su autor, su categoría y sus etiquetas
UNWIND [
  {title: 'Primeros pasos con Neo4j', date: date('2026-11-01'),
   text: 'Cómo crear una instancia gratis en AuraDB y conectarse desde el navegador.',
   autor: 'ana.lopez@example.com', categoria: 'Bases de Datos', tags: ['neo4j']},
  {title: 'Consultas básicas en Cypher', date: date('2026-11-03'),
   text: 'Ejemplos de MATCH, WHERE y RETURN para buscar nodos y relaciones.',
   autor: 'ana.lopez@example.com', categoria: 'Bases de Datos', tags: ['cypher', 'neo4j']},
  {title: 'Entornos virtuales en Python', date: date('2026-11-05'),
   text: 'Para qué sirve venv y cómo instalar paquetes sin romper el sistema.',
   autor: 'carlos.mendez@example.com', categoria: 'Programación', tags: ['python', 'linux']},
  {title: 'Interfaces gráficas con Tkinter', date: date('2026-11-08'),
   text: 'Una ventana con pestañas, tablas y botones usando ttk.',
   autor: 'carlos.mendez@example.com', categoria: 'Programación', tags: ['python', 'tkinter']},
  {title: 'Cómo instalar Linux sin morir en el intento', date: date('2026-11-10'),
   text: 'Pasos para hacer la USB, particionar el disco e instalar.',
   autor: 'laura.ruiz@example.com', categoria: 'Tutoriales', tags: ['linux']},
  {title: 'Conectar Python con Neo4j', date: date('2026-11-12'),
   text: 'Uso del driver oficial de Neo4j y un archivo .env para las credenciales.',
   autor: 'laura.ruiz@example.com', categoria: 'Bases de Datos', tags: ['python', 'neo4j']}
] AS d
MATCH (u:User {email: d.autor})
MATCH (c:Category {name: d.categoria})
MERGE (a:Article {title: d.title, date: d.date})
SET a.text = d.text
MERGE (u)-[:WROTE]->(a)
MERGE (a)-[:IN_CATEGORY]->(c)
WITH a, d
UNWIND d.tags AS tagName
MATCH (t:Tag {name: tagName})
MERGE (a)-[:HAS_TAG]->(t);

// Comentarios con quién los escribió y en qué artículo van
UNWIND [
  {name: 'Me sirvió mucho para la tarea', url: 'https://miblog.com/comentarios/1',
   autor: 'miguel.torres@example.com', titulo: 'Consultas básicas en Cypher', fecha: date('2026-11-03')},
  {name: 'Faltó explicar OPTIONAL MATCH', url: 'https://miblog.com/comentarios/2',
   autor: 'carlos.mendez@example.com', titulo: 'Consultas básicas en Cypher', fecha: date('2026-11-03')},
  {name: 'Buen resumen de MATCH y WHERE', url: 'https://miblog.com/comentarios/3',
   autor: 'laura.ruiz@example.com', titulo: 'Consultas básicas en Cypher', fecha: date('2026-11-03')},
  {name: 'No sabía que ttk tenía Treeview', url: 'https://miblog.com/comentarios/4',
   autor: 'ana.lopez@example.com', titulo: 'Interfaces gráficas con Tkinter', fecha: date('2026-11-08')},
  {name: '¿Funciona igual en Windows?', url: 'https://miblog.com/comentarios/5',
   autor: 'miguel.torres@example.com', titulo: 'Interfaces gráficas con Tkinter', fecha: date('2026-11-08')},
  {name: 'Aura me pidió verificar el correo', url: 'https://miblog.com/comentarios/6',
   autor: 'carlos.mendez@example.com', titulo: 'Primeros pasos con Neo4j', fecha: date('2026-11-01')},
  {name: 'Yo me quedé en la parte de las particiones', url: 'https://miblog.com/comentarios/7',
   autor: 'miguel.torres@example.com', titulo: 'Cómo instalar Linux sin morir en el intento', fecha: date('2026-11-10')},
  {name: 'Con el driver 5 cambian algunas cosas', url: 'https://miblog.com/comentarios/8',
   autor: 'ana.lopez@example.com', titulo: 'Conectar Python con Neo4j', fecha: date('2026-11-12')}
] AS d
MATCH (u:User {email: d.autor})
MATCH (a:Article {title: d.titulo, date: d.fecha})
MERGE (c:Comment {url: d.url})
SET c.name = d.name
MERGE (u)-[:WROTE]->(c)
MERGE (a)-[:HAS_COMMENT]->(c);
