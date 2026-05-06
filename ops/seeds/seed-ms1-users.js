/**
 * Seed oficial MS1 — ms-users
 * Profesores con foto, 25,000 usuarios fake
 * Correr: node prisma/seed.js
 */
const { PrismaClient } = require('@prisma/client');
const bcrypt = require('bcryptjs');
const { faker } = require('@faker-js/faker');

const prisma = new PrismaClient();

// Genera URL de avatar con UI Avatars
function avatar(nombre, apellido, color = '6366f1') {
  const name = encodeURIComponent(`${nombre} ${apellido}`);
  return `https://ui-avatars.com/api/?name=${name}&background=${color}&color=fff&size=200&bold=true`;
}

const PROFESORES_FIJOS = [
  {
    id: '00000000-0000-0000-0000-000000000001',
    nombre: 'Juan', apellido: 'Pérez',
    correo: 'juan.perez@utec.edu.pe',
    password: 'profesor123',
    rol: 'PROFESOR',
    foto: avatar('Juan', 'Pérez', '6366f1'),
    github: 'https://github.com/jperez',
    linkedin: 'https://linkedin.com/in/juan-perez-utec',
  },
  {
    id: '00000000-0000-0000-0000-000000000002',
    nombre: 'Ana', apellido: 'Torres',
    correo: 'ana.torres@utec.edu.pe',
    password: 'profesor123',
    rol: 'PROFESOR',
    foto: avatar('Ana', 'Torres', 'ec4899'),
    github: 'https://github.com/atorres',
    linkedin: 'https://linkedin.com/in/ana-torres-utec',
  },
  {
    id: '00000000-0000-0000-0000-000000000003',
    nombre: 'Pedro', apellido: 'Ruiz',
    correo: 'pedro.ruiz@utec.edu.pe',
    password: 'profesor123',
    rol: 'PROFESOR',
    foto: avatar('Pedro', 'Ruiz', 'f97316'),
    linkedin: 'https://linkedin.com/in/pedro-ruiz-utec',
  },
  {
    id: '00000000-0000-0000-0000-000000000004',
    nombre: 'María', apellido: 'García',
    correo: 'maria.garcia@utec.edu.pe',
    password: 'estudiante123',
    rol: 'ESTUDIANTE',
    foto: avatar('María', 'García', '10b981'),
  },
];

async function main() {
  console.log('🌱 Iniciando seed...');

  // Limpiar
  await prisma.accesoPadlet.deleteMany();
  await prisma.refreshToken.deleteMany();
  await prisma.usuario.deleteMany();
  console.log('🧹 Tablas limpias');

  // Admin
  const adminHash = await bcrypt.hash('admin123', 10);
  await prisma.usuario.create({
    data: {
      id: '00000000-0000-0000-0000-000000000000',
      nombre: 'Admin', apellido: 'UTEC',
      correo: 'admin@utec.edu.pe',
      passwordHash: adminHash,
      rol: 'ADMIN',
      foto: avatar('Admin', 'UTEC', '1e293b'),
    }
  });

  // Profesores y estudiante fijos
  for (const p of PROFESORES_FIJOS) {
    const hash = await bcrypt.hash(p.password, 10);
    await prisma.usuario.create({
      data: {
        id: p.id,
        nombre: p.nombre, apellido: p.apellido,
        correo: p.correo,
        passwordHash: hash,
        rol: p.rol,
        foto: p.foto,
        github: p.github || null,
        linkedin: p.linkedin || null,
      }
    });
  }
  console.log('✅ Usuarios fijos creados (admin + 3 profesores + 1 estudiante)');

  // 25,000 usuarios fake
  const fakeHash = await bcrypt.hash('utec2025', 10);
  const ROLES = ['PROFESOR', 'ESTUDIANTE', 'ESTUDIANTE', 'ESTUDIANTE']; // más estudiantes
  const TOTAL = 25000;
  const BATCH = 500;
  const COLORES = ['6366f1', 'ec4899', '10b981', 'f97316', '0891b2', '8b5cf6', 'ef4444'];

  let created = 0;
  for (let i = 0; i < TOTAL; i += BATCH) {
    const batch = [];
    const size = Math.min(BATCH, TOTAL - i);
    for (let j = 0; j < size; j++) {
      const nombre   = faker.person.firstName();
      const apellido = faker.person.lastName();
      const uniq     = faker.string.alphanumeric(6).toLowerCase();
      const rol      = ROLES[Math.floor(Math.random() * ROLES.length)];
      const color    = COLORES[Math.floor(Math.random() * COLORES.length)];

      batch.push({
        nombre, apellido,
        correo:       `${nombre.toLowerCase()}.${apellido.toLowerCase()}.${uniq}@utec.edu.pe`,
        passwordHash: fakeHash,
        rol,
        foto:         avatar(nombre, apellido, color),
        github:   Math.random() > 0.7 ? `https://github.com/${faker.internet.userName()}` : null,
        linkedin: Math.random() > 0.7 ? `https://linkedin.com/in/${faker.internet.userName()}` : null,
      });
    }
    await prisma.usuario.createMany({ data: batch, skipDuplicates: true });
    created += size;
    if (created % 5000 === 0) console.log(`   ${created}/${TOTAL}...`);
  }

  const total = await prisma.usuario.count();
  console.log(`\n✅ Seed completado — ${total} usuarios en la BD`);
  console.log('\n📋 Credenciales:');
  console.log('   ADMIN      → admin@utec.edu.pe        / admin123');
  console.log('   PROFESOR   → juan.perez@utec.edu.pe   / profesor123');
  console.log('   ESTUDIANTE → maria.garcia@utec.edu.pe / estudiante123');
}

main().catch(console.error).finally(() => prisma.$disconnect());
