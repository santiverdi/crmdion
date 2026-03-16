# Analytics - Hotel Dion (FOCO MARKETING)

> 964 reservas | 778 huespedes | $1,104M revenue

## Huespedes por segmento
```dataview
TABLE length(rows) as "Cantidad", sum(rows.gasto_total) as "Revenue"
FROM "01 - Huespedes/Hotel-Dion"
WHERE tipo = "huesped"
GROUP BY segmento
SORT sum(rows.gasto_total) DESC
```

## Por canal
```dataview
TABLE length(rows) as "Huespedes", sum(rows.gasto_total) as "Revenue"
FROM "01 - Huespedes/Hotel-Dion"
WHERE tipo = "huesped"
GROUP BY canal
SORT sum(rows.gasto_total) DESC
```

## Por tipo de viajero
```dataview
TABLE length(rows) as "Cantidad", sum(rows.gasto_total) as "Revenue"
FROM "01 - Huespedes/Hotel-Dion"
WHERE tipo = "huesped"
GROUP BY tipo_viajero
SORT length(rows) DESC
```

## Por mercado
```dataview
TABLE length(rows) as "Cantidad", sum(rows.gasto_total) as "Revenue"
FROM "01 - Huespedes/Hotel-Dion"
WHERE tipo = "huesped"
GROUP BY mercado
SORT sum(rows.gasto_total) DESC
```

## Por ciudad de origen
```dataview
TABLE length(rows) as "Huespedes"
FROM "01 - Huespedes/Hotel-Dion"
WHERE tipo = "huesped" AND ciudad != ""
GROUP BY ciudad
SORT length(rows) DESC
LIMIT 15
```

## Top huespedes Dion
```dataview
TABLE total_visitas as "Visitas", gasto_total as "Gasto", canal, telefono, email
FROM "01 - Huespedes/Hotel-Dion"
WHERE tipo = "huesped"
SORT gasto_total DESC
LIMIT 30
```

## VIPs Dion
```dataview
TABLE total_visitas as "Visitas", gasto_total as "Gasto", canal, telefono
FROM "01 - Huespedes/Hotel-Dion"
WHERE segmento = "VIP"
SORT gasto_total DESC
```

## Huespedes Dion que reservaron por Booking (convertir a directo)
```dataview
TABLE gasto_total as "Gasto", telefono, email, ciudad
FROM "01 - Huespedes/Hotel-Dion"
WHERE canal = "Booking.com"
SORT gasto_total DESC
```

## Campanas Dion
- **Post-estadia**: 171 contactos → `07 - Campañas/Hotel-Dion/post_estadia_Hotel-Dion.csv`
- **Booking a directo**: 116 contactos → `07 - Campañas/Hotel-Dion/booking_Hotel-Dion.csv`
- **Master completo**: 778 contactos → `07 - Campañas/Hotel-Dion/MASTER_Hotel-Dion.csv`
