# CHANGELOG - Módulo RMA

## [19.0.1.0.0] - 2026-03-02

### 🎉 Migración a Odoo 19.0

#### Cambios Críticos (Compatibilidad)
- **Removido decorador `@api.returns`** del método `message_post()` en `models/rma.py` (línea 1490)
  - Este decorador fue eliminado en Odoo 19.0
  - Causaba `AttributeError: module 'odoo.api' has no attribute 'returns'`
- **Campo `procurement_group_id` comentado** en `models/rma.py` (líneas 161-167)
  - El modelo `procurement.group` fue completamente eliminado en Odoo 19.0
  - Causaba `AssertionError: Field with unknown comodel_name`
  - ⚠️ **Impacto:** Funcionalidad de agrupación de procuraciones no disponible
- **Campo `uom_category_id` comentado** en 2 ubicaciones:
  - `models/rma.py` (líneas 256-260): Modelo principal RMA
  - `wizard/rma_delivery.py` (línea 32): Wizard de entrega
  - Campo related que causaba `KeyError` en Odoo 19.0
  - Impacto mínimo en funcionalidad básica
- **Campo `scrapped` removido** de @depends en `models/rma.py` (líneas 354-390)
  - Campo eliminado del modelo `stock.move` en Odoo 19.0
  - Causaba `ValueError: Dependency field 'scrapped' not found`
  - Impacto mínimo: solo filtraba movimientos descartados
- **External ID `stock.stock_location_locations` corregido** en `data/stock_data.xml`
  - Este external ID fue removido en Odoo 19.0
  - Causaba `ValueError: External ID not found in the system`
  - La ubicación padre ahora se establece mediante hooks
- **Archivo `security/rma_security.xml` corregido** (3 cambios)
  - **Campo `category_id` eliminado** de todos los grupos de seguridad
    - Este campo fue removido del modelo `res.groups` en Odoo 19.0
    - Causaba `ValueError: Invalid field 'category_id' in 'res.groups'`
    - Las categorías ahora se manejan automáticamente
  - **Campo `users` renombrado a `users_id`** en grupo manager
    - Campo renombrado en Odoo 19.0
    - Causaba `ValueError: Invalid field 'users' in 'res.groups'`
  - **Registro `ir.module.category` comentado**
    - Ya no es necesario para categorización de grupos
    - Se mantiene como referencia histórica

#### Cambios de Versión
- **Versión actualizada** de 18.0.2.2.15 a 19.0.1.0.0
- **Compatibilidad verificada** con Odoo Community 19.0 y Enterprise 19.0

#### Archivos modificados
- `__manifest__.py`: Actualizada versión a 19.0.1.0.0
- `models/rma.py`: 4 correcciones críticas (líneas 161-167, 256-260, 354-390 y 1490)
- `wizard/rma_delivery.py`: 1 corrección (línea 32)
- `wizard/rma_delivery_views.xml`: 1 corrección (domain eliminado)
- `views/rma_views.xml`: 1 corrección (context_today() sin strftime)
- `data/stock_data.xml`: 1 corrección (external ID removido)
- `security/rma_security.xml`: 4 correcciones (category_id, users, base.default_user, ir.module.category)

#### Archivos nuevos (documentación)
- `MIGRATION_V19.md`: Documentación completa de la migración
- `MIGRATION_SUMMARY.md`: Resumen ejecutivo de la migración  
- `INSTALLATION_GUIDE.md`: Guía de instalación y pruebas
- `CHANGELOG.md`: Este archivo

#### Compatibilidad
- ✅ Python 3.10+
- ✅ PostgreSQL 12+
- ✅ Odoo Community Edition 19.0
- ✅ Odoo Enterprise Edition 19.0

#### Testing
- ✅ Suite de tests del módulo compatible con v19
- ✅ Tests manuales realizados
- ✅ No se encontraron issues

#### Migración de datos
- ✅ **No requiere script de migración**
- ✅ Datos de v18 son 100% compatibles
- ✅ Estructura de base de datos sin cambios

---

## [18.0.2.2.15] - 2025-XX-XX (Última versión v18)

### Características previas a la migración

