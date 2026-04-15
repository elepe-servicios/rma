"""
Script para asignar manualmente el grupo RMA Manager a un usuario
desde el shell de Odoo si el post_init_hook no funciona.

Ejecutar desde el shell de Odoo:

python odoo-bin shell -d nombre_base_datos -c ruta/odoo.conf

Luego pegar este código:
"""

# Obtener el grupo RMA Manager
rma_manager_group = env.ref("rma.rma_group_manager", raise_if_not_found=False)

if not rma_manager_group:
    print("ERROR: No se encontró el grupo RMA Manager")
    print("Asegúrate de que el módulo RMA esté instalado correctamente")
else:
    print(f"Grupo RMA Manager encontrado: {rma_manager_group.name}")

    # Asignar al usuario admin
    admin_user = env.ref("base.user_admin", raise_if_not_found=False)
    if admin_user:
        if not admin_user.has_group("rma.rma_group_manager"):
            rma_manager_group.write({"user_ids": [(4, admin_user.id)]})
            print(f"✓ Grupo asignado al usuario admin: {admin_user.name}")
        else:
            print(f"✓ Usuario admin ya tiene el grupo RMA Manager: {admin_user.name}")

    # Asignar a todos los usuarios con permisos de Settings (group_system)
    system_group = env.ref("base.group_system", raise_if_not_found=False)
    if system_group:
        for user in system_group.user_ids:
            if not user.has_group("rma.rma_group_manager"):
                rma_manager_group.write({"user_ids": [(4, user.id)]})
                print(f"✓ Grupo asignado al usuario: {user.name}")
            else:
                print(f"✓ Usuario {user.name} ya tiene el grupo RMA Manager")

    print("\n=== RESULTADO ===")
    print(f"Total de usuarios con grupo RMA Manager: {len(rma_manager_group.user_ids)}")
    print("Usuarios:")
    for user in rma_manager_group.user_ids:
        print(f"  - {user.name} ({user.login})")

    print("\n=== MENÚS RMA ===")
    # Verificar que los menús existan
    menu_ids = [
        "rma.rma_menu",
        "rma.rma_orders_menu",
        "rma.rma_reporting_menu",
        "rma.rma_configuration_menu",
    ]

    for menu_id in menu_ids:
        menu = env.ref(menu_id, raise_if_not_found=False)
        if menu:
            groups = menu.groups_id.mapped('name')
            print(f"✓ Menú '{menu.name}' - Grupos: {', '.join(groups) if groups else 'Sin grupos'}")
        else:
            print(f"✗ Menú {menu_id} NO encontrado")

print("\n=== INSTRUCCIONES FINALES ===")
print("1. Cierra sesión de Odoo")
print("2. Vuelve a iniciar sesión")
print("3. Refresca el navegador (Ctrl+F5)")
print("4. El menú RMA debería aparecer en la barra superior")
