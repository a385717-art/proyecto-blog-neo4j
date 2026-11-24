// Consultas de ejemplo sobre el grafo del blog.
// Usan los datos de 02_datos_prueba.cypher.

// 1. Artículos que escribió Ana, del más nuevo al más viejo
MATCH (u:User {email: 'ana.lopez@example.com'})-[:WROTE]->(a:Article)
RETURN a.title AS titulo, a.date AS fecha
ORDER BY a.date DESC;

// 2. Artículos que tienen la etiqueta python
MATCH (a:Article)-[:HAS_TAG]->(:Tag {name: 'python'})
RETURN a.title AS titulo, a.date AS fecha
ORDER BY a.date;

// 3. Comentarios de un artículo y quién escribió cada uno
MATCH (a:Article {title: 'Consultas básicas en Cypher', date: date('2026-11-03')})-[:HAS_COMMENT]->(c:Comment)
MATCH (u:User)-[:WROTE]->(c)
RETURN c.name AS comentario, u.name AS autor
ORDER BY autor;

// 4. Artículos de la categoría Bases de Datos con su autor
MATCH (u:User)-[:WROTE]->(a:Article)-[:IN_CATEGORY]->(:Category {name: 'Bases de Datos'})
RETURN a.title AS titulo, u.name AS autor, a.date AS fecha
ORDER BY a.date;

// 5. Etiquetas y categorías de un artículo
MATCH (a:Article {title: 'Conectar Python con Neo4j', date: date('2026-11-12')})
OPTIONAL MATCH (a)-[:HAS_TAG]->(t:Tag)
OPTIONAL MATCH (a)-[:IN_CATEGORY]->(c:Category)
RETURN a.title AS titulo, collect(DISTINCT t.name) AS etiquetas, collect(DISTINCT c.name) AS categorias;

// 6. Cuántos artículos hay en cada categoría
MATCH (c:Category)
OPTIONAL MATCH (a:Article)-[:IN_CATEGORY]->(c)
RETURN c.name AS categoria, count(a) AS articulos
ORDER BY articulos DESC, categoria;

// 7. Etiquetas más usadas
MATCH (a:Article)-[:HAS_TAG]->(t:Tag)
RETURN t.name AS etiqueta, count(a) AS veces
ORDER BY veces DESC, etiqueta;

// 8. Artículo con más comentarios
MATCH (a:Article)-[:HAS_COMMENT]->(c:Comment)
RETURN a.title AS titulo, count(c) AS comentarios
ORDER BY comentarios DESC
LIMIT 1;

// 9. Usuarios que no han escrito ningún artículo
MATCH (u:User)
WHERE NOT (u)-[:WROTE]->(:Article)
RETURN u.name AS nombre, u.email AS correo;

// 10. Artículos que comparten alguna etiqueta con 'Conectar Python con Neo4j'
MATCH (a:Article {title: 'Conectar Python con Neo4j', date: date('2026-11-12')})-[:HAS_TAG]->(t:Tag)<-[:HAS_TAG]-(otro:Article)
RETURN otro.title AS articulo, collect(t.name) AS etiquetas_en_comun
ORDER BY size(etiquetas_en_comun) DESC, articulo;
