import { useEffect, useState, useCallback } from "react";

/**
 * Calls `fetcher` immediately, then again every `intervalMs`.
 * Once the backend is live and pushing over WebSocket, this can be swapped
 * for a subscribe/unsubscribe hook instead of polling - components that
 * use useLiveData don't need to change, only this hook's internals.
 */
export function useLiveData(fetcher, intervalMs = null, deps = []) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    try {
      const result = await fetcher();
      setData(result);
      setError(null);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => {
    load();
    if (!intervalMs) return;
    const id = setInterval(load, intervalMs);
    return () => clearInterval(id);
  }, [load, intervalMs]);

  return { data, loading, error, refetch: load };
}
