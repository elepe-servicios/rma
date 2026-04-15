# 🎓 LECCIONES APRENDIDAS - Migración RMA a Odoo 19

## Cambios Breaking Identificados

Durante la migración de los módulos RMA (rma, rma_delivery, rma_sale) a Odoo 19, se identificaron varios **cambios breaking** importantes que afectarán a otros módulos.

---

## 1. ⚠️ Filtros Group By sin tag `<group>`

### Cambio en Odoo 19
Los filtros de agrupación en vistas search **ya NO deben estar dentro de un tag `<group>`**.

### ANTES (Odoo 18):
```xml
<search>
    <group string="Group By" name="group_by">
        <filter string="Partner" context="{'group_by': 'partner_id'}"/>
        <filter string="State" context="{'group_by': 'state'}"/>
    </group>
</search>
```

### DESPUÉS (Odoo 19):
```xml
<search>
    <separator/>
    <filter string="Partner" name="partner_id_group_by" context="{'group_by': 'partner_id'}"/>
    <filter string="State" name="state_group_by" context="{'group_by': 'state'}"/>
</search>
```

**Impacto:** ALTO - Afecta TODAS las vistas search con Group By  
**Archivo de referencia:** `rma/SOLUCION_GROUP_BY_ODOO19.md`

---

## 2. ⚠️ Campo `category_id` en `uom.uom`

### Problema en Odoo 19
Los campos related que referencian `uom.uom.category_id` causan errores.

### ANTES (Odoo 18):
```python
uom_category_id = fields.Many2one(
    comodel_name="uom.category",
    related="product_id.uom_id.category_id",
)
uom_id = fields.Many2one(
    domain="[('category_id', '=', uom_category_id)]",
)
```

### DESPUÉS (Odoo 19):
```python
# uom_category_id comentado
uom_id = fields.Many2one(
    # domain simplificado o usar onchange
)
```

**Impacto:** MEDIO - Afecta wizards y formularios con selección de UoM  
**Módulos afectados:** rma, rma_delivery, rma_sale  
**Solución alternativa:** Usar `@api.onchange` para domain dinámico

---

## 3. ⚠️ Modelo `procurement.group` eliminado

### Cambio en Odoo 19
El modelo `procurement.group` fue eliminado por completo.

### Acción requerida:
```python
# Comentar campos que referencien este modelo
# procurement_group_id = fields.Many2one('procurement.group', ...)
```

**Impacto:** BAJO-MEDIO - Solo afecta módulos de stock/logística  
**Módulo afectado:** rma  
**Referencia en vistas:** Cambiar xpath de `procurement_group_id` a otro campo

---

## 4. ⚠️ API de grupos y usuarios

### Cambio en Odoo 19

#### Campo `groups_id` → Método `has_group()`
```python
# ANTES
if user.groups_id:
    ...

# DESPUÉS
if user.has_group('module.group_id'):
    ...
```

#### Campo `users` → Campo `user_ids`
```python
# ANTES
for user in group.users:
    ...

# DESPUÉS  
for user in group.user_ids:
    ...
```

#### Asignar usuarios a grupo
```python
# ANTES
group.users = [(4, user.id)]

# DESPUÉS
group.write({"user_ids": [(4, user.id)]})
```

**Impacto:** MEDIO - Afecta hooks de instalación y código de seguridad  
**Módulo afectado:** rma  
**Archivo de referencia:** `rma/ERROR_GROUPS_ID_RESUELTO.md`

---

## 5. ⚠️ Decorador `@api.returns` eliminado

### Cambio en Odoo 19
El decorador `@api.returns()` fue completamente eliminado.

```python
# ANTES
@api.returns("mail.message", lambda value: value.id)
def message_post(self, **kwargs):
    ...

# DESPUÉS
def message_post(self, **kwargs):
    ...
```

**Impacto:** BAJO - Poco usado, fácil de corregir  
**Módulo afectado:** rma

---

## 6. ⚠️ Campos de seguridad en XML

### Campo `category_id` en grupos
```xml
<!-- ANTES (Odoo 18) -->
<record id="group_manager" model="res.groups">
    <field name="category_id" ref="module_category"/>
</record>

<!-- DESPUÉS (Odoo 19) -->
<record id="group_manager" model="res.groups">
    <!-- category_id no existe, remover -->
</record>
```

