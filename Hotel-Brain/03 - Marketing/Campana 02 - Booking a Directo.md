# Campana 02: Booking -> Directo

> **Estado**: Lista para lanzar
> **Audiencia**: 1,341 huespedes que reservaron por Booking.com
> **Objetivo**: Que la proxima vez reserven directo
> **Ahorro potencial**: $11.9M ARS en comisiones

## Por que esta campana es clave

Booking cobra 15-18% de comision. En una reserva de $300.000:
- **Via Booking**: Vos recibis $255.000 (Booking se queda $45.000)
- **Directo con 10% OFF**: El huesped paga $270.000, vos recibis $270.000

**Todos ganan**: el huesped paga menos, vos cobras mas.

## Mensaje WhatsApp

```
Hola [NOMBRE]! Soy [RECEPCIONISTA] de Hotel Prince 🏨

Vimos que nos elegiste por Booking para tu estadia en Mar del Plata.
¡Gracias por confiar en nosotros!

Queremos contarte que reservando DIRECTO con nosotros:
✅ Pagas hasta 10% menos que en Booking
✅ Mejor habitacion disponible
✅ Late checkout gratis (sujeto a disponibilidad)
✅ Atencion directa por WhatsApp

Para tu proxima visita, reserva aca: [LINK WEB]
O simplemente escribinos y te cotizamos 😊

Hotel Prince - Mar del Plata
Tel: [NUMERO] | Web: [WEB]
```

## Email

**Asunto**: [NOMBRE], la proxima vez ahorra reservando directo

```
Hola [NOMBRE],

La ultima vez reservaste en Hotel Prince a traves de Booking.
Nos encanto tenerte!

Pero queremos contarte un secreto:
Reservando DIRECTO siempre conseguis mejor precio.

¿Por que?
Booking nos cobra una comision del 15-18%.
Ese ahorro te lo pasamos a vos.

BENEFICIOS EXCLUSIVOS por reserva directa:
• Hasta 10% menos que Booking
• Mejor habitacion disponible
• Late checkout (sujeto a disponibilidad)
• Cancelacion flexible
• Atencion personalizada por WhatsApp

👉 [BOTON: Reservar directo]
👉 O escribinos al WhatsApp: [NUMERO]

¡Te esperamos de nuevo!
Equipo Hotel Prince
```

## Segmentacion dentro de Booking

### Alta prioridad (alto gasto)
```dataview
TABLE email, telefono, gasto_total, total_visitas, ciudad
FROM "01 - Huespedes"
WHERE canal = "Booking.com" AND gasto_total > 300000
SORT gasto_total DESC
```

### Recurrentes de Booking (ya volvieron, convertirlos!)
```dataview
TABLE email, telefono, gasto_total, total_visitas
FROM "01 - Huespedes"
WHERE canal = "Booking.com" AND total_visitas >= 2
SORT total_visitas DESC
```

## Metricas
- [ ] Emails/WhatsApp enviados
- [ ] Tasa de apertura
- [ ] Reservas directas de ex-Booking (objetivo: 20% conversion)
- [ ] Revenue directo ganado
- [ ] Comisiones ahorradas
