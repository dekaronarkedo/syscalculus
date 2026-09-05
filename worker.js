/**
 * SysCalculus - Cloudflare Edge Static Asset Handler
 * Serves deterministic systems engineering calculators with sub-millisecond edge latency
 */
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    return env.ASSETS.fetch(request);
  }
};
