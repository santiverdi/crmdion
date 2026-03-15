# Campana 01: Post-Estadia

> **Estado**: Lista para lanzar
> **Audiencia**: 1,318 huespedes (checkout ultimos 30 dias)
> **Objetivo**: Resena Google + cupon de retorno

## Mensaje WhatsApp (dia +1 post checkout)

```
Hola [NOMBRE]! 👋

Gracias por elegirnos en Hotel Dion.
Esperamos que hayas disfrutado tu estadia en Mar del Plata!

Nos ayudaria mucho si nos dejas tu opinion en Google:
[LINK GOOGLE REVIEWS]

Como agradecimiento, te regalamos un 10% OFF para tu proxima reserva directa.
Tu codigo: VUELVO10
Valido hasta [FECHA +90 dias]

Reserva directo aca: [LINK WEB]
O respondenos por aca mismo 😊

Hotel Dion - Mar del Plata
```

## Email de seguimiento (dia +3)

**Asunto**: [NOMBRE], tu opinion nos importa + regalo inside 🎁

```
Hola [NOMBRE],

Fue un placer tenerte en Hotel Dion.

Queremos seguir mejorando y tu opinion es clave.
¿Nos regalas 2 minutos?

👉 [BOTON: Dejar mi opinion en Google]

Como agradecimiento:
🎟️ 10% OFF en tu proxima reserva directa
📋 Codigo: VUELVO10

Reserva directo en [WEB] o escribinos al WhatsApp [NUMERO].
Siempre es mejor que Booking 😉

¡Hasta la proxima!
Equipo Hotel Dion
```

## Metricas a medir
- [ ] Tasa de apertura email (objetivo: >30%)
- [ ] Tasa de click en link resena (objetivo: >10%)
- [ ] Resenas generadas (objetivo: 50+/mes)
- [ ] Cupones canjeados (objetivo: 5-10%)

## Query Dataview - Audiencia

```dataview
TABLE email, telefono, ultima_visita, gasto_total, segmento
FROM "01 - Huespedes"
WHERE tipo = "huesped" AND ultima_visita >= "2026-02-08"
SORT ultima_visita DESC
```
