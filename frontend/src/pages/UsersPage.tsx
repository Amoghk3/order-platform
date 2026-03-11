import { useEffect, useState } from "react";
import client from "../api/client";
import type { User, Role } from "../types";

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const [uRes, rRes] = await Promise.all([
        client.get<User[]>("/users"),
        client.get<Role[]>("/rbac/roles"),
      ]);
      setUsers(uRes.data);
      setRoles(rRes.data);
    } catch (e) {
      console.error("Failed to load users/roles", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleRoleChange = async (userId: number, roleId: number) => {
    try {
      await client.put(`/rbac/users/${userId}/role`, { role_id: roleId });
      // update local state optimistic
      setUsers((prev) =>
        prev.map((u) => {
          if (u.id === userId) {
            const newRole = roles.find((r) => r.id === roleId) || u.role;
            return { ...u, role: newRole };
          }
          return u;
        })
      );
    } catch (e: any) {
      alert("Failed to change role: " + (e.response?.data?.detail ?? "Unknown error"));
      fetchData(); // revert
    }
  };

  return (
    <div style={{ animation: "fadeUp 0.4s ease" }}>
      <div className="page-header">
        <div>
          <h2>User Management</h2>
          <p className="page-subtitle">View users and assign roles</p>
        </div>
      </div>

      <div className="glass-card">
        {loading ? (
          <div style={{ textAlign: "center", padding: "2rem" }}>
            <span className="spinner" />
          </div>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Email</th>
                  <th>Status</th>
                  <th>Created At</th>
                  <th>Role</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id}>
                    <td>#{u.id}</td>
                    <td>{u.email}</td>
                    <td>
                      <span
                        className="status-badge"
                        style={{ background: u.is_active ? "var(--success)" : "var(--text-muted)" }}
                      >
                        {u.is_active ? "Active" : "Inactive"}
                      </span>
                    </td>
                    <td>{new Date(u.created_at).toLocaleDateString()}</td>
                    <td>
                      <select
                        className="form-input"
                        style={{ padding: "0.4rem 0.5rem", width: "150px" }}
                        value={u.role.id}
                        onChange={(e) => handleRoleChange(u.id, parseInt(e.target.value))}
                      >
                        {roles.map((r) => (
                          <option key={r.id} value={r.id}>
                            {r.name}
                          </option>
                        ))}
                      </select>
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
