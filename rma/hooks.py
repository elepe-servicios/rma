# Copyright 2020 Tecnativa - Ernesto Tejeda
# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def post_init_hook(env):
    def _get_next_picking_type_color():
        """Choose the next available color for the operation types."""
        stock_picking_type = env["stock.picking.type"]
        picking_type = stock_picking_type.search_read(
            [("warehouse_id", "!=", False), ("color", "!=", False)],
            ["color"],
            order="color",
        )
        all_used_colors = [res["color"] for res in picking_type]
        available_colors = [
            color for color in range(0, 12) if color not in all_used_colors
        ]
        return available_colors[0] if available_colors else 0

    def create_rma_locations(warehouse):
        stock_location = env["stock.location"]
        if not warehouse.rma_loc_id:
            rma_location_vals = warehouse._get_rma_location_values(
                {"company_id": warehouse.company_id.id}, warehouse.code
            )
            warehouse.rma_loc_id = (
                stock_location.with_context(active_test=False)
                .create(rma_location_vals)
                .id
            )

    def create_rma_picking_types(whs):
        ir_sequence_sudo = env["ir.sequence"].sudo()
        stock_picking_type = env["stock.picking.type"]
        color = _get_next_picking_type_color()
        stock_picking = stock_picking_type.search(
            [("sequence", "!=", False)], limit=1, order="sequence desc"
        )
        max_sequence = stock_picking.sequence or 0
        create_data = whs._get_picking_type_create_values(max_sequence)[0]
        sequence_data = whs._get_sequence_values()
        data = {}
        for picking_type, values in create_data.items():
            if (
                picking_type in ["rma_in_type_id", "rma_out_type_id"]
                and not whs[picking_type]
            ):
                picking_sequence = sequence_data[picking_type]
                sequence = ir_sequence_sudo.create(picking_sequence)
                values.update(
                    warehouse_id=whs.id,
                    color=color,
                    sequence_id=sequence.id,
                )
                data[picking_type] = stock_picking_type.create(values).id

        if data:
            whs.write(data)
        whs.rma_in_type_id.return_picking_type_id = whs.rma_out_type_id.id
        whs.rma_out_type_id.return_picking_type_id = whs.rma_in_type_id.id

    def create_rma_routes(warehouses):
        """Create initially rma in/out stock.location.routes and stock.rules"""
        warehouses = warehouses.with_context(rma_post_init_hook=True)
        for wh in warehouses:
            route_vals = wh._create_or_update_route()
            wh.write(route_vals)

    # Create rma locations and picking types
    warehouses = env["stock.warehouse"].search([])
    for warehouse in warehouses:
        create_rma_locations(warehouse)
        create_rma_picking_types(warehouse)
    create_rma_routes(warehouses)
    # Create rma sequence per company
    for company in env["res.company"].search([]):
        company.create_rma_index()

    # Assign RMA Manager group to admin users
    rma_manager_group = env.ref("rma.rma_group_manager", raise_if_not_found=False)
    if rma_manager_group:
        # Assign to user_admin (the main admin user)
        admin_user = env.ref("base.user_admin", raise_if_not_found=False)
        if admin_user:
            # In Odoo 19, use has_group to check and user_ids field to assign
            if not admin_user.has_group("rma.rma_group_manager"):
                rma_manager_group.write({"user_ids": [(4, admin_user.id)]})

        # Also assign to all users with Settings access (group_system)
        system_group = env.ref("base.group_system", raise_if_not_found=False)
        if system_group:
            # In Odoo 19, the field is user_ids not users
            for user in system_group.user_ids:
                if not user.has_group("rma.rma_group_manager"):
                    rma_manager_group.write({"user_ids": [(4, user.id)]})
