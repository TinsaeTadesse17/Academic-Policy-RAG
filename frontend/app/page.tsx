"use client";

import { useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import styles from "./page.module.css";

type Citation = {
  source_pdf: string;
  page_number: number | string;
  chunk_id: string;
};

type AskResponse = {
  answer: string;
  citations: Citation[];
};

export default function Home() {
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState<AskResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const submitQuestion = async (override?: string) => {
    const query = override ?? question;
    setError(null);
    setResponse(null);

    if (!query.trim()) {
      setError("Please enter a question.");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch("/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: query }),
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || "Request failed");
      }

      const data = (await res.json()) as AskResponse;
      setResponse(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setQuestion("");
    setResponse(null);
    setError(null);
    textareaRef.current?.focus();
  };

  const runTemplate = (template: string) => {
    setQuestion(template);
    submitQuestion(template);
  };

  return (
    <div className={styles.page}>
      <main className={styles.main}>
        <header className={styles.topbar}>
          <div className={styles.brand}>
            <span className={styles.brandBadge}>AI</span>
            <div>
              <p className={styles.brandTitle}>Policy Assistant</p>
              <p className={styles.brandSubtitle}>RAG-backed university QA</p>
            </div>
          </div>
          <div className={styles.topbarActions}>
            <button
              className={styles.iconButton}
              aria-label="Search"
              onClick={() => textareaRef.current?.focus()}
            >
              🔍
            </button>
            <button className={styles.primaryButton} onClick={resetForm}>
              New Question
            </button>
          </div>
        </header>

        <section className={styles.hero}>
          <div>
            <p className={styles.welcome}>👋 Welcome</p>
            <h1>Ask anything about academic rules, conduct, and policies.</h1>
            <p className={styles.subcopy}>
              Answers are grounded in official student handbooks with citations.
            </p>
          </div>
          <div className={styles.stats}>
            <div>
              <span>Sources</span>
              <strong>100+ PDFs</strong>
            </div>
            <div>
              <span>Coverage</span>
              <strong>Global</strong>
            </div>
            <div>
              <span>Mode</span>
              <strong>RAG</strong>
            </div>
          </div>
        </section>

        <section className={styles.composer}>
          <label className={styles.label} htmlFor="question">
            Ask a policy question
          </label>
          <textarea
            id="question"
            className={styles.textarea}
            placeholder="What is the policy on academic probation?"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            ref={textareaRef}
          />
          <div className={styles.composerFooter}>
            <div className={styles.chips}>
              <button
                className={styles.chip}
                onClick={() =>
                  runTemplate(
                    "What are the requirements for academic probation?"
                  )
                }
              >
                Academic rules
              </button>
              <button
                className={styles.chip}
                onClick={() =>
                  runTemplate("What is the code of conduct for students?")
                }
              >
                Conduct policy
              </button>
              <button
                className={styles.chip}
                onClick={() =>
                  runTemplate("How can I appeal a disciplinary decision?")
                }
              >
                Appeals
              </button>
              <button
                className={styles.chip}
                onClick={() =>
                  runTemplate("What are the attendance requirements?")
                }
              >
                Attendance
              </button>
            </div>
            <button
              className={styles.primaryButton}
              onClick={() => submitQuestion()}
              disabled={loading}
            >
              {loading ? "Searching..." : "Ask"}
            </button>
          </div>
          <p className={styles.hint}></p>
        </section>

        <section className={styles.quickActions}>
          <h2>Quick actions</h2>
          <div className={styles.quickGrid}>
            <button
              className={styles.quickCard}
              onClick={() =>
                runTemplate(
                  "Summarize academic standing and probation rules."
                )
              }
            >
              <span>🎓</span>
              <div>
                <strong>Academic Standing</strong>
                <p>Summary of probation and warning thresholds.</p>
              </div>
            </button>
            <button
              className={styles.quickCard}
              onClick={() =>
                runTemplate("What is the plagiarism policy and consequences?")
              }
            >
              <span>🧾</span>
              <div>
                <strong>Integrity Policy</strong>
                <p>Plagiarism rules and disciplinary actions.</p>
              </div>
            </button>
            <button
              className={styles.quickCard}
              onClick={() =>
                runTemplate("What are the grievance and appeals procedures?")
              }
            >
              <span>⚖️</span>
              <div>
                <strong>Appeals</strong>
                <p>Steps for student appeals and grievances.</p>
              </div>
            </button>
          </div>
        </section>

        {error ? (
          <section className={styles.cardError}>
            <h2>Error</h2>
            <p>{error}</p>
          </section>
        ) : null}

        {response ? (
          <section className={styles.answerCard}>
            <h2>Answer</h2>
            <div className={styles.answer}>
              <ReactMarkdown>{response.answer}</ReactMarkdown>
            </div>
            <h3>Citations</h3>
            {response.citations.length === 0 ? (
              <p className={styles.muted}>No citations returned.</p>
            ) : (
              <ul className={styles.citations}>
                {response.citations.map((citation) => (
                  <li key={citation.chunk_id}>
                    <span>{citation.source_pdf}</span>
                    <span>Page {citation.page_number}</span>
                    <span>{citation.chunk_id}</span>
                  </li>
                ))}
              </ul>
            )}
          </section>
        ) : null}
      </main>
    </div>
  );
}
