import React from "react";
import { api } from "../lib/api.js";
import { useFetchState } from "../lib/useFetchState.js";
import { SkeletonCardGrid } from "../skeletons/Skeleton.jsx";
import ErrorState from "./ErrorState.jsx";

export default function DistrictSummary() {
  const { status, data, error, retry } = useFetchState(api.districts, []);

  return (
    <section className="panel">
      <h2>District Summary</h2>
      {status === "loading" && <SkeletonCardGrid count={5} />}
      {status === "error" && <ErrorState message={error} onRetry={retry} />}
      {status === "success" && (
        <div className="card-grid">
          {data.map((d) => (
            <div className="card" key={d.district}>
              <h3>{d.district}</h3>
              <p className="metric">{d.avg_composite_score.toFixed(1)}</p>
              <p className="metric-label">avg composite KPI ({d.n_phcs} PHCs)</p>
              <p className="badges">
                <span className="badge badge-critical">{d.n_flagged} flagged</span>
                <span className="badge badge-watch">{d.n_watch} watch</span>
              </p>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
