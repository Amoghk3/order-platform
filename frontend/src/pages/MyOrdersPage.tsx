import { useEffect, useState, type FormEvent } from "react";
import client from "../api/client";
import type { Order } from "../types";
import StatusBadge from "../components/StatusBadge";

export default function MyOrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);

  // New order form
  const [amount, setAmount] = useState("");
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const fetchOrders = () => {
    client
      .get<Order[]>("/orders/me")
      .then((r) => setOrders(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  const handleCreate = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    const parsed = parseFloat(amount);
    if (isNaN(parsed) || parsed <= 0) {
      setError("Enter a valid amount");
      return;
    }
    setCreating(true);
    try {
      await client.post("/orders", { total_amount: parsed });
      setSuccess("Order created!");
      setAmount("");
      fetchOrders();
    } catch (err: any) {
      setError(err.response?.data?.detail ?? "Failed to create order");
    } finally {
      setCreating(false);
    }
  };

  const handleCancel = async (orderId: number) => {
    try {
      await client.post(`/orders/${orderId}/cancel`);
      fetchOrders();
    } catch (err: any) {
      setError(err.response?.data?.detail ?? "Cancel failed");
    }
  };

  return (
    <div style={{ animation: "fadeUp 0.4s ease" }}>
      <div className="page-header">
        <div>
          <h2>My Orders</h2>
          <p className="page-subtitle">Create and manage your orders</p>
        </div>
      </div>

      {/* New order form */}
      <div className="glass-card" style={{ marginBottom: "1.5rem" }}>
        <h3 style={{ marginBottom: "1rem", fontWeight: 600 }}>
          New Order
        </h3>
        {error && <div className="alert-error">{error}</div>}
        {success && <div className="alert-success">{success}</div>}
        <form onSubmit={handleCreate} className="inline-form">
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label htmlFor="order-amount">Amount ($)</label>
            <input
              id="order-amount"
              type="number"
              step="0.01"
              min="0.01"
              className="form-input"
              placeholder="99.99"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              required
            />
          </div>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={creating}
            id="btn-create-order"
          >
            {creating ? <span className="spinner" /> : "Create Order"}
          </button>
        </form>
      </div>

      {/* Orders table */}
      <div className="glass-card">
        {loading ? (
          <div style={{ textAlign: "center", padding: "2rem" }}>
            <span className="spinner" />
          </div>
        ) : orders.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🛒</div>
            <p>You haven't placed any orders yet.</p>
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
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {orders.map((o) => (
                  <tr key={o.id}>
                    <td>#{o.id}</td>
                    <td>${parseFloat(o.total_amount).toFixed(2)}</td>
                    <td>
                      <StatusBadge status={o.status} />
                    </td>
                    <td>{new Date(o.created_at).toLocaleDateString()}</td>
                    <td>
                      {o.status !== "CANCELLED" && o.status !== "COMPLETED" && (
                        <button
                          className="btn btn-danger btn-sm"
                          onClick={() => handleCancel(o.id)}
                        >
                          Cancel
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
