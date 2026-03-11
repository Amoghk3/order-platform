import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Layout() {
  const { user, isAdmin, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="app-layout">
      {/* ── Sidebar ─────────────────────────────────── */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <span className="brand-icon">📦</span>
          <h1>OrderHub</h1>
        </div>

        <nav className="sidebar-nav">
          <NavLink to="/dashboard" className="nav-link" id="nav-dashboard">
            <span className="nav-icon">🏠</span>
            Dashboard
          </NavLink>
          <NavLink to="/orders" className="nav-link" id="nav-orders">
            <span className="nav-icon">🛒</span>
            My Orders
          </NavLink>

          {isAdmin && (
            <>
              <div className="nav-divider" />
              <span className="nav-section-label">Admin</span>
              <NavLink to="/admin/orders" className="nav-link" id="nav-admin-orders">
                <span className="nav-icon">📋</span>
                All Orders
              </NavLink>
              <NavLink to="/admin/users" className="nav-link" id="nav-admin-users">
                <span className="nav-icon">👥</span>
                Users
              </NavLink>
              <NavLink to="/admin/rbac" className="nav-link" id="nav-admin-rbac">
                <span className="nav-icon">🔐</span>
                RBAC
              </NavLink>
            </>
          )}
        </nav>

        <div className="sidebar-footer">
          <div className="user-chip">
            <span className="user-avatar">
              {user?.email?.charAt(0).toUpperCase()}
            </span>
            <div className="user-info">
              <span className="user-email">{user?.email}</span>
              <span className="user-role">{user?.role?.name}</span>
            </div>
          </div>
          <button onClick={handleLogout} className="btn btn-ghost btn-sm" id="btn-logout">
            Logout
          </button>
        </div>
      </aside>

      {/* ── Main content ────────────────────────────── */}
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
