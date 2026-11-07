import { useEffect, useState } from "react";

const API = "http://127.0.0.1:8000";

export default function App() {
  const [tickets, setTickets] = useState([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");

  const load = async () => {
    const res = await fetch(`${API}/tickets`);
    setTickets(await res.json());
  };
  useEffect(() => { load(); }, []);

  const create = async (e) => {
    e.preventDefault();
    await fetch(`${API}/tickets`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, description, created_by: 1 }),
    });
    setTitle(""); setDescription("");
    load();
  };

  const act = async (id, action) => {          // action = "triage" or "approve"
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
