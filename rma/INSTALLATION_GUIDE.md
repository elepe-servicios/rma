# Guía de Instalación y Pruebas - RMA v19.0

## Instalación

### Opción 1: Instalación limpia en Odoo 19

```bash
# 1. Asegurarse de que el módulo esté en el addons_path
# Editar odoo.conf y verificar:
# addons_path = /path/to/odoo/addons,/path/to/custom/addons

# 2. Actualizar lista de módulos
odoo-bin -c odoo.conf -d mi_base_datos -u base --stop-after-init

# 3. Instalar el módulo RMA
odoo-bin -c odoo.conf -d mi_base_datos -i rma --stop-after-init

# 4. (Opcional) Ejecutar con tests
odoo-bin -c odoo.conf -d mi_base_datos -i rma --test-enable --stop-after-init
```

### Opción 2: Actualización desde Odoo 18

```bash
# 1. Hacer backup de la base de datos
pg_dump mi_base_datos > backup_antes_migracion.sql

# 2. Actualizar Odoo de v18 a v19 (seguir guía oficial de Odoo)

# 3. Actualizar el módulo RMA
odoo-bin -c odoo.conf -d mi_base_datos -u rma --stop-after-init

# 4. Verificar logs por posibles warnings
tail -f /var/log/odoo/odoo.log
```

### Opción 3: Instalación con Docker

```bash
# Usando docker-compose
docker-compose run --rm odoo odoo -i rma -d mi_base_datos --stop-after-init
```

---

## Verificación Post-Instalación

### 1. Verificar configuración automática

Después de instalar, verificar que se hayan creado:

```python
# En Odoo shell (odoo-bin shell -d mi_base_datos)
env = odoo.api.Environment(cr, uid, {})

# Verificar ubicaciones RMA
warehouses = env['stock.warehouse'].search([])
for wh in warehouses:
    print(f"Almacén: {wh.name}")
    print(f"  - Ubicación RMA: {wh.rma_loc_id.name}")
    print(f"  - Tipo operación entrada: {wh.rma_in_type_id.name}")
    print(f"  - Tipo operación salida: {wh.rma_out_type_id.name}")

# Verificar secuencias por empresa
companies = env['res.company'].search([])
for company in companies:
    seq = env['ir.sequence'].search([
        ('code', '=', 'rma'),
        ('company_id', '=', company.id)
    ])
    print(f"Empresa: {company.name} - Secuencia RMA: {seq.name}")
```

### 2. Verificar accesos de seguridad

```sql
-- En PostgreSQL, verificar grupos de acceso
SELECT g.name, g.category_id
FROM res_groups g
WHERE g.name LIKE '%RMA%';

-- Verificar permisos de modelos
SELECT m.model, a.name, a.perm_read, a.perm_write, a.perm_create, a.perm_unlink
FROM ir_model_access a
JOIN ir_model m ON a.model_id = m.id
WHERE m.model LIKE '%rma%';
```

### 3. Verificar vistas

```python
# Verificar que las vistas principales existan
view_names = [
    'rma.rma_view_form',
    'rma.rma_view_tree',
    'rma.rma_view_search',
    'rma.portal_my_rmas',
]
for view_name in view_names:
    view = env.ref(view_name, raise_if_not_found=False)
    if view:
        print(f"✅ Vista {view_name}: OK")
    else:
        print(f"❌ Vista {view_name}: NO ENCONTRADA")
```

---

## Pruebas Funcionales

### Test 1: Crear RMA desde cero

1. Ir a **RMA > RMAs > Crear**
2. Completar campos:
   - Cliente
   - Producto
   - Cantidad
   - Operación solicitada
3. **Confirmar** el RMA
4. Verificar estado: "Confirmed"
5. Verificar que se haya creado el picking de recepción

### Test 2: Crear RMA desde delivery

1. Crear una orden de venta y entregarla
2. En el picking de entrega (estado "Done"), hacer clic en "Create RMA"
3. Seleccionar productos a devolver
4. Crear el RMA
5. Verificar que el campo "Origin Delivery" esté lleno
6. Procesar la recepción del producto

### Test 3: Flujo completo de reemplazo

1. Crear RMA con operación "Replace"
2. Confirmar
3. Procesar recepción (botón "Receive Products")
4. Validar el picking de entrada
5. Verificar que el estado cambie a "Received"
6. Verificar que se cree automáticamente un picking de salida para el reemplazo
7. Procesar el envío del reemplazo
8. Verificar estado final: "Replaced"

### Test 4: Flujo completo de reembolso

1. Crear RMA con operación "Refund"
2. Confirmar
3. Procesar recepción
4. Crear nota de crédito (botón "Create Refund")
5. Verificar que se genere una factura de tipo "Credit Note"
6. Validar la nota de crédito
7. Verificar estado final: "Refunded"

### Test 5: Portal de cliente

1. Activar el portal para un cliente
2. Iniciar sesión como cliente en el portal
3. Ir a **My Account > RMAs**
4. Crear un nuevo RMA desde el portal
5. Verificar que el cliente puede:
   - Ver listado de sus RMAs
   - Ver detalle de cada RMA
   - Enviar mensajes en el chatter
   - Ver estado actual

### Test 6: Equipos de RMA

