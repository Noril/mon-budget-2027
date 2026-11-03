// Fonction Vercel : enregistre, de façon anonyme, les choix d'une partie terminée du jeu.
// Aucune donnée personnelle : ni adresse IP, ni cookie, ni identifiant, ni heure (le jour seulement).
// Base Postgres (Neon, région UE) jointe par son API HTTP : aucune dépendance à installer.
import { LEVIERS, THEMES, VERSION, MAX_DECISIONS } from "./_leviers.js";

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

function nettoyerThemes(themes) {
  // thèmes joués : identifiant connu -> 1 (inclus) ou 2 (favori) ; le reste est ignoré
  const propre = {};
  if (!themes || typeof themes !== "object" || Array.isArray(themes)) return propre;
  for (const [id, v] of Object.entries(themes)) if (THEMES.includes(id) && (v === 1 || v === 2)) propre[id] = v;
  return propre;
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
  // déploiements d'aperçu (tests) : rien n'est enregistré, pour ne pas mêler les essais aux vraies parties
  if (process.env.VERCEL_ENV && process.env.VERCEL_ENV !== "production") return res.status(204).end();
  if (!process.env.DATABASE_URL) return res.status(503).json({ erreur: "statistiques non configurées" });
  const ip = (req.headers["x-forwarded-for"] || "").split(",")[0].trim();
  if (trop(ip)) return res.status(429).json({ erreur: "trop de requêtes" });
  const corps = typeof req.body === "string" ? JSON.parse(req.body || "{}") : req.body || {};
  if (JSON.stringify(corps).length > 4000) return res.status(400).json({ erreur: "requête refusée" });
  const choix = nettoyer(corps.choix);
  if (!choix || Object.keys(choix).length < 10) return res.status(400).json({ erreur: "partie incomplète" });
  const themes = nettoyerThemes(corps.themes);
  const decisions = Number.isInteger(corps.decisions) && corps.decisions > 0 && corps.decisions <= 200 ? corps.decisions : null;
  const plafond = corps.plafond === true;
  try {
    await sql(`CREATE TABLE IF NOT EXISTS parties (id BIGSERIAL PRIMARY KEY, jour DATE NOT NULL DEFAULT CURRENT_DATE,
      version TEXT NOT NULL, choix JSONB NOT NULL)`, []);
    // colonnes ajoutées avec le choix des thèmes (parties antérieures : NULL)
    await sql(`ALTER TABLE parties ADD COLUMN IF NOT EXISTS themes JSONB, ADD COLUMN IF NOT EXISTS decisions INTEGER,
      ADD COLUMN IF NOT EXISTS plafond BOOLEAN`, []);
    await sql("INSERT INTO parties (version, choix, themes, decisions, plafond) VALUES ($1, $2, $3, $4, $5)",
      [VERSION, JSON.stringify(choix), JSON.stringify(themes), decisions, plafond && decisions >= MAX_DECISIONS]);
    return res.status(204).end();
  } catch (e) {
    return res.status(500).json({ erreur: "enregistrement impossible" });
  }
}
