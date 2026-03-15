# Finanzas

## Estructura de costos
| Categoria | Subcategoria | Monto mensual | Tipo |
|-----------|-------------|---------------|------|
| Personal | Recepcion |  | Fijo |
| Personal | Housekeeping |  | Fijo |
| Personal | Mantenimiento |  | Fijo |
| Personal | Administracion |  | Fijo |
| Servicios | Luz |  | Variable |
| Servicios | Gas |  | Variable |
| Servicios | Agua |  | Variable |
| Servicios | Internet/TV |  | Fijo |
| Servicios | Telefono |  | Fijo |
| Insumos | Amenities |  | Variable |
| Insumos | Blanqueria |  | Variable |
| Insumos | Limpieza |  | Variable |
| Insumos | Desayuno |  | Variable |
| Comisiones | Booking (15-18%) |  | Variable |
| Comisiones | Despegar |  | Variable |
| Comisiones | Pasarela de pago |  | Variable |
| Impuestos | IIBB |  | Variable |
| Impuestos | Tasa municipal |  | Fijo |
| Marketing | Publicidad online |  | Variable |
| Marketing | Web/dominio |  | Fijo |
| Mantenimiento | Reparaciones |  | Variable |
| Seguros | Seguro hotel |  | Fijo |

## Metricas clave
- **ADR** (Average Daily Rate): Ingreso promedio por habitacion ocupada
- **RevPAR** (Revenue Per Available Room): Ingreso por habitacion disponible
- **GOPPAR**: Ganancia operativa bruta por habitacion disponible
- **Costo por habitacion ocupada**: Total gastos variables / habitaciones vendidas
- **Break-even**: Cuantas habitaciones necesitas vender para cubrir costos fijos

## Rentabilidad por canal
```dataview
TABLE
  sum(total) as "Revenue Bruto",
  canal as "Canal"
FROM "02 - Reservas"
WHERE tipo = "reserva"
GROUP BY canal
```

> **Nota**: A Booking restarle 15-18% de comision para ver revenue neto real.
> Una reserva directa de $50.000 vale mas que una de Booking de $60.000.
