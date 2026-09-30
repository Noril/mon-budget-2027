// Fonction Vercel : enregistre, de façon anonyme et sur consentement, les choix d'une partie du jeu.
// Aucune donnée personnelle : ni adresse IP, ni cookie, ni identifiant, ni heure (le jour seulement).
// Base Postgres (Neon, région UE) jointe par son API HTTP : aucune dépendance à installer.
import { LEVIERS, VERSION } from "./_leviers.js";

const LIMITE = new Map(); // anti-robots en mémoire de l'instance ; l'adresse IP n'est jamais écrite
const FENETRE_MS = 60_000, MAX_PAR_FENETRE = 5;

function trop(ip) {
  const maintenant = Date.now();
  const r = (LIMITE.get(ip) || []).filter(t => maintenant - t < FENETRE_MS);
  r.push(maintenant);
  LIMITE.set(ip, r);
  if (LIMITE.size > 5000) LIMITE.clear();
  return r.length > MAX_PAR_FENETRE;
}

function nettoyer(choix) {
  // ne garde que des leviers et des valeurs connus : rien d'arbitraire n'entre dans la base
  const propre = {};
  if (!choix || typeof choix !== "object" || Array.isArray(choix)) return null;
  for (const [id, v] of Object.entries(choix)) {
    const l = LEVIERS[id];
    if (!l) continue;
    if (l.options ? l.options.includes(v) : typeof v === "number" && Number.isFinite(v) && v >= l.min && v <= l.max) propre[id] = v;
  }
  return Object.keys(propre).length ? propre : null;
}

async function sql(requete, params) {
  const url = new URL(process.env.DATABASE_URL);
  const r = await fetch(`https://${url.hostname}/sql`, {
    method: "POST",
    headers: { "Neon-Connection-String": process.env.DATABASE_URL, "Content-Type": "application/json" },
    body: JSON.stringify({ query: requete, params }),
  });
  if (!r.ok) throw new Error(`base : ${r.status}`);
  return r.json();
}

export default async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store");
  if (req.method !== "POST") return res.status(405).json({ erreur: "POST seulement" });
  if (!process.env.DATABASE_URL) return res.status(503).json({ erreur: "statistiques non configurées" });
  const ip = (req.headers["x-forwarded-for"] || "").split(",")[0].trim();
  if (trop(ip)) return res.status(429).json({ erreur: "trop de requêtes" });
  const corps = typeof req.body === "string" ? JSON.parse(req.body || "{}") : req.body || {};
  if (JSON.stringify(corps).length > 4000 || corps.consentement !== true) return res.status(400).json({ erreur: "requête refusée" });
  const choix = nettoyer(corps.choix);
  if (!choix || Object.keys(choix).length < 10) return res.status(400).json({ erreur: "partie incomplète" });
  try {
    await sql(`CREATE TABLE IF NOT EXISTS parties (id BIGSERIAL PRIMARY KEY, jour DATE NOT NULL DEFAULT CURRENT_DATE,
      version TEXT NOT NULL, choix JSONB NOT NULL)`, []);
    await sql("INSERT INTO parties (version, choix) VALUES ($1, $2)", [VERSION, JSON.stringify(choix)]);
    return res.status(204).end();
  } catch (e) {
    return res.status(500).json({ erreur: "enregistrement impossible" });
  }
}
