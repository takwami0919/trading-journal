
import Link from "next/link";
import { notFound } from "next/navigation";
import DemoJournalEditor from "../../../components/DemoJournalEditor";

type Trade = {
  id: string;
  symbol: string;
  direction: string;
  status: string;
  quantity: number;
  remaining_quantity: number;
  entry_price: number;
  exit_price: number | null;
  entry_time: string;
  exit_time: string | null;
  gross_pnl: number | null;
  fees: number;
  net_pnl: number | null;
};

type DemoTrade = Trade & {
  strategy: string;
  notes: string;
  lesson: string;
};

type Props = {
  params: Promise<{ tradeId: string }>;
};

const API_URL = "http://127.0.0.1:8000";

// Simulated trades used only for Demo Mode.
const demoTrades: Record<string, DemoTrade> = {
  "demo-1": {
    id: "demo-1",
    symbol: "AAPL",
    direction: "long",
    status: "closed",
    quantity: 10,
    remaining_quantity: 0,
    entry_price: 210,
    exit_price: 218.52,
    entry_time: "2026-11-09T10:00:00-06:00",
    exit_time: "2026-11-09T14:30:00-06:00",
    gross_pnl: 85.2,
    fees: 0,
    net_pnl: 85.2,
    strategy: "Breakout Trading",
    notes:
      "Entered after a simulated breakout above resistance. Price continued higher, and the position reached the planned exit.",
    lesson:
      "Having a clear entry and exit plan helps avoid emotional decisions.",
  },

  "demo-2": {
    id: "demo-2",
    symbol: "MSFT",
    direction: "long",
    status: "closed",
    quantity: 5,
    remaining_quantity: 0,
    entry_price: 425,
    exit_price: 420.5,
    entry_time: "2026-11-10T09:45:00-06:00",
    exit_time: "2026-11-10T13:15:00-06:00",
    gross_pnl: -22.5,
    fees: 0,
    net_pnl: -22.5,
    strategy: "Momentum Trading",
    notes:
      "Entered expecting upward momentum, but the simulated price moved against the position.",
    lesson:
      "A losing trade can still follow a good process when risk is controlled.",
  },

  "demo-3": {
    id: "demo-3",
    symbol: "NVDA",
    direction: "long",
    status: "closed",
    quantity: 8,
    remaining_quantity: 0,
    entry_price: 140,
    exit_price: 154.05,
    entry_time: "2026-11-11T10:15:00-06:00",
    exit_time: "2026-11-11T15:00:00-06:00",
    gross_pnl: 112.4,
    fees: 0,
    net_pnl: 112.4,
    strategy: "Trend Following",
    notes:
      "The simulated trade followed an established upward trend. The position was closed after reaching the target.",
    lesson:
      "Waiting for confirmation can improve trade selection.",
  },

  "demo-4": {
    id: "demo-4",
    symbol: "TSLA",
    direction: "long",
    status: "closed",
    quantity: 6,
    remaining_quantity: 0,
    entry_price: 250,
    exit_price: 243.75,
    entry_time: "2026-11-12T09:50:00-06:00",
    exit_time: "2026-11-12T12:20:00-06:00",
    gross_pnl: -37.5,
    fees: 0,
    net_pnl: -37.5,
    strategy: "Support Bounce",
    notes:
      "Entered near a simulated support level, but the price broke below support instead of bouncing.",
    lesson:
      "Support levels can fail, so defining risk before entry is important.",
  },

  "demo-5": {
    id: "demo-5",
    symbol: "AMD",
    direction: "long",
    status: "closed",
    quantity: 12,
    remaining_quantity: 0,
    entry_price: 155,
    exit_price: 161.4,
    entry_time: "2026-11-13T10:30:00-06:00",
    exit_time: "2026-11-13T14:45:00-06:00",
    gross_pnl: 76.8,
    fees: 0,
    net_pnl: 76.8,
    strategy: "Breakout Trading",
    notes:
      "Bought after simulated resistance was broken. The trade moved steadily upward before reaching the profit target.",
    lesson:
      "Following a predefined strategy makes performance easier to evaluate.",
  },

  "demo-6": {
    id: "demo-6",
    symbol: "AMZN",
    direction: "long",
    status: "closed",
    quantity: 5,
    remaining_quantity: 0,
    entry_price: 195,
    exit_price: 209.02,
    entry_time: "2026-11-16T10:00:00-06:00",
    exit_time: "2026-11-16T14:15:00-06:00",
    gross_pnl: 70.1,
    fees: 0,
    net_pnl: 70.1,
    strategy: "Trend Following",
    notes:
      "Entered during a simulated upward move and closed the trade after the target was reached.",
    lesson:
      "Documenting why a trade was entered makes future reviews more useful.",
  },
};

// Load real trades from FastAPI.
async function getTrade(
  tradeId: string
): Promise<Trade | null> {
  const response = await fetch(
    `${API_URL}/trades/${encodeURIComponent(tradeId)}`,
    {
      cache: "no-store",
    }
  );

  if (response.status === 404) {
    return null;
  }

  if (!response.ok) {
    throw new Error("Failed to load trade details");
  }

  return response.json();
}

function money(value: number | null | undefined) {
  if (value === null || value === undefined) {
    return "—";
  }

  const amount = Number(value);

  return `${amount < 0 ? "-" : ""}$${Math.abs(
    amount
  ).toFixed(2)}`;
}

