"""add_rbac_tables_and_seed_data

Revision ID: 3b9a206351da
Revises: 32c867376892
Create Date: 2026-03-10 18:10:56.182518

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b9a206351da'
down_revision: Union[str, Sequence[str], None] = '32c867376892'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── 1. Create RBAC Tables ────────────────────────────────────────────────
    roles_table = op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_roles_name'), 'roles', ['name'], unique=True)
    
    perms_table = op.create_table(
        'permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_permissions_name'), 'permissions', ['name'], unique=True)
    
    role_perms_table = op.create_table(
        'role_permissions',
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('role_id', 'permission_id')
    )

    # ── 2. Seed Data ────────────────────────────────────────────────────────
    # Standard Roles
    op.bulk_insert(roles_table, [
        {'id': 1, 'name': 'user', 'description': 'Standard customer'},
        {'id': 2, 'name': 'manager', 'description': 'Store manager'},
        {'id': 3, 'name': 'admin', 'description': 'System administrator'},
    ])

    # Standard Permissions
    op.bulk_insert(perms_table, [
        {'id': 1, 'name': 'orders:create', 'description': 'Can place an order'},
        {'id': 2, 'name': 'orders:read_own', 'description': 'Can view own orders'},
        {'id': 3, 'name': 'orders:read_all', 'description': 'Can view all orders'},
        {'id': 4, 'name': 'users:read_own', 'description': 'Can read own profile'},
        {'id': 5, 'name': 'users:list', 'description': 'Can list all users'},
        {'id': 6, 'name': 'rbac:manage', 'description': 'Can manage roles and permissions'},
    ])

    # Bind Permissions to Roles (user=1, manager=2, admin=3)
    op.bulk_insert(role_perms_table, [
        # User permissions
        {'role_id': 1, 'permission_id': 1},
        {'role_id': 1, 'permission_id': 2},
        {'role_id': 1, 'permission_id': 4},
        
        # Manager permissions (user perms + view all orders)
        {'role_id': 2, 'permission_id': 1},
        {'role_id': 2, 'permission_id': 2},
        {'role_id': 2, 'permission_id': 3},
        {'role_id': 2, 'permission_id': 4},
        
        # Admin permissions (all)
        {'role_id': 3, 'permission_id': 1},
        {'role_id': 3, 'permission_id': 2},
        {'role_id': 3, 'permission_id': 3},
        {'role_id': 3, 'permission_id': 4},
        {'role_id': 3, 'permission_id': 5},
        {'role_id': 3, 'permission_id': 6},
    ])

    # ── 3. Migrate Users Table ───────────────────────────────────────────────
    # Add role_id column initially nullable
    op.add_column('users', sa.Column('role_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_users_role_id', 'users', 'roles', ['role_id'], ['id'])
    
    # Map old string role to default 'user' ID (1), or handle 'ADMIN' mapping to 'admin' ID (3)
    # Using raw SQL
    op.execute(
        "UPDATE users SET role_id = 3 WHERE role = 'ADMIN'"
    )
    op.execute(
        "UPDATE users SET role_id = 1 WHERE role_id IS NULL"
    )

    # Now make role_id non-nullable and drop old role column
    op.alter_column('users', 'role_id', nullable=False)
    op.drop_column('users', 'role')


def downgrade() -> None:
    # Reverse migrations
    op.add_column('users', sa.Column('role', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.execute("UPDATE users SET role = 'ADMIN' WHERE role_id = 3")
    op.execute("UPDATE users SET role = 'USER' WHERE role_id = 1")
    op.drop_constraint('fk_users_role_id', 'users', type_='foreignkey')
    op.drop_column('users', 'role_id')
    
    op.drop_table('role_permissions')
    op.drop_index(op.f('ix_permissions_name'), table_name='permissions')
    op.drop_table('permissions')
    op.drop_index(op.f('ix_roles_name'), table_name='roles')
    op.drop_table('roles')
