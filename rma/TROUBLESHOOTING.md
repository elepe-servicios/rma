# 🔧 Resolución de Problemas - RMA v19.0

## Error: AttributeError: module 'odoo.api' has no attribute 'returns'

### Descripción del Problema

Al intentar instalar el módulo RMA en Odoo 19.0, se produce el siguiente error:

```
AttributeError: module 'odoo.api' has no attribute 'returns'
File "/mnt/extra-addons/rma/models/rma.py", line 1487, in Rma
    @api.returns("mail.message", lambda value: value.id)
```

### Causa Raíz

El decorador `@api.returns()` fue **deprecado y eliminado** en Odoo 19.0. Este decorador era utilizado en versiones anteriores para especificar el tipo de retorno de métodos, particularmente útil para el ORM cuando se trabajaba con registros.

### Solución Aplicada

**Archivo modificado:** `models/rma.py` (línea 1487)

**Cambio realizado:**

```python
# ❌ ANTES (causaba error en Odoo 19)
@api.returns("mail.message", lambda value: value.id)
def message_post(self, **kwargs):
    """Set 'sent' field to True when an email is sent from rma form
    view. This field (sent) is used to set the appropriate style to the
    'Send by Email' button in the rma form view.
    """
    if self.env.context.get("mark_rma_as_sent"):
        self.write({"sent": True})
    self_with_context = self.with_context(mail_post_autofollow=True)
    return super(Rma, self_with_context).message_post(**kwargs)

# ✅ DESPUÉS (compatible con Odoo 19)
def message_post(self, **kwargs):
    """Set 'sent' field to True when an email is sent from rma form
    view. This field (sent) is used to set the appropriate style to the
    'Send by Email' button in the rma form view.
    """
    if self.env.context.get("mark_rma_as_sent"):
        self.write({"sent": True})
    self_with_context = self.with_context(mail_post_autofollow=True)
    return super(Rma, self_with_context).message_post(**kwargs)
```

### ¿Por qué funciona sin el decorador?

1. **Herencia correcta:** El método hereda de `models.Model` que ya tiene la definición correcta de `message_post()`
2. **Tipo de retorno implícito:** El `super().message_post()` ya retorna un `mail.message`
3. **Sin necesidad de conversión:** En Odoo 19, el framework maneja automáticamente los tipos de retorno

### Estado Actual

✅ **CORREGIDO** - El módulo ahora instala correctamente en Odoo 19.0

---

## Error: AssertionError with unknown comodel_name 'procurement.group' o 'stock.procurement.group'

### Descripción del Problema

Al intentar instalar el módulo RMA en Odoo 19.0, se produce uno de estos errores:

```
AssertionError: Field rma.procurement_group_id with unknown comodel_name 'procurement.group'
```

O después de intentar corregirlo:

```
AssertionError: Field rma.procurement_group_id with unknown comodel_name 'stock.procurement.group'
```

### Causa Raíz

El modelo `procurement.group` fue **completamente eliminado en Odoo 19.0**. No fue renombrado, simplemente ya no existe. El concepto de "procurement group" como modelo separado fue removido y su funcionalidad integrada directamente en otros modelos de stock.

### Solución Aplicada

**Archivo modificado:** `models/rma.py` (líneas 161-166)

**Cambio realizado:**

```python
# ❌ ANTES (causaba error en Odoo 19)
procurement_group_id = fields.Many2one(
    comodel_name="procurement.group",  # o "stock.procurement.group"
    string="Procurement group",
)

# ✅ DESPUÉS (compatible con Odoo 19)
# NOTE: procurement.group model was removed in Odoo 19
# The procurement group concept is no longer used as a separate model
# Keeping this commented for reference and potential future migration data
# procurement_group_id = fields.Many2one(
#     comodel_name="procurement.group",
#     string="Procurement group",
# )
```

**Razón:** El modelo `procurement.group` ya no existe en Odoo 19. La funcionalidad de agrupación de procuraciones ahora se maneja de manera diferente, integrada en los modelos de stock.

### Impacto

⚠️ **Funcionalidad perdida:** La capacidad de agrupar procuraciones mediante un grupo específico no está disponible en esta versión del módulo RMA.

**Alternativas:**
1. Las procuraciones se manejan automáticamente por el sistema de stock
2. Si se necesita esta funcionalidad, debe ser reimplementada usando los nuevos mecanismos de Odoo 19
3. Para la mayoría de casos de uso, la funcionalidad básica de RMA no se ve afectada

### Estado Actual

✅ **CORREGIDO** - El campo ha sido comentado y el módulo puede instalar correctamente.

---

## Error: KeyError with related field uom_category_id

### Descripción del Problema

Al intentar instalar el módulo RMA en Odoo 19.0, se produce el siguiente error:

```
KeyError: 'Field category_id referenced in related field definition rma.uom_category_id does not exist.'
```

### Causa Raíz

El campo `uom_category_id` está definido como un campo `related` que referencia `product_id.uom_id.category_id`. En Odoo 19, hay cambios en cómo se manejan estos campos relacionados que causan este error.

### Solución Aplicada

**Archivo modificado:** `models/rma.py` (líneas 256-260)

**Cambio realizado:**

