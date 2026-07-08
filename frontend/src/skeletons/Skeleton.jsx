import React from "react";

/** A single skeleton bar. Fixed size — never randomized — so it always
 * occupies exactly the space its real content will occupy. */
export function SkeletonBar({ width = "100%", height = "14px" }) {
  return <div className="skeleton-bar" style={{ width, height }} />;
}

/** Fixed number of rows/cols, matching the real table exactly, so there is
 * no layout shift when data arrives. */
export function SkeletonTable({ rows = 5, cols = 4 }) {
  return (
    <div className="skeleton-table" role="status" aria-label="Loading table">
      {Array.from({ length: rows }).map((_, r) => (
        <div className="skeleton-row" key={r}>
          {Array.from({ length: cols }).map((_, c) => (
            <SkeletonBar key={c} width={c === 0 ? "70%" : "90%"} />
          ))}
        </div>
      ))}
    </div>
  );
}

export function SkeletonCardGrid({ count = 5 }) {
  return (
    <div className="skeleton-card-grid" role="status" aria-label="Loading cards">
      {Array.from({ length: count }).map((_, i) => (
        <div className="skeleton-card" key={i}>
          <SkeletonBar width="50%" height="18px" />
          <SkeletonBar width="80%" />
          <SkeletonBar width="60%" />
        </div>
      ))}
    </div>
  );
}

export function SkeletonInsightList({ count = 3 }) {
  return (
    <div className="skeleton-insight-list" role="status" aria-label="Loading insights">
      {Array.from({ length: count }).map((_, i) => (
        <div className="skeleton-insight" key={i}>
          <SkeletonBar width="30%" height="12px" />
          <SkeletonBar width="90%" height="16px" />
          <SkeletonBar width="100%" />
        </div>
      ))}
    </div>
  );
}
