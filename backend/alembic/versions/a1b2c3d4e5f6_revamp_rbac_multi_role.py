"""revamp_rbac_multi_role

Revision ID: a1b2c3d4e5f6
Revises: 3b9a206351da
Create Date: 2026-03-11 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '3b9a206351da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── 1. Create user_roles association table ───────────────
    op.create_table(
        'user_roles',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'role_id'),
    )

    # ── 2. Migrate existing user→role data ───────────────────
    op.execute(
        "INSERT INTO user_roles (user_id, role_id) "
        "SELECT id, role_id FROM users"
    )

    # ── 3. Drop the old role_id FK column from users ─────────
    op.drop_constraint('fk_users_role_id', 'users', type_='foreignkey')
    op.drop_column('users', 'role_id')

    # ── 4. Add updated_at columns ────────────────────────────
    op.add_column(
        'users',
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=True,
        ),
    )
    op.add_column(
        'roles',
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=True,
        ),
    )
    op.add_column(
        'permissions',
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=True,
        ),
    )
    op.add_column(
        'orders',
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=True,
        ),
    )

    # ── 5. Seed new permissions ──────────────────────────────
    op.execute(
        "INSERT INTO permissions (name, description) VALUES "
        "('orders:update_status', 'Can change order status'),"
        "('orders:cancel', 'Can cancel any order'),"
        "('users:deactivate', 'Can deactivate a user account')"
    )

    # Assign new perms to manager and admin
    # orders:update_status & orders:cancel → manager, admin
    op.execute(
        "INSERT INTO role_permissions (role_id, permission_id) "
        "SELECT r.id, p.id FROM roles r, permissions p "
        "WHERE r.name IN ('manager', 'admin') "
        "AND p.name IN ('orders:update_status', 'orders:cancel')"
    )
    # users:deactivate → admin only
    op.execute(
        "INSERT INTO role_permissions (role_id, permission_id) "
        "SELECT r.id, p.id FROM roles r, permissions p "
        "WHERE r.name = 'admin' AND p.name = 'users:deactivate'"
    )


def downgrade() -> None:
    # Remove new permissions
    op.execute(
        "DELETE FROM role_permissions WHERE permission_id IN "
        "(SELECT id FROM permissions WHERE name IN "
        "('orders:update_status', 'orders:cancel', 'users:deactivate'))"
    )
    op.execute(
        "DELETE FROM permissions WHERE name IN "
        "('orders:update_status', 'orders:cancel', 'users:deactivate')"
    )

    # Remove updated_at columns
    op.drop_column('orders', 'updated_at')
    op.drop_column('permissions', 'updated_at')
    op.drop_column('roles', 'updated_at')
    op.drop_column('users', 'updated_at')

    # Restore role_id on users
    op.add_column(
        'users',
        sa.Column('role_id', sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        'fk_users_role_id', 'users', 'roles', ['role_id'], ['id']
    )

    # Migrate data back (take first role)
    op.execute(
        "UPDATE users SET role_id = ("
        "  SELECT role_id FROM user_roles WHERE user_roles.user_id = users.id LIMIT 1"
        ")"
    )
    op.alter_column('users', 'role_id', nullable=False)

    # Drop user_roles table
    op.drop_table('user_roles')
