o # Analytics - Hotel Prince

> Periodo: Sep 2025 - Mar 2026 | 7708 reservas totales | 6482 activas

## Resumen ejecutivo
| Metrica | Valor |
|---------|-------|
| Reservas totales | 7,708 |
| Reservas activas | 6,482 |
| Cancelaciones | 1,226 (15.9%) |
| Revenue total | $6,433,324,930 ARS |
| Revenue alojamiento | $6,404,395,401 ARS |
| Ticket promedio | $992,491 ARS |
| Tarifa promedio/noche | $83,001 ARS |
| Pasajeros unicos | 5,608 |
| Total noches vendidas | 75,741 |
| Promedio noches/reserva | 6.9 |

## Revenue por mercado
| Mercado | Reservas | Revenue | Ticket Promedio |
|---------|----------|---------|-----------------|
| Directo | 3,778 | $1,165,753,611 | $308,564 |
| Tour & Travel | 760 | $1,006,310,344 | $1,324,093 |
| OTAs | 1,372 | $383,286,394 | $279,363 |
| Corporativo | 556 | $286,744,150 | $515,727 |
| Mercado | 5 | $0 | $0 |

## Revenue por canal (origen)
| Canal | Reservas | Revenue | Ticket Promedio |
|-------|----------|---------|-----------------|
| Contacto Telefónico | 1,611 | $1,203,513,466 | $747,060 |
| WhatsApp | 1,231 | $466,675,967 | $379,103 |
| Mail | 469 | $426,173,500 | $908,686 |
| Booking.com | 1,372 | $383,286,394 | $279,363 |
| Walk In | 1,496 | $264,797,077 | $177,003 |
| Motor de reservas propio | 245 | $89,115,050 | $363,735 |
| Portal de reservas | 15 | $5,764,200 | $384,280 |
| Consulta | 7 | $1,120,000 | $160,000 |
| Instagram | 2 | $1,079,000 | $539,500 |
| Canal OTA | 3 | $389,844 | $129,948 |
| Sin Cargo / Complimentary | 15 | $180,000 | $12,000 |
| Origen | 5 | $0 | $0 |

## Revenue por mes
| Mes | Reservas | Revenue | Noches vendidas |
|-----|----------|---------|-----------------|
| 2025-09 | 371 | $43,473,307 | 774 |
| 2025-10 | 609 | $105,433,492 | 1,567 |
| 2025-11 | 941 | $257,778,092 | 3,508 |
| 2025-12 | 1,129 | $330,534,078 | 4,285 |
| 2026-01 | 1,370 | $979,259,221 | 9,556 |
| 2026-02 | 1,325 | $803,409,297 | 8,469 |
| 2026-03 | 593 | $212,513,025 | 3,409 |
| 2026-04 | 111 | $74,472,114 | 1,062 |
| 2026-05 | 10 | $16,221,873 | 255 |
| 2026-06 | 1 | $13,000,000 | 108 |
| 2026-09 | 6 | $6,000,000 | 1,054 |

## Top 20 ciudades de origen
| Ciudad | Reservas |
|--------|----------|
| Buenos Aires | 461 |
| Ciudad Autónoma de Buenos Aires | 228 |
| La Plata | 85 |
| Tandil | 47 |
| Lanús | 43 |
| Mar del Plata | 34 |
| Rosario | 28 |
| Santa Fe | 27 |
| Avellaneda | 26 |
| Necochea | 23 |
| Bahía Blanca | 22 |
| Olavarría | 22 |
| Tres Arroyos | 21 |
| Temperley | 14 |
| Lomas de Zamora | 14 |
| Vicente López | 13 |
| Quilmes | 13 |
| Córdoba | 13 |
| San Miguel de Tucumán | 12 |
| Azul | 11 |

## Estado de reservas
| Estado | Cantidad | % |
|--------|----------|---|
| C. Sin anticipo | 3,445 | 44.7% |
| C. Anticipo | 2,921 | 37.9% |
| Cancelada por el pasajero | 1,086 | 14.1% |
| No Show | 108 | 1.4% |
| Solicitud | 99 | 1.3% |
| Cancelada por falta de respuesta | 18 | 0.2% |
| Pago Rechazado | 14 | 0.2% |
| Estado | 5 | 0.1% |
| Reprogramada | 1 | 0.0% |

## Queries Dataview en vivo

### Huespedes VIP
```dataview
TABLE total_visitas as "Visitas", gasto_total as "Gasto", canal as "Canal", telefono as "Tel"
FROM "01 - Huespedes"
WHERE segmento = "VIP"
SORT gasto_total DESC
LIMIT 30
```

### Revenue por canal (vivo)
```dataview
TABLE
  length(rows) as "Reservas",
  sum(rows.gasto_total) as "Revenue Total"
FROM "01 - Huespedes"
WHERE tipo = "huesped"
GROUP BY mercado
SORT sum(rows.gasto_total) DESC
```
