# PLAN DE ENVIO MASIVO SIN BAN

## Estrategia hibrida recomendada

```
PASO 1: Email masivo (gratis, sin riesgo)
   → El huesped recibe mail con boton "Escribime por WhatsApp"
   → El que hace click, TE ESCRIBE A VOS
   → Ya queda habilitada la conversacion

PASO 2: WhatsApp solo a los que YA te tienen agendado
   → Broadcast a huespedes recientes (ultimos 30 dias)
   → Estos si te tienen guardado porque se comunicaron al reservar

PASO 3: WhatsApp API (si queres escalar)
   → Para llegar a los que NO te tienen guardado
   → Pago por mensaje pero legal y seguro
```

---

## PASO 1: Email masivo con Brevo (ARRANCAR HOY)

### Crear cuenta
1. Ir a **brevo.com** (ex Sendinblue)
2. Crear cuenta gratuita
3. Plan Free = 300 emails/dia (en 19 dias cubriste los 5,480 contactos)

### Importar contactos
1. Subir `MASTER_huespedes.csv` desde `07 - Campanas/`
2. Crear listas por segmento:
   - Lista "Post-estadia" (1,318)
   - Lista "Booking" (1,341)
   - Lista "VIPs" (135)
   - Lista "Familias" (192)
   - Lista "Corporativos" (469)
   - Lista "Primera vez" (2,499)

### Email #1: Post-estadia (PRIORIDAD 1)

**Para**: Lista post-estadia (1,318 contactos)
**Envio**: 300/dia x 5 dias

**Asunto**: ¿Como la pasaste en Hotel Dion? 🏨

**Cuerpo**:
```
Hola {{nombre}},

Gracias por tu estadia en Hotel Dion!
Esperamos que hayas disfrutado Mar del Plata.

¿Nos ayudas con una reseña rapida?
👉 [BOTON: Dejar reseña en Google]

Como agradecimiento, te damos 10% OFF
en tu proxima reserva directa.

¿Queres reservar? Escribinos directo:
👉 [BOTON: Hablar por WhatsApp]

¡Hasta la proxima!
Equipo Hotel Dion
```

**Importante**: El boton de WhatsApp es un link:
`https://wa.me/54XXXXXXXXXX?text=Hola!%20Estuve%20en%20Hotel%20Dion%20y%20quiero%20consultar%20disponibilidad`

Cuando hacen click, ELLOS te escriben a vos. Sin riesgo de ban.

### Email #2: Booking a Directo (PRIORIDAD 2)

**Para**: Lista Booking (1,341 contactos)
**Envio**: Despues de terminar el #1

**Asunto**: {{nombre}}, la proxima vez paga menos que en Booking

**Cuerpo**:
```
Hola {{nombre}},

La ultima vez reservaste Hotel Dion por Booking.
Nos encanto tenerte!

Pero sabias que reservando DIRECTO
siempre pagas MENOS?

Booking nos cobra comision del 15%.
Ese ahorro te lo pasamos a vos: hasta 10% menos.

Ademas por reserva directa:
✅ Mejor habitacion disponible
✅ Late checkout (sujeto a dispo)
✅ Atencion directa por WhatsApp

👉 [BOTON: Reservar directo - Mejor precio]
👉 [BOTON: Consultar por WhatsApp]

Hotel Dion ⭐⭐⭐ - Mar del Plata
```

### Email #3: Reactivacion general (PRIORIDAD 3)

**Para**: Primera vez alto gasto (2,499)
**Asunto**: {{nombre}}, te extrañamos en Hotel Dion

**Cuerpo**:
```
Hola {{nombre}},

Ya paso un tiempo desde tu visita a Hotel Dion.
Mar del Plata siempre tiene algo lindo para ofrecer.

Tenemos un beneficio exclusivo para vos:
🎟️ 15% OFF en tu proxima reserva directa

Solo hasta [FECHA].

👉 [BOTON: Quiero reservar con descuento]
👉 [BOTON: Consultar por WhatsApp]

Te esperamos!
Hotel Dion - Mar del Plata
```

---

## PASO 2: WhatsApp Broadcast (solo a recientes)

### Quienes SI te tienen agendado (seguro mandar):
- Huespedes ultimos 30 dias que se comunicaron por WhatsApp
- VIPs que ya chatean con ustedes
- Cualquiera que les haya escrito antes

### Como hacerlo seguro:
1. WhatsApp Business App > Listas de difusion > Nueva lista
2. Agregar SOLO contactos que te tienen guardado
3. Maximo 256 por lista
4. No mandar mas de 2-3 listas por dia
5. Espaciar los envios (no todo junto)
6. Si ves que baja el "delivery rate", PARAR

### Filtro practico:
De los 1,318 post-estadia, filtrar los que reservaron por WhatsApp:

**Estos son seguros** (te contactaron por WA, te tienen guardado):
- Canal "WhatsApp": ~400 personas aprox
- Son tu primera tanda de broadcast

---

## PASO 3: WhatsApp API (para escalar - semana 3+)

### Si queres llegar a TODOS por WhatsApp:

**Opcion recomendada: Callbell o WATI**

| Caracteristica | Callbell | WATI |
|---------------|----------|------|
| WhatsApp + IG + Email | Si | Solo WA |
| Multiagente | Si (tu equipo) | Si |
| Templates aprobados | Si | Si |
| Broadcast masivo | Si | Si |
| Precio base | USD 15/mes | USD 40/mes |
| Costo por mensaje | ~USD 0.05 | ~USD 0.05 |
| Idioma | Español | Ingles |

**Proceso**:
1. Crear cuenta en Callbell/WATI
2. Verificar numero de WhatsApp Business
3. Crear template de mensaje (Meta lo aprueba en 24-48hs)
4. Importar contactos del CSV
5. Enviar broadcast oficial

**Template ejemplo para aprobacion de Meta**:
```
Hola {{1}}! De Hotel Dion, Mar del Plata.
Gracias por tu estadia con nosotros.
Tenemos una oferta especial para tu proxima visita.
¿Te interesa? Respondenos y te contamos!
```

---

## CRONOGRAMA REAL

| Dia | Accion | Costo |
|-----|--------|-------|
| Hoy | Crear cuenta Brevo + importar CSV | $0 |
| Hoy | Disenar email #1 (post-estadia) | $0 |
| Manana | Empezar envio email #1 (300/dia) | $0 |
| Dia 3 | WhatsApp broadcast a los que vinieron por WA | $0 |
| Dia 5 | Medir resultados: emails abiertos + WA recibidos | - |
| Dia 6 | Empezar email #2 (Booking) | $0 |
| Semana 2 | Evaluar si vale la pena Callbell/WATI | ~USD 15/mes |
| Semana 2 | Armar perfil Google Business + pedir resenas | $0 |
| Semana 3 | Instagram: contenido + link a WhatsApp | $0 |

## Resultado esperado (mes 1)
- 5,480 emails enviados
- ~30% aperturas = 1,644 personas leen tu mail
- ~10% click en WhatsApp = 164 personas te escriben
- ~5% de esos reservan = 8 reservas nuevas directas
- + resenas de Google incrementan busquedas organicas
- + WhatsApp broadcast suma otras ~50-100 conversaciones

**164 personas escribiendote al WhatsApp el primer mes, con costo $0.**
A medida que sumas Instagram y API, escala a 500+/mes.
