import { useEffect, useState, type FormEvent } from "react";
import client from "../api/client";
import type { Role, Permission } from "../types";

export default function RbacPage() {
  const [roles, setRoles] = useState<Role[]>([]);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [rolePerms, setRolePerms] = useState<Record<number, Permission[]>>({});
  const [loading, setLoading] = useState(true);

  const [newRoleName, setNewRoleName] = useState("");
  const [newPermName, setNewPermName] = useState("");

  const fetchData = async () => {
    try {
      const [rRes, pRes] = await Promise.all([
        client.get<Role[]>("/rbac/roles"),
        client.get<Permission[]>("/rbac/permissions"),
      ]);
      setRoles(rRes.data);
      setPermissions(pRes.data);

      // fetch mapping for each role
      const mapping: Record<number, Permission[]> = {};
      for (const role of rRes.data) {
        const perms = await client.get<Permission[]>(`/rbac/roles/${role.id}/permissions`);
        mapping[role.id] = perms.data;
      }
      setRolePerms(mapping);
    } catch (e) {
      console.error("Failed to fetch RBAC data", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreateRole = async (e: FormEvent) => {
    e.preventDefault();
    if (!newRoleName) return;
    try {
      await client.post("/rbac/roles", { name: newRoleName, description: "Created via API" });
      setNewRoleName("");
      fetchData();
    } catch (e: any) {
      alert(e.response?.data?.detail ?? "Failed to create role");
    }
  };

  const handleDeleteRole = async (roleId: number) => {
    if (!confirm("Are you sure you want to delete this role?")) return;
    try {
      await client.delete(`/rbac/roles/${roleId}`);
      fetchData();
    } catch (e: any) {
      alert(e.response?.data?.detail ?? "Failed to delete role");
    }
  };

  const handleCreatePerm = async (e: FormEvent) => {
    e.preventDefault();
    if (!newPermName) return;
    try {
      await client.post("/rbac/permissions", { name: newPermName, description: "Created via API" });
      setNewPermName("");
      fetchData();
    } catch (e: any) {
      alert(e.response?.data?.detail ?? "Failed to create permission");
    }
  };

  const handleAssignPerm = async (roleId: number, permId: number) => {
    try {
      await client.post(`/rbac/roles/${roleId}/permissions`, { permission_id: permId });
      fetchData();
    } catch (e: any) {
      alert(e.response?.data?.detail ?? "Failed to assign permission");
    }
  };

  const handleRemovePerm = async (roleId: number, permId: number) => {
    try {
      await client.delete(`/rbac/roles/${roleId}/permissions/${permId}`);
      fetchData();
    } catch (e: any) {
      alert(e.response?.data?.detail ?? "Failed to remove permission");
    }
  };

  return (
    <div style={{ animation: "fadeUp 0.4s ease" }}>
      <div className="page-header">
        <div>
          <h2>RBAC Management</h2>
          <p className="page-subtitle">Manage Roles, Permissions, and their assignments</p>
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: "center", padding: "2rem" }}>
          <span className="spinner" />
        </div>
      ) : (
        <div className="rbac-grid">
          {/* Roles Column */}
          <div className="rbac-column">
            <div className="glass-card" style={{ marginBottom: "1.5rem" }}>
              <h3 style={{ marginBottom: "1rem", fontWeight: 600 }}>Create Role</h3>
              <form onSubmit={handleCreateRole} className="inline-form">
                <input
                  type="text"
                  className="form-input"
                  placeholder="Role name (e.g. manager)"
                  value={newRoleName}
                  onChange={(e) => setNewRoleName(e.target.value)}
                  required
                />
                <button type="submit" className="btn btn-primary">Add Role</button>
              </form>
            </div>

            <div className="glass-card rbac-section">
              <h3 style={{ marginBottom: "1rem", fontWeight: 600 }}>Roles & Assignments</h3>
              <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
                {roles.map(r => {
                  const assignedPerms = rolePerms[r.id] || [];
                  const unassignedPerms = permissions.filter(p => !assignedPerms.find(ap => ap.id === p.id));

                  return (
                    <div key={r.id} style={{ padding: "1rem", background: "var(--bg-elevated)", borderRadius: "var(--radius-sm)", border: "1px solid var(--glass-border)" }}>
                      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: ".5rem" }}>
                        <span style={{ fontWeight: 600 }}>{r.name}</span>
                        <button className="btn btn-ghost btn-sm" style={{ color: "var(--danger)" }} onClick={() => handleDeleteRole(r.id)}>Delete</button>
                      </div>
                      
                      <div className="tag-list" style={{ marginBottom: "1rem" }}>
                        {assignedPerms.length === 0 && <span style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>No permissions assigned</span>}
                        {assignedPerms.map(p => (
                          <span key={p.id} className="tag">
                            {p.name}
                            <button onClick={() => handleRemovePerm(r.id, p.id)}>×</button>
                          </span>
                        ))}
                      </div>

                      <select 
                        className="form-input" 
                        style={{ padding: "0.3rem 0.5rem", fontSize: "0.8rem" }}
                        value="" 
                        onChange={(e) => {
                          if (e.target.value) handleAssignPerm(r.id, parseInt(e.target.value));
                        }}
                      >
                        <option value="">+ Assign Permission</option>
                        {unassignedPerms.map(p => (
                          <option key={p.id} value={p.id}>{p.name}</option>
                        ))}
                      </select>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>

          {/* Permissions Column */}
          <div className="rbac-column">
            <div className="glass-card" style={{ marginBottom: "1.5rem" }}>
              <h3 style={{ marginBottom: "1rem", fontWeight: 600 }}>Create Permission</h3>
              <form onSubmit={handleCreatePerm} className="inline-form">
                <input
                  type="text"
                  className="form-input"
                  placeholder="Perm name (e.g. orders:read)"
                  value={newPermName}
                  onChange={(e) => setNewPermName(e.target.value)}
                  required
                />
                <button type="submit" className="btn btn-primary">Add Perm</button>
              </form>
            </div>

            <div className="glass-card rbac-section">
              <h3 style={{ marginBottom: "1rem", fontWeight: 600 }}>All Permissions ({permissions.length})</h3>
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Name</th>
                    </tr>
                  </thead>
                  <tbody>
                    {permissions.map(p => (
                      <tr key={p.id}>
                        <td>#{p.id}</td>
                        <td>{p.name}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
