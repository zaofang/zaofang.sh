// Terminals get index.txt at /, over plain http too; browsers on http are sent to https.
const TERMINAL = /^(curl|wget|httpie|xh|fetch)\b/i;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const text = TERMINAL.test(request.headers.get("user-agent") ?? "");
    if (url.protocol === "http:" && !text) {
      url.protocol = "https:";
      return new Response(null, { status: 301, headers: { location: url.href, vary: "user-agent" } });
    }
    if (url.pathname !== "/") return env.ASSETS.fetch(request);
    const res = await env.ASSETS.fetch(text ? new URL("/index.txt", url) : request);
    const out = new Response(res.body, res);
    if (text) out.headers.set("content-type", "text/plain; charset=utf-8");
    out.headers.set("vary", "user-agent");
    return out;
  },
};
