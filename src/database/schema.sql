-- Leads del cualificador de Meta Ads
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    telefono TEXT NOT NULL,
    email TEXT,
    checkin DATE NOT NULL,
    checkout DATE NOT NULL,
    adultos INTEGER NOT NULL DEFAULT 1,
    menores INTEGER NOT NULL DEFAULT 0,
    tipo_habitacion TEXT NOT NULL,
    mensaje TEXT,
    utm_source TEXT,
    utm_campaign TEXT,
    estado TEXT NOT NULL DEFAULT 'nuevo',  -- nuevo, contactado, reservado, perdido
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    contactado_at DATETIME,
    reservado_at DATETIME,
    notas TEXT
);

CREATE INDEX IF NOT EXISTS idx_leads_estado ON leads(estado);
CREATE INDEX IF NOT EXISTS idx_leads_created ON leads(created_at);