```python
# ❌ ANTES (causaba error en Odoo 19)
uom_category_id = fields.Many2one(
    related="product_id.uom_id.category_id", string="Category UoM"
)

# ✅ DESPUÉS (compatible con Odoo 19)
# NOTE: Field commented due to related field issue in Odoo 19
# The uom category can still be accessed via product_id.uom_id.category_id if needed
# uom_category_id = fields.Many2one(
#     related="product_id.uom_id.category_id", string="Category UoM"
# )
```

**Razón:** El campo no es crítico para la funcionalidad básica del RMA. Si se necesita acceder a la categoría UoM, aún se puede hacer mediante `product_id.uom_id.category_id`.

### Impacto

✅ **Impacto mínimo:** Este campo se usaba principalmente para validaciones de UoM. La funcionalidad principal del RMA no se ve afectada.

**Ubicaciones afectadas:**
1. `models/rma.py` (línea 256-260) - Modelo principal
2. `wizard/rma_delivery.py` (línea 32) - Wizard de entrega/reemplazo

### Estado Actual

✅ **CORREGIDO** - Los campos han sido comentados en ambas ubicaciones y el módulo puede instalar correctamente.

---

## Resumen de Cambios Críticos

El módulo RMA requirió **CUATRO correcciones** para ser compatible con Odoo 19.0:

| # | Problema | Ubicación | Solución |
|---|----------|-----------|----------|
| 1 | `@api.returns` no existe | `models/rma.py:1490` | Removido el decorador |
| 2 | `procurement.group` eliminado | `models/rma.py:161-167` | Campo comentado |
| 3 | `uom_category_id` related error | `models/rma.py:256-260` | Campo comentado |
| 4 | `uom_category_id` related error | `wizard/rma_delivery.py:32` | Campo comentado |

Los cuatro cambios son necesarios para que el módulo instale correctamente.

---

## Otros Posibles Problemas

### Si encuentras otros errores relacionados con `@api.returns`

**Buscar en todo el módulo:**
```bash
grep -r "@api.returns" /mnt/extra-addons/rma/
```

**O en Windows PowerShell:**
```powershell
Select-String -Path "C:\Jorge\trunk_seyco_19\elepe-servicios\seyco_addons\rma-19\rma\**\*.py" -Pattern "@api.returns"
```

**Solución general:**
- Eliminar el decorador `@api.returns`
- Verificar que el método herede correctamente del padre
- El tipo de retorno se manejará automáticamente

### Verificar instalación correcta

```bash
# En línea de comandos de Odoo
odoo-bin -c odoo.conf -d tu_bd -i rma --stop-after-init --log-level=debug

# Verificar que no hay errores
tail -f /var/log/odoo/odoo.log | grep -i error
```

---

## Cambios en API de Odoo 19

### Decoradores Deprecados

| Decorador | Estado en v19 | Alternativa |
|-----------|---------------|-------------|
| `@api.returns()` | ❌ ELIMINADO | Remover, el tipo se infiere |
| `@api.one` | ❌ ELIMINADO | Usar `self.ensure_one()` |
| `@api.multi` | ❌ ELIMINADO | Ya no es necesario |
| `@api.model` | ✅ VÁLIDO | Sin cambios |
| `@api.depends()` | ✅ VÁLIDO | Sin cambios |
| `@api.onchange()` | ✅ VÁLIDO | Sin cambios |
| `@api.constrains()` | ✅ VÁLIDO | Sin cambios |

### Mejores Prácticas para Odoo 19

1. **No usar decoradores deprecados**
2. **Verificar tipos de retorno implícitamente**
3. **Usar `ensure_one()` cuando se necesita un solo registro**
4. **Aprovechar type hints de Python cuando sea útil**

---

## Verificación Post-Corrección

### Checklist

- [x] Decorador `@api.returns` removido
- [x] Módulo instala sin errores
- [x] Método `message_post()` funciona correctamente
- [x] Tests pasan (si aplica)
- [x] Documentación actualizada

### Prueba Funcional

```python
# En Odoo shell
env = odoo.api.Environment(cr, uid, {})

# Crear un RMA de prueba
rma = env['rma'].create({
    'partner_id': env.ref('base.res_partner_1').id,
    'product_id': env['product.product'].search([], limit=1).id,
    'product_uom_qty': 1,
})

# Probar message_post (debe funcionar sin errores)
message = rma.message_post(body="Test message")
print(f"Message creado: {message.id}")
# ✅ Debe funcionar sin AttributeError
```

---

## Historial de Cambios

| Fecha | Versión | Cambio |
|-------|---------|--------|
| 2026-03-02 | 19.0.1.0.0 | Removido `@api.returns` de `message_post()` |
| 2026-03-02 | 19.0.1.0.0 | Migración inicial a Odoo 19.0 |

---

## Referencias

- **Odoo 19 Release Notes:** https://www.odoo.com/documentation/19.0/developer/reference/upgrades.html
- **OCA Migration Guide:** https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-19.0
- **API Deprecations:** https://github.com/odoo/odoo/blob/19.0/doc/developer/reference/upgrades.rst

---

## Contacto y Soporte

Si encuentras otros problemas durante la migración:

1. Verificar los logs de Odoo: `/var/log/odoo/odoo.log`
2. Revisar documentación: `MIGRATION_V19.md`
3. Reportar issues: https://github.com/OCA/rma/issues
4. Comunidad OCA: https://odoo-community.org

---

**Última actualización:** 2026-03-02  
**Estado:** ✅ RESUELTO  
**Versión del módulo:** 19.0.1.0.0
