# Validación Post-Migración RMA v19.0

## 🎯 Objetivo
Este documento guía la validación completa del módulo RMA después de la migración a Odoo 19.0.

---

## ✅ Validación Técnica

### 1. Instalación del Módulo

```bash
# Actualizar lista de módulos
odoo-bin -c odoo.conf -d test_db --update=all --stop-after-init

# Instalar RMA
odoo-bin -c odoo.conf -d test_db -i rma --stop-after-init
```

**Verificar:**
- [ ] Instalación sin errores
- [ ] Logs sin warnings críticos
- [ ] Post-init hook ejecutado correctamente

### 2. Verificación de Base de Datos

```sql
-- Conectar a PostgreSQL
psql -d test_db

-- Verificar tablas creadas
SELECT tablename FROM pg_tables 
WHERE tablename LIKE 'rma%' 
ORDER BY tablename;

-- Resultado esperado:
-- rma
-- rma_finalization
-- rma_operation
-- rma_tag
-- rma_team
-- ... (más tablas relacionadas)

-- Verificar secuencias
SELECT sequence_name FROM information_schema.sequences 
WHERE sequence_name LIKE '%rma%';

-- Verificar índices
SELECT indexname, tablename 
FROM pg_indexes 
WHERE tablename LIKE 'rma%';
```

**Verificar:**
- [ ] Todas las tablas creadas
- [ ] Índices en campos clave
- [ ] Foreign keys configuradas
- [ ] Secuencias por empresa

### 3. Verificación de Modelos

```python
# En Odoo shell: odoo-bin shell -d test_db
env = odoo.api.Environment(cr, uid, {})

# Verificar modelo RMA
rma_model = env['rma']
print(f"Modelo RMA: {rma_model}")
print(f"Campos: {len(rma_model._fields)}")

# Verificar otros modelos
models = ['rma.operation', 'rma.team', 'rma.finalization', 'rma.tag']
for model_name in models:
    model = env[model_name]
    count = model.search_count([])
    print(f"{model_name}: {count} registros")
```

**Verificar:**
- [ ] Todos los modelos accesibles
- [ ] Campos definidos correctamente
- [ ] Relaciones entre modelos

### 4. Verificación de Vistas

```python
# Verificar vistas principales
views = [
    'rma.rma_view_form',
    'rma.rma_view_tree',
    'rma.rma_view_search',
    'rma.rma_view_kanban',
    'rma.portal_my_rmas',
    'rma.rma_team_view_form',
    'rma.rma_operation_view_form',
]

for view_ref in views:
    try:
        view = env.ref(view_ref)
        print(f"✅ {view_ref}: {view.name}")
    except Exception as e:
        print(f"❌ {view_ref}: ERROR - {e}")
```

**Verificar:**
- [ ] Todas las vistas existen
- [ ] Sin errores de XML
- [ ] Vistas renderizables

### 5. Verificación de Seguridad

```python
# Verificar grupos de acceso
groups = env['res.groups'].search([('name', 'like', 'RMA')])
for group in groups:
    print(f"Grupo: {group.name}")
    print(f"  Usuarios: {len(group.users)}")
    print(f"  Categoría: {group.category_id.name}")

# Verificar reglas de registro
rules = env['ir.rule'].search([('model_id.model', 'like', 'rma')])
for rule in rules:
    print(f"Regla: {rule.name}")
    print(f"  Modelo: {rule.model_id.model}")
    print(f"  Dominio: {rule.domain_force}")
```

**Verificar:**
- [ ] Grupos creados (RMA User, RMA Manager)
- [ ] Reglas de registro aplicadas
- [ ] Permisos configurados correctamente

### 6. Verificación de Datos Iniciales

```python
# Verificar operaciones predefinidas
operations = env['rma.operation'].search([])
print(f"Operaciones RMA: {len(operations)}")
for op in operations:
    print(f"  - {op.name} ({op.code})")

# Verificar configuración de almacén
warehouses = env['stock.warehouse'].search([])
for wh in warehouses:
    print(f"\nAlmacén: {wh.name}")
    print(f"  Ubicación RMA: {wh.rma_loc_id.name if wh.rma_loc_id else 'NO CREADA'}")
    print(f"  Tipo entrada: {wh.rma_in_type_id.name if wh.rma_in_type_id else 'NO CREADO'}")
    print(f"  Tipo salida: {wh.rma_out_type_id.name if wh.rma_out_type_id else 'NO CREADO'}")
```

**Verificar:**
- [ ] Operaciones predefinidas creadas
- [ ] Ubicaciones RMA en almacenes
- [ ] Tipos de operación configurados

---

## 🧪 Validación Funcional

### Test 1: Crear RMA Manualmente

**Pasos:**
1. Ir a **RMA > RMAs > Crear**
2. Seleccionar cliente: "Azure Interior"
3. Seleccionar producto: Cualquier producto stockeable
4. Cantidad: 1
5. Operación: "Refund"
6. Guardar

**Validaciones:**
- [ ] RMA creado con estado "Draft"
- [ ] Nombre generado automáticamente
- [ ] Campo partner_id lleno
- [ ] Campo product_id lleno

### Test 2: Confirmar RMA

**Pasos:**
1. Abrir RMA creado en Test 1
2. Hacer clic en "Confirm"

**Validaciones:**
- [ ] Estado cambia a "Confirmed"
- [ ] Botón "Receive Products" visible
- [ ] Se puede generar picking de recepción

### Test 3: Recibir Productos

**Pasos:**
1. Hacer clic en "Receive Products"
2. Validar el picking generado
3. Hacer clic en "Validate"

**Validaciones:**
- [ ] Picking creado y validado
- [ ] Estado RMA cambia a "Received"
- [ ] Movimientos de stock creados
- [ ] Producto en ubicación RMA

