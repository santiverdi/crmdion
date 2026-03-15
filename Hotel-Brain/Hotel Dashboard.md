# Grupo Hotelero - Dashboard Central

## El Grupo
| Hotel | Reservas | Perfiles | Revenue |
|-------|----------|----------|---------|
| **Hotel Valles** | 1,824 | 1,351 | $1,681M |
| **Hotel VIPS** | 1,442 | 1,065 | $1,277M |
| **Hotel Kings** | 1,785 | 1,321 | $1,239M |
| **Hotel Prince** | 1,057 | 838 | $1,107M |
| **Hotel Dion** | 964 | 778 | $1,104M |
| **Hotel America** | 626 | 448 | $772M |
| **TOTAL** | **7,698** | **5,801** | **$7,182M** |

> 166 huespedes estuvieron en mas de 1 hotel del grupo

## Navegacion por hotel
- [[01 - Huespedes/Hotel-Prince/|Hotel Prince]] (838 huespedes)
- [[01 - Huespedes/Hotel-Kings/|Hotel Kings]] (1,321 huespedes)
- [[01 - Huespedes/Hotel-VIPS/|Hotel VIPS]] (1,065 huespedes)
- [[01 - Huespedes/Hotel-America/|Hotel America]] (448 huespedes)
- [[01 - Huespedes/Hotel-Valles/|Hotel Valles]] (1,351 huespedes)
- [[01 - Huespedes/Hotel-Dion/|Hotel Dion]] (778 huespedes) ← FOCO MARKETING

## Navegacion general
- [[06 - Analytics/Index|Analytics Grupo]]
- [[06 - Analytics/Hotel Dion|Analytics Dion]]
- [[03 - Marketing/PLAN DE ACCION - Generar Inbound|Plan de Accion Inbound]]
- [[03 - Marketing/PLAN DE ACCION - Envio Masivo Sin Ban|Envio Masivo Sin Ban]]
- [[03 - Marketing/Estrategia General|Estrategia Marketing]]
- [[04 - Finanzas/Index|Finanzas]]

## Queries rapidas

### VIPs de todo el grupo
```dataview
TABLE hotel as "Hotel", total_visitas as "Visitas", gasto_total as "Gasto", canal as "Canal", telefono as "Tel"
FROM "01 - Huespedes"
WHERE segmento = "VIP"
SORT gasto_total DESC
LIMIT 20
```

### Huespedes Hotel Dion
```dataview
TABLE segmento, total_visitas as "Visitas", gasto_total as "Gasto", canal, ciudad
FROM "01 - Huespedes/Hotel-Dion"
WHERE tipo = "huesped"
SORT gasto_total DESC
LIMIT 30
```

### Buscar huesped por nombre
```dataview
TABLE hotel, segmento, gasto_total, telefono, email
FROM "01 - Huespedes"
WHERE tipo = "huesped" AND contains(nombre, "")
```

## Estado del proyecto
- [x] Importar datos 6 hoteles de TodoAlojamiento
- [x] Crear perfiles: 5,801 huespedes
- [x] Segmentacion: VIP, Recurrente, Primera vez
- [x] CSVs de campanas por hotel
- [x] Identificar 166 huespedes cross-hotel
- [x] Plan de marketing inbound
- [ ] Lanzar campana email (Brevo)
- [ ] Lanzar WhatsApp broadcast
- [ ] Completar Google Business
- [ ] Instagram ads

## Plugins Obsidian necesarios
- **Dataview** - Consultas en vivo (CRITICO)
- **Templater** - Templates dinamicos
- **Charts** - Graficos
- **Kanban** - Pipeline de campanas
