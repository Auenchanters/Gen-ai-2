import { type FormEvent, useState } from "react";
import { ask } from "../api";
import type { AskResponse } from "../types";

export function AskBox() {
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState<AskResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (question.trim().length < 3) {
      setError("Please enter at least 3 characters.");
      return;
    }
    setError("");
    setLoading(true);
    setResponse(null);
    try {
      setResponse(await ask(question));
    } catch {
      setError("Could not get an answer. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section aria-labelledby="ask-heading">
      <h2 id="ask-heading">Ask about grid risk</h2>
      <form onSubmit={onSubmit}>
        <label htmlFor="question">Your question</label>
        <textarea
          id="question"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          aria-describedby="question-hint"
          rows={2}
          maxLength={500}
        />
        <p id="question-hint">Example: which zones are at risk this evening?</p>
        <button type="submit" disabled={loading} aria-busy={loading}>
          {loading ? "Asking…" : "Ask"}
        </button>
      </form>
      <div role="status" aria-live="polite">
        {error && <p className="error">{error}</p>}
        {response && (
          <p>
            {response.answer} <span className="source">[source: {response.source}]</span>
          </p>
        )}
      </div>
    </section>
  );
}
