import { useEffect, useState, useCallback } from "react";

/**
 * Deterministic UX contract:
 *   status is always exactly one of "loading" | "success" | "error".
 *   There is no "flash of nothing" and no indeterminate spinner-forever
 *   state — every render maps to one of three known states, and callers
 *   render a fixed-size skeleton for "loading" so there is zero layout
 *   shift between states.
 */
export function useFetchState(fetchFn, deps = []) {
  const [status, setStatus] = useState("loading");
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const load = useCallback(() => {
    let cancelled = false;
    setStatus("loading");
    setError(null);
    fetchFn()
      .then((result) => {
        if (cancelled) return;
        setData(result);
        setStatus("success");
      })
      .catch((err) => {
        if (cancelled) return;
        setError(err.message || "Unknown error");
        setStatus("error");
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => load(), [load]);

  return { status, data, error, retry: load };
}