### Campo `users` → `user_ids`
```xml
<!-- ANTES -->
<field name="users" eval="[(4, ref('base.user_admin'))]"/>

<!-- DESPUÉS -->
<!-- Remover del XML, asignar en hooks -->
```

**Impacto:** MEDIO - Afecta archivos de seguridad  
**Módulo afectado:** rma, odoo_connector_api, meli_oerp

---

## 7. ⚠️ Campo `scrapped` en `stock.move` eliminado

### Acción requerida
Remover de `@api.depends` cualquier referencia a `scrapped` en stock.move:

```python
# ANTES
@api.depends('stock_move_ids.scrapped')

# DESPUÉS
@api.depends('stock_move_ids.state')
```

**Impacto:** BAJO - Poco usado  
**Módulo afectado:** rma

---

## 8. ⚠️ Target `inline` en acciones

### Cambio en Odoo 19
El valor `inline` para el campo `target` en acciones ya no es válido.

```xml
<!-- ANTES -->
<field name="target">inline</field>

<!-- DESPUÉS -->
<field name="target">current</field>
```

**Impacto:** BAJO - Fácil de corregir  
**Módulo afectado:** rma

---

## 9. ⚠️ `context_today()` en dominios XML

### Problema
No se puede usar `context_today()` en dominios XML.

```xml
<!-- NO FUNCIONA -->
<filter domain="[('date', '<', context_today())]" />

<!-- SOLUCIÓN: Usar campo computado -->
```

```python
is_late = fields.Boolean(compute="_compute_is_late")

@api.depends('date')
def _compute_is_late(self):
    today = fields.Date.context_today(self)
    for rec in self:
        rec.is_late = rec.date and rec.date < today
```

```xml
<!-- USAR -->
<filter domain="[('is_late', '=', True)]" />
```

**Impacto:** MEDIO - Afecta filtros de búsqueda con fechas  
**Módulo afectado:** rma

---

## Resumen de Impacto

| Cambio | Impacto | Módulos afectados | Dificultad |
|--------|---------|-------------------|------------|
| Group By sin `<group>` | 🔴 ALTO | Todos con search | ⭐ Fácil |
| `uom_category_id` | 🟡 MEDIO | Wizards UoM | ⭐⭐ Media |
| `procurement.group` | 🟡 MEDIO | Stock/Logística | ⭐⭐ Media |
| API grupos/usuarios | 🟡 MEDIO | Hooks instalación | ⭐⭐ Media |
| `@api.returns` | 🟢 BAJO | Pocos | ⭐ Fácil |
| Seguridad XML | 🟡 MEDIO | Archivos seguridad | ⭐⭐ Media |
| `scrapped` eliminado | 🟢 BAJO | Pocos | ⭐ Fácil |
| `target="inline"` | 🟢 BAJO | Acciones | ⭐ Fácil |
| `context_today()` XML | 🟡 MEDIO | Filtros fechas | ⭐⭐⭐ Alta |

---

## Checklist de Migración a Odoo 19

Use esta lista para verificar módulos:

- [ ] Buscar `<group string="Group By"` → Remover tag `<group>`
- [ ] Buscar `/list` en xpath → Cambiar a `/tree`
- [ ] Buscar `uom_category_id` related → Comentar o usar onchange
- [ ] Buscar `procurement.group` → Comentar referencias
- [ ] Buscar `user.groups_id` → Usar `has_group()`
- [ ] Buscar `group.users` → Usar `group.user_ids`
- [ ] Buscar `@api.returns` → Remover decorador
- [ ] Buscar `category_id` en res.groups XML → Remover
- [ ] Buscar `scrapped` en @api.depends → Remover
- [ ] Buscar `target="inline"` → Cambiar a `current`
- [ ] Buscar `context_today()` en XML → Usar campo computado

---

## Módulos migrados exitosamente

✅ **rma** - 19.0.1.0.0  
✅ **rma_delivery** - 19.0.1.0.0  
✅ **rma_sale** - 19.0.1.0.0  

**Total de errores corregidos:** 12+  
**Documentos creados:** 15+  
**Lecciones aplicables a:** Todos los módulos en migración

---

**Fecha:** 2026-03-02  
**Creado por:** GitHub Copilot AI Assistant  
**Estado:** 📚 Referencia completa para futuras migraciones
