-- ================================================================
-- Athena queries para UTECRate
-- FIX: nombres de tablas corregidos (los originales referenciaban
--      tablas inexistentes: users_users, content_enrollments, etc.)
--
-- Tablas reales en S3/Glue:
--   utecrate.usuarios       (de ms-users/PostgreSQL)
--   utecrate.carrera        (de ms-academic/MySQL)
--   utecrate.curso          (de ms-academic/MySQL)
--   utecrate.profesor_curso (de ms-academic/MySQL)
--   utecrate.calificaciones (de ms-reviews/MongoDB)
-- ================================================================

-- ── Q1: Top 10 profesores por promedio de calificaciones ──────
-- Une calificaciones (Mongo→S3) con usuarios (Postgres→S3)
SELECT
    u.nombre || ' ' || u.apellido   AS profesor,
    u.correo,
    COUNT(*)                        AS total_calificaciones,
    ROUND(AVG(CAST(c.puntaje AS DOUBLE)), 2) AS promedio
FROM utecrate.calificaciones c
JOIN utecrate.usuarios u
  ON c.profesor_id_cache = u.id
WHERE u.rol = 'PROFESOR'
GROUP BY u.id, u.nombre, u.apellido, u.correo
ORDER BY promedio DESC, total_calificaciones DESC
LIMIT 10;

-- ── Q2: Cursos con más calificaciones y su promedio ───────────
-- Une calificaciones con profesor_curso y curso
SELECT
    cu.nombre                                        AS curso,
    cu.codigo,
    COUNT(*)                                         AS total_calificaciones,
    ROUND(AVG(CAST(cal.puntaje AS DOUBLE)), 2)       AS promedio,
    COUNT(DISTINCT pc.profesor_id)                   AS profesores_distintos
FROM utecrate.calificaciones cal
JOIN utecrate.profesor_curso pc
  ON cal.profesor_curso_id = pc.id
JOIN utecrate.curso cu
  ON pc.curso_id = cu.id
GROUP BY cu.id, cu.nombre, cu.codigo
ORDER BY total_calificaciones DESC
LIMIT 10;

-- ── Q3: Distribución de usuarios por rol ─────────────────────
SELECT
    rol,
    COUNT(*)                          AS cantidad,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS porcentaje
FROM utecrate.usuarios
GROUP BY rol
ORDER BY cantidad DESC;

-- ── Q4: Calificaciones promedio por semestre ──────────────────
SELECT
    semestre,
    COUNT(*)                                   AS total,
    ROUND(AVG(CAST(puntaje AS DOUBLE)), 2)     AS promedio,
    MIN(CAST(puntaje AS DOUBLE))               AS minimo,
    MAX(CAST(puntaje AS DOUBLE))               AS maximo
FROM utecrate.calificaciones
WHERE semestre IS NOT NULL
GROUP BY semestre
ORDER BY semestre DESC;
