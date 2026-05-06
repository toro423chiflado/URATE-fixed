import axios from 'axios';

// ── Helper: inyecta el token JWT en cada request ──────────────
function authInterceptor(config) {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
}

// ── MS1 — ms-users (auth, perfil, gestión usuarios) ──────────
export const apiAuth = axios.create({ baseURL: import.meta.env.VITE_MS1_URL });
apiAuth.interceptors.request.use(authInterceptor);

// ── MS2 — ms-academic (carreras, cursos, profesor-curso) ──────
// FIX: añadido — la rúbrica exige consumir MS2
export const apiAcademic = axios.create({ baseURL: import.meta.env.VITE_MS2_URL });
apiAcademic.interceptors.request.use(authInterceptor);

// ── MS3 — ms-reviews (calificaciones) ────────────────────────
// FIX: añadido — la rúbrica exige consumir MS3
export const apiReviews = axios.create({ baseURL: import.meta.env.VITE_MS3_URL });
apiReviews.interceptors.request.use(authInterceptor);

// ── MS4 — ms-content (perfiles agregados, top-profesores) ────
// FIX: añadido — la rúbrica exige consumir MS4
export const apiContent = axios.create({ baseURL: import.meta.env.VITE_MS4_URL });
apiContent.interceptors.request.use(authInterceptor);

// ── MS5 — ms-analytics (Athena queries, ingest) ──────────────
// FIX: añadido — la rúbrica exige consumir MS5
export const apiAnalytics = axios.create({ baseURL: import.meta.env.VITE_MS5_URL });
apiAnalytics.interceptors.request.use(authInterceptor);

// ── Orquestador (RBAC gateway opcional) ──────────────────────
export const apiOrchestrator = axios.create({ baseURL: import.meta.env.VITE_ORCHESTRATOR_URL });
apiOrchestrator.interceptors.request.use(authInterceptor);