### Test 4: Crear Nota de Crédito

**Pasos:**
1. Desde RMA en estado "Received"
2. Hacer clic en "Create Refund"
3. Completar wizard
4. Validar factura

**Validaciones:**
- [ ] Nota de crédito creada
- [ ] Estado RMA cambia a "Refunded"
- [ ] Asiento contable generado
- [ ] Smart button muestra factura

### Test 5: Portal de Cliente

**Pasos:**
1. Activar acceso portal para un cliente
2. Iniciar sesión en portal
3. Ir a "My Account > RMAs"
4. Crear nuevo RMA

**Validaciones:**
- [ ] Cliente puede ver sus RMAs
- [ ] Cliente puede crear RMA
- [ ] Cliente puede enviar mensajes
- [ ] Cliente ve estado del RMA

### Test 6: Reporte PDF

**Pasos:**
1. Abrir un RMA
2. Hacer clic en "Print > RMA Report"

**Validaciones:**
- [ ] PDF se genera sin errores
- [ ] Contiene información del RMA
- [ ] Diseño correcto
- [ ] Logo de empresa visible

### Test 7: Dashboard

**Pasos:**
1. Ir a **RMA > Dashboard**

**Validaciones:**
- [ ] Dashboard carga sin errores
- [ ] Gráficos se renderizan
- [ ] Datos correctos
- [ ] Filtros funcionan

### Test 8: Multi-Empresa

**Prerequisitos:** Base de datos con múltiples empresas

**Pasos:**
1. Crear RMA en empresa A
2. Cambiar a empresa B
3. Intentar ver RMA de empresa A

**Validaciones:**
- [ ] RMA de empresa A no visible en empresa B
- [ ] Cada empresa tiene sus propias ubicaciones RMA
- [ ] Secuencias independientes por empresa

---

## 🔄 Validación de Integración

### Con Stock

```python
# Verificar integración con movimientos
rma = env['rma'].search([], limit=1)
print(f"RMA: {rma.name}")
print(f"Picking de recepción: {rma.reception_picking_id.name if rma.reception_picking_id else 'No creado'}")
print(f"Movimientos: {len(rma.move_ids)}")
```

**Verificar:**
- [ ] Movimientos de stock vinculados
- [ ] Picking types correctos
- [ ] Trazabilidad completa

### Con Accounting

```python
# Verificar integración contable
rma = env['rma'].search([('state', '=', 'refunded')], limit=1)
if rma:
    print(f"RMA: {rma.name}")
    print(f"Factura: {rma.refund_id.name if rma.refund_id else 'No creada'}")
    print(f"Monto: {rma.refund_id.amount_total if rma.refund_id else 0}")
```

**Verificar:**
- [ ] Notas de crédito vinculadas
- [ ] Asientos contables correctos
- [ ] Conciliación funcionando

---

## 📊 Validación de Performance

### Test de Carga

```python
import time

# Crear 100 RMAs
start = time.time()
partner = env['res.partner'].search([], limit=1)
product = env['product.product'].search([('type', '=', 'product')], limit=1)

for i in range(100):
    env['rma'].create({
        'partner_id': partner.id,
        'product_id': product.id,
        'product_uom_qty': 1,
    })

end = time.time()
print(f"Tiempo para crear 100 RMAs: {end - start:.2f}s")
print(f"Promedio: {(end - start) / 100:.3f}s por RMA")

# Buscar con diferentes filtros
start = time.time()
rmas = env['rma'].search([('state', '=', 'draft')])
end = time.time()
print(f"Búsqueda de RMAs draft: {end - start:.3f}s ({len(rmas)} registros)")
```

**Verificar:**
- [ ] Creación < 0.5s por RMA
- [ ] Búsquedas < 1s
- [ ] Sin memory leaks

---

## 📝 Checklist Final

### Técnico
- [ ] Instalación sin errores
- [ ] Todas las tablas creadas
- [ ] Todos los modelos accesibles
- [ ] Todas las vistas funcionando
- [ ] Seguridad configurada
- [ ] Datos iniciales cargados
- [ ] Post-init hook ejecutado

### Funcional
- [ ] Crear RMA manual
- [ ] Confirmar RMA
- [ ] Recibir productos
- [ ] Crear nota de crédito
- [ ] Generar reemplazo
- [ ] Portal funcionando
- [ ] Reportes generándose
- [ ] Dashboard con datos

### Integración
- [ ] Stock: movimientos y picking
- [ ] Accounting: notas de crédito
- [ ] Portal: acceso clientes
- [ ] Mail: notificaciones

### Performance
- [ ] Tiempos de respuesta aceptables
- [ ] Sin errores en logs
- [ ] Memoria estable

---

## 🚨 Problemas Comunes y Soluciones

### Problema: No se crean ubicaciones RMA

**Solución:**
```python
from odoo.addons.rma.hooks import post_init_hook
post_init_hook(env)
```

### Problema: Usuario no ve RMAs

**Solución:**
```python
user = env['res.users'].browse(USER_ID)
group = env.ref('rma.group_rma_user')
user.write({'groups_id': [(4, group.id)]})
```

### Problema: Error al crear nota de crédito

**Verificar:**
- Configuración contable del producto
- Diario contable por defecto
- Posición fiscal del cliente

---

## ✅ Aprobación Final

**Revisado por:** _________________  
**Fecha:** _________________  
**Firma:** _________________

**Estado de la migración:** 
- [ ] ✅ APROBADA - Listo para producción
- [ ] ⚠️ CON OBSERVACIONES - Requiere ajustes menores
- [ ] ❌ RECHAZADA - Requiere correcciones

**Observaciones:**
```
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```

---

_Documento generado: 2026-03-02_  
_Versión del módulo: 19.0.1.0.0_
