import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.api.deps import get_db
from app.db.rbac_models import Role, Permission, RolePermission
from app.db.models import User
from app.core.security import hash_password

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def seed_rbac(db):
    """Seed the basic RBAC roles and permissions required for testing."""
    # Create roles
    user_role = Role(id=1, name="user", description="User")
    manager_role = Role(id=2, name="manager", description="Manager")
    admin_role = Role(id=3, name="admin", description="Admin")
    db.add_all([user_role, manager_role, admin_role])

    # Create permissions
    perms = [
        Permission(id=1, name="orders:create"),
        Permission(id=2, name="orders:read_own"),
        Permission(id=3, name="orders:read_all"),
        Permission(id=4, name="users:read_own"),
        Permission(id=5, name="users:list"),
        Permission(id=6, name="rbac:manage"),
    ]
    db.add_all(perms)
    db.commit()

    # Map permissions
    mappings = [
        # user
        RolePermission(role_id=1, permission_id=1),
        RolePermission(role_id=1, permission_id=2),
        RolePermission(role_id=1, permission_id=4),
        # manager
        RolePermission(role_id=2, permission_id=1),
        RolePermission(role_id=2, permission_id=2),
        RolePermission(role_id=2, permission_id=3),
        RolePermission(role_id=2, permission_id=4),
        # admin (all)
        *[RolePermission(role_id=3, permission_id=i) for i in range(1, 7)]
    ]
    db.add_all(mappings)
    db.commit()


@pytest.fixture(scope="session")
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    seed_rbac(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session(setup_db):
    """Provides a fresh database session for a test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    """Provides a TestClient with the dependency overridden to use the test DB session."""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def create_test_user_in_db(db_session, email, password, role_id):
    user = User(
        email=email,
        hashed_password=hash_password(password),
        role_id=role_id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture()
def test_user(db_session):
    email = "user@example.com"
    password = "password123"
    create_test_user_in_db(db_session, email, password, role_id=1)
    
    app.dependency_overrides[get_db] = lambda: db_session
    c = TestClient(app)
    response = c.post("/api/v1/auth/login", data={"username": email, "password": password})
    c.headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
    return c


@pytest.fixture()
def test_manager(db_session):
    email = "manager@example.com"
    password = "password123"
    create_test_user_in_db(db_session, email, password, role_id=2)
    
    app.dependency_overrides[get_db] = lambda: db_session
    c = TestClient(app)
    response = c.post("/api/v1/auth/login", data={"username": email, "password": password})
    c.headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
    return c


@pytest.fixture()
def test_admin(db_session):
    email = "admin@example.com"
    password = "password123"
    create_test_user_in_db(db_session, email, password, role_id=3)
    
    app.dependency_overrides[get_db] = lambda: db_session
    c = TestClient(app)
    response = c.post("/api/v1/auth/login", data={"username": email, "password": password})
    c.headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
    return c
