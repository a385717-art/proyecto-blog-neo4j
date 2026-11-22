// El correo identifica a cada usuario en las consultas del CRUD.
CREATE CONSTRAINT user_email_unique IF NOT EXISTS
FOR (u:User) REQUIRE u.email IS UNIQUE;

// El nombre identifica a cada etiqueta en las consultas del CRUD.
CREATE CONSTRAINT tag_name_unique IF NOT EXISTS
FOR (t:Tag) REQUIRE t.name IS UNIQUE;

// Los artículos pueden repetir título en fechas distintas.
CREATE CONSTRAINT article_title_date_unique IF NOT EXISTS
FOR (a:Article) REQUIRE (a.title, a.date) IS UNIQUE;

// La URL identifica a cada comentario en las consultas del CRUD.
CREATE CONSTRAINT comment_url_unique IF NOT EXISTS
FOR (c:Comment) REQUIRE c.url IS UNIQUE;

// El nombre identifica a cada categoría en las consultas del CRUD.
CREATE CONSTRAINT category_name_unique IF NOT EXISTS
FOR (c:Category) REQUIRE c.name IS UNIQUE;
