# Bot WhatsApp / Instagram

## Flujos automaticos

### 1. Consulta de disponibilidad
```
Usuario: "Tienen disponibilidad para el 15 de enero?"
Bot: "Hola! Para el 15/01 tenemos disponibilidad.
      Cuantas noches y cuantas personas serian?"
Usuario: "3 noches, 2 adultos y 1 nene"
Bot: "Perfecto! Tenemos:
      - Habitacion Triple: $XX.XXX/noche
      - Suite Familiar: $XX.XXX/noche
      Ambas incluyen desayuno. Queres que te reserve?"
```

### 2. Post-estadia automatico
```
Bot (dia +1): "Hola [nombre]! Gracias por hospedarte con nosotros.
              Nos ayudas con una resena en Google? [link]
              Como agradecimiento, te damos 10% en tu proxima reserva directa.
              Codigo: VUELVO10"
```

### 3. Reactivacion
```
Bot (dia +90): "Hola [nombre]! Ya pasaron unos meses desde tu visita.
               Tenemos una promo especial para vos: 15% OFF reservando directo.
               Valido hasta [fecha]. Reserva aca: [link web]"
```

### 4. FAQ automatico
- Horarios check-in/check-out
- Estacionamiento
- Desayuno incluido
- Distancia a la playa
- Mascotas
- Formas de pago

## Herramientas posibles
- **Baileys** (WhatsApp Web API - gratis, no oficial)
- **WhatsApp Business API** (oficial, pago por mensaje)
- **ManyChat** (Instagram + WhatsApp)
- **Chatwoot** (open source, multicanal)
