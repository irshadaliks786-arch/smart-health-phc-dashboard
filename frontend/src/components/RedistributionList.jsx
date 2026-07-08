import React from "react";
import { api } from "../lib/api.js";
import { useFetchState } from "../lib/useFetchState.js";
import { SkeletonTable } from "../skeletons/Skeleton.jsx";
import ErrorState from "./ErrorState.jsx";

export default function RedistributionList() {
  const { status, data, error, retry } = useFetchState(
    () => api.redistribution("HIGH"),
    []
  );

  return (
    <section className="panel">
      <h2>High-priority Redistribution Recommendations</h2>
      {status === "loading" && <SkeletonTable rows={4} cols={4} />}
      {status === "error" && <ErrorState message={error} onRetry={retry} />}
      {status === "success" && (
        <table className="data-table">
          <thead>
            <tr>
              <th>Medicine</th>
              <th>Deficit PHC</th>
              <th>Surplus PHC</th>
              <th>Transfer qty</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, i) => (
              <tr key={i}>
                <td>{row.medicine_name}</td>
                <td>{row.deficit_phc}</td>
                <td>{row.surplus_phc}</td>
                <td>{row.transfer_qty}</td>
              </tr>
            ))}
            {data.length === 0 && (
              <tr>
                <td colSpan={4}>No high-priority transfers needed right now.</td>
              </tr>
            )}
          </tbody>
        </table>
      )}
    </section>
  );
}
