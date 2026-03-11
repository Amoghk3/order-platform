import { useEffect, useState } from "react";
import client from "../api/client";
import type { Order, OrderListResponse } from "../types";
import StatusBadge from "../components/StatusBadge";

export default function AllOrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  // Pagination & Filters
  const [page, setPage] = useState(1);
  const limit = 10;
  const [statusFilter, setStatusFilter] = useState("");

  const fetchOrders = () => {
    setLoading(true);
    const offset = (page - 1) * limit;
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString(),
    });
    if (statusFilter) {
      params.append("status", statusFilter);
    }

    client
      .get<OrderListResponse>(`/orders?${params.toString()}`)
      .then((r) => {
        setOrders(r.data.items);
        setTotal(r.data.total);
      })
      .catch((e) => console.error("Failed to load orders", e))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchOrders();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, statusFilter]);

  const handleStatusChange = async (orderId: number, newStatus: string) => {
    try {
      await client.patch(`/orders/${orderId}/status`, { status: newStatus });
      fetchOrders();
    } catch (e: any) {
      alert("Failed to update status: " + (e.response?.data?.detail ?? "Unknown error"));
    }
  };

  const totalPages = Math.ceil(total / limit) || 1;

  return (
    <div style={{ animation: "fadeUp 0.4s ease" }}>
      <div className="page-header">
        <div>
          <h2>All Orders (Admin)</h2>
          <p className="page-subtitle">Manage all user orders across the platform</p>
        </div>
      </div>

      <div className="glass-card">
        <div className="filters-row">
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label htmlFor="status-filter">Filter by Status</label>
            <select
              id="status-filter"
              className="form-input"
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(1); // Reset to page 1 on filter
              }}
            >
              <option value="">All Statuses</option>
              <option value="PENDING">Pending</option>
              <option value="CONFIRMED">Confirmed</option>
              <option value="PROCESSING">Processing</option>
              <option value="COMPLETED">Completed</option>
              <option value="CANCELLED">Cancelled</option>
            </select>
          </div>
        </div>

        {loading ? (
          <div style={{ textAlign: "center", padding: "2rem" }}>
            <span className="spinner" />
          </div>
        ) : orders.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📭</div>
            <p>No orders found matching the filter.</p>
          </div>
        ) : (
          <>
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>User ID</th>
                    <th>Amount</th>
                    <th>Status</th>
                    <th>Created</th>
                    <th>Update Status</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.map((o) => (
                    <tr key={o.id}>
                      <td>#{o.id}</td>
                      <td>{o.user_id}</td>
                      <td>${parseFloat(o.total_amount).toFixed(2)}</td>
                      <td>
                        <StatusBadge status={o.status} />
                      </td>
                      <td>{new Date(o.created_at).toLocaleDateString()}</td>
                      <td>
                        <select
                          className="form-input"
                          style={{ padding: "0.4rem 0.5rem", width: "130px" }}
                          value={o.status}
                          onChange={(e) => handleStatusChange(o.id, e.target.value)}
                          disabled={o.status === "CANCELLED"}
                        >
                          <option value="PENDING">Pending</option>
                          <option value="CONFIRMED">Confirmed</option>
                          <option value="PROCESSING">Processing</option>
                          <option value="COMPLETED">Completed</option>
                          <option value="CANCELLED">Cancelled</option>
                        </select>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="pagination">
              <button
                className="btn btn-ghost btn-sm"
                disabled={page === 1}
                onClick={() => setPage(p => p - 1)}
              >
                Previous
              </button>
              <span className="pagination-info">
                Page {page} of {totalPages} (Total: {total})
              </span>
              <button
                className="btn btn-ghost btn-sm"
                disabled={page === totalPages}
                onClick={() => setPage(p => p + 1)}
              >
                Next
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
