
"use client";

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type PerformancePoint = {
  date: string;
  symbol: string;
  trade_pnl: number;
  cumulative_pnl: number;
};

type Props = {
  data: PerformancePoint[];
};

export default function PerformanceChart({ data }: Props) {
  return (
    <section className="mt-10 rounded-xl bg-[#1e293b] p-6">
      <h2 className="mb-2 text-2xl font-semibold text-white">
        Trading Performance
      </h2>

      <p className="mb-6 text-gray-400">
        Cumulative realized profit and loss over time
      </p>

      {data.length === 0 ? (
        <div className="flex h-72 items-center justify-center rounded-lg border border-dashed border-gray-600">
          <div className="text-center">
            <p className="text-lg text-gray-300">
              No closed trades yet.
            </p>

            <p className="mt-2 text-sm text-gray-400">
              Your performance chart will appear once you close a trade.
            </p>
          </div>
        </div>
      ) : (
        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={data}
              margin={{
                top: 10,
                right: 20,
                left: 10,
                bottom: 10,
              }}
            >
              <CartesianGrid
                stroke="#334155"
                strokeDasharray="3 3"
              />

              <XAxis
                dataKey="date"
                stroke="#94a3b8"
                tickFormatter={(value: string) =>
                  new Date(value).toLocaleDateString()
                }
              />

              <YAxis
                stroke="#94a3b8"
                tickFormatter={(value: number) =>
                  `$${value}`
                }
              />

              <Tooltip
                labelFormatter={(value) =>
                  new Date(String(value)).toLocaleString()
                }
                formatter={(value) => [
                  `$${Number(value).toFixed(2)}`,
                  "Cumulative P&L",
                ]}
                contentStyle={{
                  backgroundColor: "#0f172a",
                  border: "1px solid #334155",
                  borderRadius: "8px",
                  color: "#ffffff",
                }}
              />

              <Line
                type="monotone"
                dataKey="cumulative_pnl"
                stroke="#38bdf8"
                strokeWidth={3}
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </section>
  );
}
