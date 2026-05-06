-- ================================================================
-- Agregar img_url a carreras y cursos
-- Ejecutar DESPUÉS del data.sql principal
-- ================================================================

-- CARRERAS — logos por color de facultad
UPDATE carrera SET img_url = 'https://placehold.co/400x200/6366F1/white?text=Cursos+Generales'        WHERE codigo = 'CG';
UPDATE carrera SET img_url = 'https://placehold.co/400x200/06B6D4/white?text=Sistemas+de+Informacion' WHERE codigo = 'SI';
UPDATE carrera SET img_url = 'https://placehold.co/400x200/EC4899/white?text=Ciencia+de+Datos+IA'     WHERE codigo = 'CDIA';
UPDATE carrera SET img_url = 'https://placehold.co/400x200/8B5CF6/white?text=Ciencia+Computacion'     WHERE codigo = 'CC';
UPDATE carrera SET img_url = 'https://placehold.co/400x200/EF4444/white?text=Ciberseguridad'          WHERE codigo = 'CS';
UPDATE carrera SET img_url = 'https://placehold.co/400x200/0369A1/white?text=Admin+Negocios'          WHERE codigo = 'AND';
UPDATE carrera SET img_url = 'https://placehold.co/400x200/059669/white?text=Business+Analytics'      WHERE codigo = 'BA';
UPDATE carrera SET img_url = 'https://placehold.co/400x200/F59E0B/white?text=Ing+Industrial'          WHERE codigo = 'II';
UPDATE carrera SET img_url = 'https://placehold.co/400x200/10B981/white?text=Bioingeneria'             WHERE codigo = 'BI';
UPDATE carrera SET img_url = 'https://placehold.co/400x200/F97316/white?text=Ing+Energia'             WHERE codigo = 'IE';
UPDATE carrera SET img_url = 'https://placehold.co/400x200/64748B/white?text=Ing+Mecanica'            WHERE codigo = 'IM';
UPDATE carrera SET img_url = 'https://placehold.co/400x200/7C3AED/white?text=Ing+Quimica'             WHERE codigo = 'IQ';
UPDATE carrera SET img_url = 'https://placehold.co/400x200/065F46/white?text=Ing+Ambiental'           WHERE codigo = 'IA';
UPDATE carrera SET img_url = 'https://placehold.co/400x200/9F1239/white?text=Ing+Civil'               WHERE codigo = 'IC';
UPDATE carrera SET img_url = 'https://placehold.co/400x200/0891B2/white?text=Ing+Electronica'         WHERE codigo = 'IEL';
UPDATE carrera SET img_url = 'https://placehold.co/400x200/BE123C/white?text=Ing+Mecatronica'         WHERE codigo = 'IMT';

-- CURSOS — imagen generada con el color y nombre del curso
UPDATE curso SET img_url = CONCAT(
    'https://placehold.co/400x200/',
    REPLACE(color_hex, '#', ''),
    '/white?text=',
    REPLACE(REPLACE(REPLACE(nombre, ' ', '+'), 'á','a'), 'é','e')
) WHERE img_url IS NULL;
