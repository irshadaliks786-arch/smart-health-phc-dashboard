import React, { useState } from "react";
import { api } from "../lib/api.js";
import { useFetchState } from "../lib/useFetchState.js";
import { SkeletonTable } from "../skeletons/Skeleton.jsx";
import ErrorState from "./ErrorState.jsx";

export default function PhcTable() {
  const [flaggedOnly, setFlaggedOnly] = useState(false);
  const { status, data, error, retry } = useFetchState(
    () => api.phcs(flaggedOnly ? { flagged_only: "true" } : {}),
    [flaggedOnly]
  );

  return (
    <section className="panel">
      <div className="panel-header">
        <h2>PHC Register</h2>
        <label className="toggle">
          <input
            type="checkbox"
            checked={flaggedOnly}
            onChange={(e) => setFlaggedOnly(e.target.checked)}
          />
          Flagged only
        </label>
      </div>

      {status === "loading" && <SkeletonTable rows={6} cols={5} />}
      {status === "error" && <ErrorState message={error} onRetry={retry} />}
      {status === "success" && (
        <table className="data-table">
          <thead>
            <tr>
              <th>PHC ID</th>
              <th>District</th>
              <th>Composite Score</th>
              <th>Status</th>
              <th>Weakest sub-score</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row) => {
              const subScores = {
                Stock: row.stock_score,
                Beds: row.bed_score,
                Attendance: row.attendance_score,
                Tests: row.test_score,
                Footfall: row.footfall_score,
              };
              const weakest = Object.entries(subScores).sort(
                (a, b) => a[1] - b[1]
              )[0];
              return (
                <tr key={row.phc_id}>
                  <td>{row.phc_id}</td>
                  <td>{row.district}</td>
                  <td>{row.composite_kpi_score.toFixed(1)}</td>
                  <td>{row.flag_status}</td>
                  <td>
                    {weakest[0]} ({weakest[1].toFixed(1)})
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </section>
  );
}
