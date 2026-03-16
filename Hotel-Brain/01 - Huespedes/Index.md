# Huespedes - Base de datos

## Todos los huespedes
```dataview
TABLE
  segmento as "Segmento",
  tipo_viajero as "Tipo",
  total_visitas as "Visitas",
  gasto_total as "Gasto Total",
  canal as "Canal",
  ciudad as "Ciudad",
  ultima_visita as "Ultima visita"
FROM "01 - Huespedes"
WHERE tipo = "huesped"
SORT gasto_total DESC
```

## VIPs (3+ visitas o alto gasto)
```dataview
TABLE
  total_visitas as "Visitas",
  gasto_total as "Gasto",
  canal as "Canal",
  telefono as "Tel"
FROM "01 - Huespedes"
WHERE segmento = "VIP"
SORT gasto_total DESC
```

## Recurrentes
```dataview
TABLE total_visitas as "Visitas", gasto_total as "Gasto", canal as "Canal"
FROM "01 - Huespedes"
WHERE segmento = "Recurrente"
SORT gasto_total DESC
```

## Con email (para campanas)
```dataview
TABLE email as "Email", segmento as "Seg", gasto_total as "Gasto"
FROM "01 - Huespedes"
WHERE email != "" AND tipo = "huesped"
SORT gasto_total DESC
```

## Familias
```dataview
TABLE total_visitas as "Visitas", gasto_total as "Gasto", ciudad as "Ciudad"
FROM "01 - Huespedes"
WHERE tipo_viajero = "Familia"
SORT gasto_total DESC
```

## Por ciudad
```dataview
TABLE length(rows) as "Huespedes", sum(rows.gasto_total) as "Revenue"
FROM "01 - Huespedes"
WHERE tipo = "huesped"
GROUP BY ciudad
SORT length(rows) DESC
```
