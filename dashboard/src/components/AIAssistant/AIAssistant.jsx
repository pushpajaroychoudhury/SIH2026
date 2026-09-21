import { useState } from "react";
import { Bot, Minus, Plus, Send } from "lucide-react";
import { askAssistant } from "../../services/api";
import "./AIAssistant.css";

export default function AIAssistant({ suggestedPrompts = [] }) {
  const [collapsed, setCollapsed] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);

  const send = async (text) => {
    const question = text ?? input;
    if (!question.trim() || sending) return;

    setMessages((m) => [...m, { role: "user", text: question }]);
    setInput("");
    setSending(true);

    try {
      const res = await askAssistant(question);
      setMessages((m) => [...m, { role: "assistant", text: res.answer }]);
    } catch {
      setMessages((m) => [
        ...m,
        { role: "assistant", text: "Couldn't reach the assistant service. Try again shortly." },
      ]);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className={`ai-assistant card ${collapsed ? "collapsed" : ""}`}>
      <div className="aa-header">
        <div className="aa-header-left">
          <span className="aa-icon">
            <Bot size={16} />
          </span>
          <span>AI Assistant</span>
        </div>
        <button className="aa-collapse-btn" onClick={() => setCollapsed((c) => !c)}>
          {collapsed ? <Plus size={16} /> : <Minus size={16} />}
        </button>
      </div>

      {!collapsed && (
        <>
          <div className="aa-body">
            {messages.length === 0 && (
              <div className="aa-prompts">
                {suggestedPrompts.map((p) => (
                  <button key={p} className="aa-prompt-btn" onClick={() => send(p)}>
                    {p}
                  </button>
                ))}
              </div>
            )}

            {messages.map((m, i) => (
              <div key={i} className={`aa-message ${m.role}`}>
                {m.text}
              </div>
            ))}

            {sending && <div className="aa-message assistant aa-typing">Thinking…</div>}
          </div>

          <form
            className="aa-input-row"
            onSubmit={(e) => {
              e.preventDefault();
              send();
            }}
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask me anything..."
            />
            <button type="submit" aria-label="Send" disabled={sending}>
              <Send size={15} />
            </button>
          </form>
        </>
      )}
    </div>
  );
}