1. Ir a **RMA > Configuración > Equipos**
2. Crear un equipo de RMA
3. Asignar miembros al equipo
4. Crear RMA y asignar al equipo
5. Verificar que los miembros puedan ver el RMA
6. Verificar reglas de acceso

### Test 7: Dashboard y reportes

1. Ir a **RMA > Dashboard**
2. Verificar gráficos:
   - RMAs por estado
   - RMAs por equipo
   - RMAs por razón de finalización
3. Generar reporte PDF de un RMA
4. Verificar que se genere correctamente

### Test 8: Multi-empresa

1. Configurar múltiples empresas
2. Crear RMA para empresa A
3. Cambiar de empresa a B
4. Verificar que no se vea el RMA de empresa A
5. Crear RMA para empresa B
6. Verificar almacenes y ubicaciones por empresa

---

## Pruebas Automatizadas

### Ejecutar suite completa de tests

```bash
# Tests unitarios
odoo-bin -c odoo.conf -d test_rma --test-enable --stop-after-init -i rma

# Tests específicos de un módulo
odoo-bin -c odoo.conf -d test_rma --test-enable --stop-after-init \
  --test-tags /rma

# Tests con coverage (requiere coverage.py instalado)
coverage run odoo-bin -c odoo.conf -d test_rma --test-enable \
  --stop-after-init -i rma
coverage report
coverage html
```

### Tests de integración con otros módulos

```bash
# Si tienes rma_sale instalado
odoo-bin -c odoo.conf -d test_rma --test-enable --stop-after-init \
  -i rma,rma_sale --test-tags /rma,/rma_sale
```

---

## Troubleshooting

### Problema: "No se crean ubicaciones RMA automáticamente"

**Solución:**
```python
# Ejecutar manualmente el post_init_hook
from odoo.addons.rma.hooks import post_init_hook
post_init_hook(env)
```

### Problema: "Usuario no puede ver RMAs"

**Verificar:**
1. Que el usuario tenga el grupo "RMA / User" o "RMA / Manager"
2. Que el usuario pertenezca a un equipo de RMA si está configurado
3. Revisar reglas de registro (ir.rule)

**Solución:**
```python
# Asignar grupo al usuario
user = env['res.users'].browse(USER_ID)
group = env.ref('rma.group_rma_user')
user.groups_id = [(4, group.id)]
```

### Problema: "Error al crear nota de crédito"

**Verificar:**
1. Que el módulo `stock_account` esté instalado
2. Que los productos tengan configuración contable
3. Que existan diarios contables

### Problema: "Portal no muestra RMAs"

**Verificar:**
1. Que el cliente tenga acceso al portal
2. Que las vistas de portal estén instaladas
3. Verificar permisos en ir.rule para portal

---

## Performance y Optimización

### Índices de base de datos

El módulo crea automáticamente índices en:
- `rma.name`
- `rma.date`
- `rma.user_id`
- `rma.team_id`
- `rma.partner_id`

### Optimización de búsquedas

Para mejorar performance en bases con muchos RMAs:

```python
# Buscar con límite y offset
rmas = env['rma'].search([('state', '=', 'confirmed')], 
                          limit=100, offset=0, 
                          order='date desc')

# Usar search_count para contadores
count = env['rma'].search_count([('state', '=', 'draft')])

# Agrupar lecturas
rmas = env['rma'].search([])
data = rmas.read(['name', 'partner_id', 'state', 'date'])
```

### Limpieza de datos antiguos

```python
# Archivar RMAs finalizados hace más de 2 años
from datetime import datetime, timedelta
two_years_ago = datetime.now() - timedelta(days=730)
old_rmas = env['rma'].search([
    ('state', 'in', ['finished', 'cancelled', 'locked']),
    ('write_date', '<', two_years_ago.strftime('%Y-%m-%d'))
])
# Nota: RMA no tiene campo 'active', considerar implementarlo si se necesita archiving
```

---

## Logs y Debugging

### Activar logs de debug

En `odoo.conf`:
```ini
[options]
log_level = debug
log_handler = :DEBUG,odoo.addons.rma:DEBUG
```

### Logs importantes a revisar

```bash
# Ver logs de instalación
grep "rma" /var/log/odoo/odoo.log | grep -i "init"

# Ver logs de errores
grep "rma" /var/log/odoo/odoo.log | grep -i "error"

# Ver logs de post_init_hook
grep "post_init_hook" /var/log/odoo/odoo.log
```

---

## Checklist Final

Después de la instalación, verificar:

- [ ] Ubicaciones RMA creadas en todos los almacenes
- [ ] Tipos de operación RMA (entrada/salida) creados
- [ ] Rutas de stock configuradas
- [ ] Secuencias RMA por empresa
- [ ] Grupos de seguridad asignados a usuarios
- [ ] Portal accesible para clientes
- [ ] Vistas principales funcionando
- [ ] Reportes PDF generándose correctamente
- [ ] Dashboard mostrando datos
- [ ] Tests automatizados pasando
- [ ] Integración con stock funcionando
- [ ] Integración con accounting funcionando

---

## Soporte y Documentación

- **Documentación completa:** `MIGRATION_V19.md`
- **Issues de OCA:** https://github.com/OCA/rma/issues
- **Odoo Community:** https://odoo-community.org
- **Foro Odoo:** https://www.odoo.com/forum

---

**Última actualización:** 2026-03-02  
**Versión del módulo:** 19.0.1.0.0
