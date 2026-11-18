
import Link from "next/link";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import PerformanceChart from "../components/PerformanceChart";

type Analytics = {
  total_trades: number;
  open_trades: number;
  closed_trades: number;
  total_realized_pnl: number;
  win_rate: number;
};

type Trade = {
  id: string;
  symbol: string;
  direction: string;
  status: string;
  quantity: number;
  entry_price: number;
  exit_price: number | null;
  net_pnl: number | null;
};

type PerformancePoint = {
  date: string;
  symbol: string;
  trade_pnl: number;
  cumulative_pnl: number;
};

type PageProps = {
  searchParams: Promise<{
    mode?: string;
    sync?: string;
  }>;
};

const API_URL = "http://127.0.0.1:8000";

// -----------------------------------
// DEMO DATA
// Simulated trades, not real Alpaca data
// -----------------------------------

const demoTrades: Trade[] = [
  {
    id: "demo-1",
    symbol: "AAPL",
    direction: "long",
    status: "closed",
    quantity: 10,
    entry_price: 210,
    exit_price: 218.52,
    net_pnl: 85.2,
  },
  {
    id: "demo-2",
    symbol: "MSFT",
    direction: "long",
    status: "closed",
    quantity: 5,
    entry_price: 425,
    exit_price: 420.5,
    net_pnl: -22.5,
  },
  {
    id: "demo-3",
    symbol: "NVDA",
    direction: "long",
    status: "closed",
    quantity: 8,
    entry_price: 140,
    exit_price: 154.05,
    net_pnl: 112.4,
  },
  {
    id: "demo-4",
    symbol: "TSLA",
    direction: "long",
    status: "closed",
    quantity: 6,
    entry_price: 250,
    exit_price: 243.75,
    net_pnl: -37.5,
  },
  {
    id: "demo-5",
    symbol: "AMD",
    direction: "long",
    status: "closed",
    quantity: 12,
    entry_price: 155,
    exit_price: 161.4,
    net_pnl: 76.8,
  },
  {
    id: "demo-6",
    symbol: "AMZN",
    direction: "long",
    status: "closed",
    quantity: 5,
    entry_price: 195,
    exit_price: 209.02,
    net_pnl: 70.1,
  },
];

const demoPerformance: PerformancePoint[] = [
  {
    date: "2026-11-09",
    symbol: "AAPL",
    trade_pnl: 85.2,
    cumulative_pnl: 85.2,
  },
  {
    date: "2026-11-10",
    symbol: "MSFT",
    trade_pnl: -22.5,
    cumulative_pnl: 62.7,
  },
  {
    date: "2026-11-11",
    symbol: "NVDA",
    trade_pnl: 112.4,
    cumulative_pnl: 175.1,
  },
  {
    date: "2026-11-12",
    symbol: "TSLA",
    trade_pnl: -37.5,
    cumulative_pnl: 137.6,
  },
  {
    date: "2026-11-13",
    symbol: "AMD",
    trade_pnl: 76.8,
    cumulative_pnl: 214.4,
  },
  {
    date: "2026-11-16",
    symbol: "AMZN",
    trade_pnl: 70.1,
    cumulative_pnl: 284.5,
  },
];

const demoAnalytics: Analytics = {
  total_trades: 6,
  open_trades: 0,
  closed_trades: 6,
  total_realized_pnl: 284.5,
  win_rate: 66.67,
};

// -----------------------------------
// FETCH LIVE DATA FROM FASTAPI
// -----------------------------------

async function getDashboardData() {
  const [
    analyticsResponse,
    tradesResponse,
    performanceResponse,
  ] = await Promise.all([
    fetch(`${API_URL}/analytics/summary`, {
      cache: "no-store",
    }),
    fetch(`${API_URL}/trades/`, {
      cache: "no-store",
    }),
    fetch(`${API_URL}/analytics/performance`, {
      cache: "no-store",
    }),
  ]);

  if (
    !analyticsResponse.ok ||
    !tradesResponse.ok ||
    !performanceResponse.ok
  ) {
    throw new Error("Failed to load trading data");
  }

  const analytics: Analytics =
    await analyticsResponse.json();

  const trades: Trade[] =
    await tradesResponse.json();

  const performance: PerformancePoint[] =
    await performanceResponse.json();

  return {
    analytics,
    trades,
    performance,
  };
}

// -----------------------------------
// IMPORT REAL EXECUTIONS FROM ALPACA
// -----------------------------------