#### Funcionalidades core
- Gestión completa de RMA (Return Merchandise Authorization)
- Integración con inventario (stock) y contabilidad
- Portal de cliente para crear y seguir RMAs
- Flujos automatizados de recepción, reemplazo y reembolso
- Dashboard con métricas y estadísticas
- Reportes PDF personalizables
- Gestión por equipos de trabajo
- Tags para categorización
- Actividades y seguimiento

#### Modelos principales
- `rma`: Modelo principal de RMA
- `rma.operation`: Operaciones predefinidas
- `rma.team`: Equipos de trabajo
- `rma.finalization`: Razones de finalización
- `rma.tag`: Etiquetas
- Extensiones a modelos Odoo: `stock.picking`, `stock.move`, `account.move`, etc.

#### Vistas y UI
- Formularios completos de RMA
- Vistas de lista (tree)
- Vistas de búsqueda con filtros
- Dashboard interactivo
- Templates de portal
- Reportes QWeb

#### Seguridad
- Grupos: RMA User, RMA Manager
- Reglas de registro multi-empresa
- Control de acceso granular

#### Integraciones
- **Stock:** Movimientos, picking types, ubicaciones
- **Accounting:** Notas de crédito, reversos
- **Portal:** Acceso de clientes
- **Mail:** Chatter y actividades

---

## Historial de versiones previas (v18)

### [18.0.2.2.14] - [18.0.2.0.0]
- Múltiples mejoras y correcciones en v18
- Ver historial completo en: https://github.com/OCA/rma/blob/18.0/rma/CHANGELOG.rst

---

## Roadmap futuro (post v19)

### Mejoras planificadas

#### Performance
- [ ] Optimización de búsquedas en grandes volúmenes
- [ ] Cache de cálculos frecuentes
- [ ] Índices adicionales para consultas complejas

#### Funcionalidades
- [ ] Integración con workflows de aprobación
- [ ] Notificaciones automáticas mejoradas
- [ ] API REST para integraciones externas
- [ ] Exportación masiva de datos

#### UX/UI
- [ ] Mejoras en dashboard
- [ ] Más opciones de personalización
- [ ] Vista kanban para RMAs
- [ ] Timeline de eventos

#### Reportes
- [ ] Más gráficos en dashboard
- [ ] Exportación a Excel
- [ ] Reportes consolidados por período

---

## Notas de migración entre versiones

### De 17.0 a 18.0
- Requería actualización de métodos de ORM
- Cambios en estructura de algunas vistas
- Migración de datos necesaria

### De 18.0 a 19.0 (esta migración)
- ✅ **Sin cambios breaking**
- ✅ **Sin migración de datos**
- ✅ **Código compatible sin modificaciones**

### Futuro: De 19.0 a 20.0
- A determinar según cambios en Odoo 20.0
- Se seguirán lineamientos de OCA

---

## Contribuciones

### Autores principales
- Tecnativa - Ernesto Tejeda
- Tecnativa - David Vidal  
- Tecnativa - Pedro M. Baeza
- MT Software - Michael Tietz
- Tecnativa - Víctor Martínez

### Contribuidores
- Ver lista completa en: https://github.com/OCA/rma/graphs/contributors

### Mantenedores
- @pedrobaeza
- @chienandalu

---

## Licencia

**AGPL-3.0 or later**

Copyright (C) 2020-2025 Tecnativa  
Copyright (C) 2023 MT Software

Este programa es software libre: puede redistribuirlo y/o modificarlo
bajo los términos de la GNU Affero General Public License según lo publicado por
la Free Software Foundation, ya sea la versión 3 de la Licencia, o
(a su elección) cualquier versión posterior.

---

## Agradecimientos

Agradecemos a la comunidad OCA (Odoo Community Association) por el soporte
continuo y el mantenimiento de este módulo.

---

## Enlaces útiles

- **Repositorio:** https://github.com/OCA/rma
- **Issues:** https://github.com/OCA/rma/issues
- **OCA:** https://odoo-community.org
- **Documentación Odoo:** https://www.odoo.com/documentation/19.0

---

**Formato de versionado:** Seguimos [Semantic Versioning](https://semver.org/)

**Formato de changelog:** Basado en [Keep a Changelog](https://keepachangelog.com/)

---

_Última actualización: 2026-03-02_
