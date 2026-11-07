import { useEffect, useState } from "react";

const API = "http://127.0.0.1:8000";

export default function App() {
  const [tickets, setTickets] = useState([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");  // "" = All
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const load = async (signal) => {
    setLoading(true);
    setError("");
    try {
      const params = new URLSearchParams();
      if (statusFilter) params.set("status", statusFilter);
      if (search) params.set("search", search);
      const res = await fetch(`${API}/tickets?${params}`, { signal });
      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      setTickets(await res.json());
    } catch (err) {
      // 被取消的请求也会抛错，但那是故意的，不能当成真错误显示
      if (err.name !== "AbortError") setError("Failed to load tickets.");
    } finally {
      if (!signal || !signal.aborted) setLoading(false);
    }
  };

  // 搜索词或筛选变化时：等 300ms 再发请求（debounce），
  // 并且新变化一来，就取消上一个还没回来的请求（防竞态）
  useEffect(() => {
    const controller = new AbortController();
    const timer = setTimeout(() => load(controller.signal), 300);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [search, statusFilter]);

  const create = async (e) => {
    e.preventDefault();
    await fetch(`${API}/tickets`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, description, created_by: 1 }),
    });
    setTitle(""); setDescription("");
    load();                       // 按钮操作不用等 debounce，立刻刷新
  };

  const act = async (id, action) => {
    await fetch(`${API}/tickets/${id}/${action}`, { method: "POST" });
    load();
  };

  return (
    <div>
      <h1>Support Tickets</h1>
      <form onSubmit={create}>
        <input value={title} onChange={(e) => setTitle(e.target.value)}
               placeholder="Title" required />
        <input value={description} onChange={(e) => setDescription(e.target.value)}
               placeholder="Description" required />
        <button type="submit">Submit ticket</button>
      </form>

      <div style={{ margin: "12px 0" }}>
        <input value={search} onChange={(e) => setSearch(e.target.value)}
               placeholder="Search tickets..." />
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="">All</option>
          <option value="open">open</option>
          <option value="needs_review">needs_review</option>
          <option value="assigned">assigned</option>
        </select>
      </div>

      {loading && <div>Loading...</div>}
      {error && <div style={{ color: "red" }}>{error}</div>}
      {!loading && tickets.length === 0 && <div>No tickets found.</div>}

      {tickets.map((t) => (
        <div key={t.id} style={{ border: "1px solid #ccc", margin: 8, padding: 8 }}>
          <b>#{t.id} {t.title}</b> — {t.status}
          <div>{t.description}</div>
          {t.ai_summary && (
            <div>
              AI suggests: {t.suggested_category} / {t.suggested_priority}
              <br />Summary: {t.ai_summary}
            </div>
          )}
          {t.status === "open" && (
            <button onClick={() => act(t.id, "triage")}>Run AI triage</button>
          )}
          {t.status === "needs_review" && (
            <button onClick={() => act(t.id, "approve")}>Approve</button>
          )}
          {t.status === "assigned" && (
            <div>Final: {t.category} / {t.priority}</div>
          )}
        </div>
      ))}
    </div>
  );
}
