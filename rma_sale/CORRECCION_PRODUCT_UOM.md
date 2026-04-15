# ✅ CORRECCIÓN - Campo product_uom en sale.order.line

## Problema

Al intentar crear un RMA desde una orden de venta, se producía el siguiente error:

```
AttributeError: 'sale.order.line' object has no attribute 'product_uom'. Did you mean: 'product_id'?
```

**Error completo:**
```python
File "/mnt/extra-addons/rma_sale/models/sale.py", line 178, in prepare_sale_rma_data
    "uom": self.product_uom,
           ^^^^^^^^^^^^^^^^
AttributeError: 'sale.order.line' object has no attribute 'product_uom'
```

---

## Causa

En Odoo 19, el campo `product_uom` en el modelo `sale.order.line` fue **renombrado a `product_uom_id`**.

Este es un cambio de nomenclatura estándar para campos Many2one en Odoo, donde se agrega el sufijo `_id`.

---

## Solución Aplicada

**Archivo modificado:** `models/sale.py` (línea 178)

### ANTES (Odoo 18):
```python
data.append(
    {
        "product": product,
        "quantity": self.qty_delivered,
        "uom": self.product_uom,  # ❌ No existe en Odoo 19
        "picking": False,
        "sale_line_id": self,
    }
)
```

### DESPUÉS (Odoo 19):
```python
data.append(
    {
        "product": product,
        "quantity": self.qty_delivered,
        # NOTE: product_uom renamed to product_uom_id in Odoo 19
        "uom": self.product_uom_id,  # ✅ Correcto
        "picking": False,
        "sale_line_id": self,
    }
)
```

---

## ⚠️ Nota Importante

**NO confundir con `stock.move`:**

En el modelo `stock.move`, el campo sigue siendo `product_uom` (sin el sufijo `_id`):

```python
# ✅ CORRECTO en stock.move (Odoo 19)
uom = move.product_uom  # Sin _id
qty = move.product_uom_qty

# ✅ CORRECTO en sale.order.line (Odoo 19)
uom = line.product_uom_id  # Con _id
qty = line.product_uom_qty
```

Esta inconsistencia es normal en Odoo, donde algunos modelos legacy mantienen nombres de campo sin `_id`.

---

## Impacto

✅ **Funcionalidad restaurada:**
- Creación de RMAs desde órdenes de venta funciona correctamente
- El UoM se captura correctamente para el RMA
- Sin pérdida de funcionalidad

⚠️ **Cambio breaking:**
- Afecta cualquier módulo que acceda a `sale.order.line.product_uom`
- Fácil de detectar: causa AttributeError inmediato
- Fácil de corregir: simplemente agregar `_id` al final

---

## Otros campos afectados

Este cambio de nomenclatura puede afectar otros campos Many2one en `sale.order.line`. Campos comunes:

| Campo Odoo 18 | Campo Odoo 19 | Verificar |
|---------------|---------------|-----------|
| `product_uom` | `product_uom_id` | ✅ Confirmado |
| Otros campos Many2one | Revisar según contexto | ⚠️ Posible |

---

## Cómo detectar

**Búsqueda en código:**
```bash
# Buscar posibles problemas
grep -r "\.product_uom[^_]" --include="*.py" your_module/
```

**Síntomas:**
- AttributeError al trabajar con líneas de venta
- Error menciona `'sale.order.line' object has no attribute 'product_uom'`
- Ocurre al crear/procesar RMAs desde órdenes de venta

---

## Estado

✅ **Corrección aplicada**  
✅ **Funcionalidad probada** - Creación de RMA desde OV funciona  
✅ **Documentación actualizada** en `LECCIONES_APRENDIDAS_ODOO19.md`

---

## Verificación

Para verificar que la corrección funciona:

1. Ir a **Ventas** → Órdenes de venta
2. Abrir una orden confirmada con productos entregados
3. Click en el botón **"Create RMA"**
4. ✅ El wizard debe abrirse sin errores
5. ✅ Los productos deben mostrarse con sus UoM correctos

---

**Fecha:** 2026-03-02  
**Archivo modificado:** `models/sale.py`  
**Línea corregida:** 178  
**Cambio:** `product_uom` → `product_uom_id`  
**Estado:** ✅ RESUELTO
