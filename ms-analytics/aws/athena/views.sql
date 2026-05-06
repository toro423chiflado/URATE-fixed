-- ================================================================
-- Vistas en Athena para UTECRate
-- FIX: nombres de tablas corregidos, lógica ajustada a esquema real
-- ================================================================

-- ── Vista 1: ranking_profesores ───────────────────────────────
-- Consolida datos de MS1 (usuarios) + MS3 (calificaciones)
CREATE OR REPLACE VIEW utecrate.ranking_profesores AS
SELECT
    u.id                                                       AS profesor_id,
    u.nombre || ' ' || u.apellido                             AS nombre_completo,
    u.correo,
    u.foto,
    COUNT(c.puntaje)                                           AS total_reviews,
    ROUND(AVG(CAST(c.puntaje AS DOUBLE)), 2)                  AS promedio,
    SUM(CASE WHEN CAST(c.puntaje AS DOUBLE) >= 4.5 THEN 1 ELSE 0 END) AS reviews_excelentes
FROM utecrate.usuarios u
LEFT JOIN utecrate.calificaciones c
    ON c.profesor_id_cache = u.id
WHERE u.rol = 'PROFESOR'
GROUP BY u.id, u.nombre, u.apellido, u.correo, u.foto;

-- ── Vista 2: resumen_cursos ───────────────────────────────────
-- Consolida MS2 (cursos/carreras) + MS3 (calificaciones)
CREATE OR REPLACE VIEW utecrate.resumen_cursos AS
SELECT
    cu.id                                                      AS curso_id,
    cu.nombre                                                  AS curso,
    cu.codigo,
    ca.nombre                                                  AS carrera,
    COUNT(DISTINCT pc.profesor_id)                             AS num_profesores,
    COUNT(cal.puntaje)                                         AS total_calificaciones,
    ROUND(AVG(CAST(cal.puntaje AS DOUBLE)), 2)                AS promedio_calificacion
FROM utecrate.curso cu
JOIN utecrate.carrera ca
    ON cu.carrera_id = ca.id
LEFT JOIN utecrate.profesor_curso pc
    ON pc.curso_id = cu.id
LEFT JOIN utecrate.calificaciones cal
    ON cal.profesor_curso_id = pc.id
GROUP BY cu.id, cu.nombre, cu.codigo, ca.nombre;