async function importFromAlpaca() {
  "use server";

  let success = false;

  try {
    const response = await fetch(
      `${API_URL}/executions/sync`,
      {
        method: "POST",
        cache: "no-store",
      }
    );

    success = response.ok;

    if (!response.ok) {
      console.error(
        "Alpaca import failed:",
        response.status,
        await response.text()
      );
    }
  } catch (error) {
    console.error("Alpaca import error:", error);
  }

  if (success) {
    revalidatePath("/");
    redirect("/?mode=live&sync=success");
  }

  redirect("/?mode=live&sync=error");
}

// -----------------------------------
// MAIN DASHBOARD
// -----------------------------------

export default async function Home({
  searchParams,
}: PageProps) {
  const params = await searchParams;

  const isDemo = params.mode === "demo";
  const sync = params.sync;

  // Demo Mode does not require FastAPI or PostgreSQL.
  const { analytics, trades, performance } = isDemo
    ? {
        analytics: demoAnalytics,
        trades: demoTrades,
        performance: demoPerformance,
      }
    : await getDashboardData();

  return (
    <main className="min-h-screen bg-[#0b1120] p-6 text-white md:p-10">

      {/* HEADER */}
      <div className="mb-8 flex flex-wrap items-center justify-between gap-6">
        <div>
          <h1 className="mb-2 text-4xl font-bold">
            Trading Journal
          </h1>

          <p className="text-gray-400">
            Track your trades, performance, and progress.
          </p>
        </div>

        {!isDemo && (
          <form action={importFromAlpaca}>
            <button
              type="submit"
              className="rounded-lg bg-blue-600 px-6 py-3 font-semibold text-white transition hover:bg-blue-500"
            >
              ↻ Import from Alpaca
            </button>
          </form>
        )}
      </div>

      {/* LIVE / DEMO SWITCH */}
      <div className="mb-8 flex flex-wrap items-center justify-between gap-4 rounded-xl border border-gray-700 bg-[#1e293b] p-4">

        <div className="flex flex-wrap items-center gap-3">
          <span className="font-semibold">
            Data Source:
          </span>

          <div className="flex rounded-lg bg-[#0b1120] p-1">

            <Link
              href="/?mode=live"
              className={`rounded-md px-5 py-2 text-sm font-semibold transition ${
                !isDemo
                  ? "bg-blue-600 text-white"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              Live Alpaca
            </Link>

            <Link
              href="/?mode=demo"
              className={`rounded-md px-5 py-2 text-sm font-semibold transition ${
                isDemo
                  ? "bg-purple-600 text-white"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              Demo Mode
            </Link>

          </div>
        </div>

        <span
          className={`rounded-full px-4 py-2 text-sm font-semibold ${
            isDemo
              ? "bg-purple-900 text-purple-200"
              : "bg-blue-950 text-blue-300"
          }`}
        >
          {isDemo
            ? "● Simulated Data"
            : "● Alpaca Paper Trading"}
        </span>
      </div>

      {/* DEMO INFORMATION */}
      {isDemo && (
        <div className="mb-8 rounded-lg border border-purple-800 bg-purple-950/50 p-4 text-purple-200">
          <p className="font-semibold">
            Demo Mode Active
          </p>

          <p className="mt-1 text-sm">
            You are viewing simulated trades for
            demonstration purposes. These results are
            not from your Alpaca account and are
            not stored in PostgreSQL.
          </p>
        </div>
      )}

      {/* LIVE API INFORMATION */}
      {!isDemo && (
        <div className="mb-8 rounded-xl border border-gray-700 bg-[#1e293b] p-5">
          <h2 className="mb-3 text-lg font-semibold">
            API Integration
          </h2>

          <div className="flex flex-wrap gap-3">
            <span className="rounded-lg bg-[#0b1120] px-4 py-2 text-sm text-gray-300">
              Broker: Alpaca Paper Trading
            </span>

            <span className="rounded-lg bg-[#0b1120] px-4 py-2 text-sm text-gray-300">
              Backend: FastAPI
            </span>

            <span className="rounded-lg bg-[#0b1120] px-4 py-2 text-sm text-gray-300">
              Database: PostgreSQL
            </span>
          </div>

          <p className="mt-3 text-sm text-gray-400">
            Import from Alpaca requests executions
            through the FastAPI backend and saves
            them to PostgreSQL.
          </p>

          <p className="mt-2 text-xs text-gray-500">
            Import status is displayed after synchronization.
            Connection status is not continuously monitored.
          </p>
        </div>
      )}

      {/* IMPORT STATUS */}
      {!isDemo && sync === "success" && (
        <div className="mb-8 rounded-lg border border-green-700 bg-green-950 p-4 text-green-300">
          Alpaca synchronization completed successfully!
          Your trading data has been refreshed.
        </div>
      )}

      {!isDemo && sync === "error" && (
        <div className="mb-8 rounded-lg border border-red-700 bg-red-950 p-4 text-red-300">
          Alpaca import failed. Make sure your backend
          is running and check the backend terminal.
        </div>
      )}

      {/* DASHBOARD STATISTICS */}
      <div className="grid gap-6 md:grid-cols-3">

        <div className="rounded-xl bg-[#1e293b] p-6">
          <p className="text-gray-400">
            Total Trades
          </p>

          <h2 className="mt-2 text-3xl font-bold">
            {analytics.total_trades}
          </h2>
        </div>

        <div className="rounded-xl bg-[#1e293b] p-6">
          <p className="text-gray-400">
            Win Rate
          </p>

          <h2 className="mt-2 text-3xl font-bold">
            {Number(analytics.win_rate).toFixed(2)}%
          </h2>
        </div>

        <div className="rounded-xl bg-[#1e293b] p-6">
          <p className="text-gray-400">
            Realized P&amp;L
          </p>

          <h2
            className={`mt-2 text-3xl font-bold ${
              Number(analytics.total_realized_pnl) > 0
                ? "text-green-400"
                : Number(analytics.total_realized_pnl) < 0
                  ? "text-red-400"
                  : "text-white"
            }`}
          >
            ${Number(
              analytics.total_realized_pnl
            ).toFixed(2)}
          </h2>
        </div>

      </div>

      {/* PERFORMANCE CHART */}
      <PerformanceChart data={performance} />

      {/* RECENT TRADES */}
      <section className="mt-10 rounded-xl bg-[#1e293b] p-6">

        <div className="mb-6 flex flex-wrap items-center justify-between gap-3">

          <h2 className="text-2xl font-semibold">
            Recent Trades
          </h2>

          {isDemo && (
            <span className="rounded-full bg-purple-900 px-3 py-1 text-xs font-semibold text-purple-200">
              Sample Trades
            </span>
          )}

        </div>

        <div className="overflow-x-auto">

          <table className="w-full text-left">

            <thead>
              <tr className="border-b border-gray-600 text-gray-400">
                <th className="pb-4">Symbol</th>
                <th className="pb-4">Direction</th>
                <th className="pb-4">Quantity</th>
                <th className="pb-4">Entry Price</th>
                <th className="pb-4">Exit Price</th>
                <th className="pb-4">Net P&amp;L</th>
                <th className="pb-4">Status</th>
              </tr>
            </thead>

            <tbody>
              {trades.map((trade) => (
                <tr
                  key={trade.id}
                  className="border-b border-gray-700"
                >

                  {/* CLICKABLE SYMBOL FOR BOTH MODES */}
                  <td className="py-4 font-semibold">
                    <Link
                      href={`/trades/${trade.id}`}
                      className={`hover:underline ${
                        isDemo
                          ? "text-purple-300 hover:text-purple-200"
                          : "text-blue-400 hover:text-blue-300"
                      }`}
                    >
                      {trade.symbol}
                    </Link>
                  </td>

                  {/* DIRECTION */}
                  <td className="py-4 capitalize">
                    {trade.direction}
                  </td>

                  {/* QUANTITY */}
                  <td className="py-4">
                    {trade.quantity}
                  </td>

                  {/* ENTRY PRICE */}
                  <td className="py-4">
                    ${Number(
                      trade.entry_price
                    ).toFixed(2)}
                  </td>

                  {/* EXIT PRICE */}
                  <td className="py-4">
                    {trade.exit_price === null
                      ? "—"
                      : `$${Number(
                          trade.exit_price
                        ).toFixed(2)}`}
                  </td>

                  {/* NET P&L */}
                  <td
                    className={`py-4 ${
                      trade.net_pnl === null
                        ? "text-gray-400"
                        : Number(trade.net_pnl) >= 0
                          ? "text-green-400"
                          : "text-red-400"
                    }`}
                  >
                    {trade.net_pnl === null
                      ? "—"
                      : `$${Number(
                          trade.net_pnl
                        ).toFixed(2)}`}
                  </td>

                  {/* STATUS */}
                  <td className="py-4 capitalize">
                    {trade.status}
                  </td>

                </tr>
              ))}
            </tbody>

          </table>

          {trades.length === 0 && (
            <p className="py-6 text-gray-400">
              No trades yet.
            </p>
          )}

        </div>

      </section>

      {/* DEMO FOOTER */}
      {isDemo && (
        <p className="mt-6 text-center text-sm text-gray-500">
          Demo Mode uses illustrative data only.
          Switch to Live Alpaca to view imported paper trades.
        </p>
      )}

    </main>
  );
}
