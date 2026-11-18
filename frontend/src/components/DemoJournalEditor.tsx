
"use client";
import { useEffect, useState } from "react";

type Props = {
  tradeId: string;
  initialStrategy: string;
  initialNotes: string;
  initialLesson: string;
};

type JournalData = {
  strategy: string;
  notes: string;
  lesson: string;
};

export default function DemoJournalEditor({
  tradeId,
  initialStrategy,
  initialNotes,
  initialLesson,
}: Props) {
  const [strategy, setStrategy] = useState(initialStrategy);
  const [notes, setNotes] = useState(initialNotes);
  const [lesson, setLesson] = useState(initialLesson);
  const [loaded, setLoaded] = useState(false);
  const [status, setStatus] = useState("");

  const storageKey = `trading-journal-demo-${tradeId}`;

  useEffect(() => {
    try {
      const saved = localStorage.getItem(storageKey);

      if (saved) {
        const data: JournalData = JSON.parse(saved);

        setStrategy(data.strategy ?? initialStrategy);
        setNotes(data.notes ?? initialNotes);
        setLesson(data.lesson ?? initialLesson);
      }
    } catch (error) {
      console.error("Could not load demo notes:", error);
    }

    setLoaded(true);
  }, [
    storageKey,
    initialStrategy,
    initialNotes,
    initialLesson,
  ]);

  function saveNotes() {
    const data: JournalData = {
      strategy,
      notes,
      lesson,
    };

    try {
      localStorage.setItem(
        storageKey,
        JSON.stringify(data)
      );

      setStatus("Notes saved successfully!");
    } catch (error) {
      console.error("Could not save demo notes:", error);
      setStatus("Unable to save notes in this browser.");
    }
  }

  function resetNotes() {
    setStrategy(initialStrategy);
    setNotes(initialNotes);
    setLesson(initialLesson);

    try {
      localStorage.removeItem(storageKey);
      setStatus("Sample notes restored.");
    } catch (error) {
      console.error("Could not reset notes:", error);
      setStatus("Unable to reset saved notes.");
    }
  }

  function markUnsaved() {
    setStatus("Unsaved changes");
  }

  return (
    <section className="mt-8 rounded-xl bg-[#1e293b] p-6">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-2xl font-semibold">
          Trading Journal
        </h2>

        <span className="rounded-full bg-purple-900 px-3 py-1 text-xs font-semibold text-purple-200">
          Editable Demo Notes
        </span>
      </div>

      <div className="space-y-6">
        <div>
          <label
            htmlFor="demo-strategy"
            className="mb-2 block font-semibold text-gray-300"
          >
            Strategy
          </label>

          <input
            id="demo-strategy"
            type="text"
            value={strategy}
            disabled={!loaded}
            onChange={(event) => {
              setStrategy(event.target.value);
              markUnsaved();
            }}
            className="w-full rounded-lg border border-gray-600 bg-[#0b1120] p-3 text-white outline-none focus:border-purple-500"
            placeholder="Enter your trading strategy"
          />
        </div>

        <div>
          <label
            htmlFor="demo-notes"
            className="mb-2 block font-semibold text-gray-300"
          >
            Trade Notes
          </label>

          <textarea
            id="demo-notes"
            value={notes}
            disabled={!loaded}
            onChange={(event) => {
              setNotes(event.target.value);
              markUnsaved();
            }}
            rows={5}
            className="w-full resize-y rounded-lg border border-gray-600 bg-[#0b1120] p-3 text-white outline-none focus:border-purple-500"
            placeholder="Why did you enter this trade?"
          />
        </div>

        <div>
          <label
            htmlFor="demo-lesson"
            className="mb-2 block font-semibold text-gray-300"
          >
            Lessons Learned
          </label>

          <textarea
            id="demo-lesson"
            value={lesson}
            disabled={!loaded}
            onChange={(event) => {
              setLesson(event.target.value);
              markUnsaved();
            }}
            rows={4}
            className="w-full resize-y rounded-lg border border-gray-600 bg-[#0b1120] p-3 text-white outline-none focus:border-purple-500"
            placeholder="What did you learn from this trade?"
          />
        </div>
      </div>

      <div className="mt-6 flex flex-wrap items-center gap-4">
        <button
          type="button"
          onClick={saveNotes}
          disabled={!loaded}
          className="rounded-lg bg-purple-600 px-6 py-3 font-semibold text-white transition hover:bg-purple-500 disabled:opacity-50"
        >
          Save Notes
        </button>

        <button
          type="button"
          onClick={resetNotes}
          disabled={!loaded}
          className="rounded-lg border border-gray-600 px-6 py-3 font-semibold text-gray-300 transition hover:bg-gray-700 disabled:opacity-50"
        >
          Reset to Sample
        </button>

        {status && (
          <p
            role="status"
            className={
              status.includes("successfully")
                ? "text-sm text-green-400"
                : "text-sm text-gray-300"
            }
          >
            {status}
          </p>
        )}
      </div>

      <p className="mt-5 text-sm text-gray-400">
        Demo notes are stored in this browser only.
        They are not sent to Alpaca or PostgreSQL.
      </p>
    </section>
  );
}
