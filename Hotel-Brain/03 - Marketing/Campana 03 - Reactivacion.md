# Campana 03: Reactivacion "Volve al Prince"

> **Estado**: Programar para abril
> **Audiencia**: 5,019 huespedes de primera vez
> **Objetivo**: Convertir primera vez en recurrente

## Mensaje WhatsApp (90 dias post checkout)

```
Hola [NOMBRE]! 🏖️

¿Te acordas de tu estadia en Hotel Prince?
Ya pasaron unos meses y queremos verte de nuevo.

Tenemos algo especial para vos:
🎟️ 15% OFF en tu proxima reserva directa
📅 Valido para cualquier fecha hasta diciembre 2026

Reserva aca: [LINK WEB]
O escribinos y te armamos la mejor propuesta.

¡Mar del Plata siempre te espera!
Hotel Prince 🌊
```

## Para Semana Santa (familias)

```
Hola [NOMBRE]! 🐰

Se viene Semana Santa y Mar del Plata es el plan perfecto.

En Hotel Prince tenemos:
🏨 Habitaciones familiares
🥐 Desayuno incluido
📍 A cuadras del centro y la playa
💰 Precio especial: desde $[PRECIO]/noche reservando directo

Semana Santa: 28 marzo al 6 abril
⚡ Pocas habitaciones disponibles

Reserva: [LINK] o respondenos aca.

Hotel Prince - Mar del Plata
```

## Para vacaciones de invierno

```
Hola [NOMBRE]! ❄️

Las vacaciones de invierno son mejor frente al mar.
Mar del Plata en julio tiene su magia.

En Hotel Prince:
🏨 Habitaciones calefaccionadas
🥐 Desayuno buffet incluido
💰 Tarifa invierno desde $[PRECIO]/noche
🎟️ Promo especial: 4 noches al precio de 3

Reserva directo: [LINK]
O escribinos por aca.

¡Te esperamos!
Hotel Prince 🌊
```

## Query - Primera vez que no volvieron
```dataview
TABLE email, telefono, gasto_total, primera_visita, ciudad, tipo_viajero
FROM "01 - Huespedes"
WHERE segmento = "Primera vez" AND email != ""
SORT gasto_total DESC
LIMIT 50
```