function formatDate(value: string | null) {
  if (!value) {
    return "Still open";
  }

  return new Date(value).toLocaleString("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "America/Chicago",
  });
}

export default async function TradeDetails({
  params,
}: Props) {
  const { tradeId } = await params;

  const isDemo = tradeId.startsWith("demo-");

  const trade: Trade | null = isDemo
    ? demoTrades[tradeId] ?? null
    : await getTrade(tradeId);

  if (!trade) {
    notFound();
  }

  const demoTrade = isDemo
    ? demoTrades[tradeId]
    : null;

  const backUrl = isDemo
    ? "/?mode=demo"
    : "/?mode=live";

  return (
    <main className="min-h-screen bg-[#0b1120] p-6 text-white md:p-10">

      {/* BACK BUTTON */}
      <Link
        href={backUrl}
        className="mb-8 inline-block text-blue-400 hover:underline"
      >
        ← Back to Dashboard
      </Link>

      {/* HEADER */}
      <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold">
            {trade.symbol}
          </h1>

          <p className="mt-2 text-gray-400">
            Trade Details
          </p>
        </div>

        <div className="flex items-center gap-3">
          {isDemo && (
            <span className="rounded-full bg-purple-900 px-4 py-2 text-sm font-semibold text-purple-200">
              Simulated Trade
            </span>
          )}

          <span className="rounded-lg bg-[#1e293b] px-4 py-2 capitalize">
            {trade.status}
          </span>
        </div>
      </div>

      {/* DEMO NOTICE */}
      {isDemo && (
        <div className="mb-8 rounded-lg border border-purple-800 bg-purple-950/50 p-4 text-purple-200">
          This is an illustrative trade created for
          Demo Mode. Its prices and performance are
          simulated. Journal notes are stored locally
          in your browser.
        </div>
      )}

      {/* STATISTICS */}
      <div className="grid gap-6 md:grid-cols-3">
        <div className="rounded-xl bg-[#1e293b] p-6">
          <p className="text-gray-400">
            Direction
          </p>

          <h2 className="mt-2 text-2xl font-bold capitalize">
            {trade.direction}
          </h2>
        </div>

        <div className="rounded-xl bg-[#1e293b] p-6">
          <p className="text-gray-400">
            Quantity
          </p>

          <h2 className="mt-2 text-2xl font-bold">
            {trade.quantity}
          </h2>
        </div>

        <div className="rounded-xl bg-[#1e293b] p-6">
          <p className="text-gray-400">
            Net P&amp;L
          </p>

          <h2
            className={`mt-2 text-2xl font-bold ${
              trade.net_pnl === null
                ? "text-white"
                : trade.net_pnl >= 0
                  ? "text-green-400"
                  : "text-red-400"
            }`}
          >
            {money(trade.net_pnl)}
          </h2>
        </div>
      </div>

      {/* TRADE INFORMATION */}
      <section className="mt-8 rounded-xl bg-[#1e293b] p-6">
        <h2 className="mb-6 text-2xl font-semibold">
          Trade Information
        </h2>

        <div className="grid gap-6 md:grid-cols-2">
          <div>
            <p className="text-gray-400">Entry Price</p>
            <p className="mt-1 text-xl">
              {money(trade.entry_price)}
            </p>
          </div>

          <div>
            <p className="text-gray-400">Exit Price</p>
            <p className="mt-1 text-xl">
              {money(trade.exit_price)}
            </p>
          </div>

          <div>
            <p className="text-gray-400">
              Remaining Quantity
            </p>
            <p className="mt-1 text-xl">
              {trade.remaining_quantity}
            </p>
          </div>

          <div>
            <p className="text-gray-400">Gross P&amp;L</p>
            <p className="mt-1 text-xl">
              {money(trade.gross_pnl)}
            </p>
          </div>

          <div>
            <p className="text-gray-400">Fees</p>
            <p className="mt-1 text-xl">
              {money(trade.fees)}
            </p>
          </div>

          <div>
            <p className="text-gray-400">Status</p>
            <p className="mt-1 text-xl capitalize">
              {trade.status}
            </p>
          </div>
        </div>
      </section>

      {/* TRADE TIMELINE */}
      <section className="mt-8 rounded-xl bg-[#1e293b] p-6">
        <h2 className="mb-6 text-2xl font-semibold">
          Trade Timeline
        </h2>

        <div className="space-y-4">
          <div>
            <p className="text-sm text-gray-400">
              Entry
            </p>

            <p className="mt-1 text-lg">
              {formatDate(trade.entry_time)}
            </p>
          </div>

          <div>
            <p className="text-sm text-gray-400">
              Exit
            </p>

            <p className="mt-1 text-lg">
              {formatDate(trade.exit_time)}
            </p>
          </div>
        </div>
      </section>

      {/* EDITABLE DEMO JOURNAL */}
      {demoTrade && (
        <DemoJournalEditor
          tradeId={demoTrade.id}
          initialStrategy={demoTrade.strategy}
          initialNotes={demoTrade.notes}
          initialLesson={demoTrade.lesson}
        />
      )}

      {/* FOOTER */}
      <div className="mt-8">
        <Link
          href={backUrl}
          className="inline-block rounded-lg bg-blue-600 px-6 py-3 font-semibold transition hover:bg-blue-500"
        >
          ← Back to Dashboard
        </Link>
      </div>
    </main>
  );
}
