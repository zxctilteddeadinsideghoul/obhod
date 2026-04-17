import { useEffect, useState } from "react";

export function useAsyncResource(loader, deps) {
  const [state, setState] = useState({
    data: null,
    error: null,
    loading: true,
  });

  useEffect(() => {
    let active = true;

    const run = async () => {
      setState((current) => ({ ...current, loading: true, error: null }));
      try {
        const data = await loader();
        if (active) {
          setState({ data, error: null, loading: false });
        }
      } catch (error) {
        if (active) {
          setState({ data: null, error, loading: false });
        }
      }
    };

    run();

    return () => {
      active = false;
    };
  }, deps);

  return state;
}
