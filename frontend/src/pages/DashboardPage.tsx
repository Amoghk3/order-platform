import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import client from "../api/client";
import type { Order } from "../types";

export default function DashboardPage() {
  const { user } = useAuth();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    client
      .get<Order[]>("/orders/me")
      .then((r) => setOrders(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const total = orders.length;
  const pending = orders.filter((o) => o.status === "PENDING").length;
  const completed = orders.filter((o) => o.status === "COMPLETED").length;
  const totalSpent = orders
    .reduce((sum, o) => sum + parseFloat(o.total_amount), 0)
    .toFixed(2);

  return (
    <div style={{ animation: "fadeUp 0.4s ease" }}>
      <div className="page-header">
        <div>
          <h2>Dashboard</h2>
          <p className="page-subtitle">
            Welcome back, {user?.email}
          </p>
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: "center", padding: "3rem" }}>
          <span className="spinner" />
        </div>
      ) : (
        <>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-label">Total Orders</div>
              <div className="stat-value">{total}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Pending</div>
              <div className="stat-value" style={{ color: "var(--status-pending)" }}>
                {pending}
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Completed</div>
              <div className="stat-value" style={{ color: "var(--status-completed)" }}>
                {completed}
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Total Spent</div>
              <div className="stat-value">${totalSpent}</div>
            </div>
          </div>

          <div className="glass-card">
            <h3 style={{ marginBottom: "1rem", fontWeight: 600 }}>
              Recent Orders
            </h3>
            {orders.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">📦</div>
                <p>No orders yet. Create your first order!</p>
              </div>
            ) : (
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Amount</th>
                      <th>Status</th>
                      <th>Created</th>
                    </tr>
                  </thead>
                  <tbody>
                    {orders.slice(0, 5).map((o) => (
                      <tr key={o.id}>
                        <td>#{o.id}</td>
                        <td>${parseFloat(o.total_amount).toFixed(2)}</td>
                        <td>
                          <span
                            className="status-badge"
                            style={{
                              background: `var(--status-${o.status.toLowerCase()})`,
                            }}
                          >
                            {o.status}
                          </span>
                        </td>
                        <td>{new Date(o.created_at).toLocaleDateString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
