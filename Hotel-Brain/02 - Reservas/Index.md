# Reservas

## Pipeline activo
```dataview
TABLE
  pasajero as "Pasajero",
  llegada as "Llegada",
  salida as "Salida",
  noches as "Noches",
  canal as "Canal",
  total as "Total"
FROM "02 - Reservas"
WHERE tipo = "reserva"
SORT llegada DESC
LIMIT 50
```
