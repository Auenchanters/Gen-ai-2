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
    <div className="ask-wrap">
      <form className="ask-form" onSubmit={onSubmit}>
        <label className="ask-label" htmlFor="question">
          Your question
        </label>
        <textarea
          id="question"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          aria-describedby="question-hint"
          rows={2}
          maxLength={500}
          placeholder="e.g. Which zones are at risk this evening, and what should I do?"
        />
        <p className="hint" id="question-hint">
          Answered from the live forecast — by Gemini when enabled, else deterministic rules.
        </p>
        <button className="btn" type="submit" disabled={loading} aria-busy={loading}>
          {loading ? "Asking…" : "Ask"}
        </button>
      </form>
      <div role="status" aria-live="polite">
        {error && <p className="error">{error}</p>}
        {response && (
          <div className="answer">
            <p>{response.answer}</p>
            <span className="source">source: {response.source}</span>
          </div>
        )}
      </div>
    </div>
  );
}
