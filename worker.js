// Terminals get index.txt at / (over http too); browsers get HTML over https.
const TERMINAL = /^(curl|wget|httpie|xh|fetch)\b/i;

// q-value the Accept header gives `type`, from its most specific matching range.
function q(accept, type) {
  let spec = -1, value = 0;
  for (const part of accept.toLowerCase().split(",")) {
    const [range, ...params] = part.split(";").map((s) => s.trim());
    const s = range === type ? 2 : range === type.split("/")[0] + "/*" ? 1 : range === "*/*" ? 0 : -1;
    if (s > spec) {
      spec = s;
      const p = params.find((x) => x.startsWith("q="));
      value = p ? Number(p.slice(2)) : 1;
    }
  }
  return value;
}

function wantsText(request) {
  const accept = request.headers.get("accept") ?? "";
  const text = q(accept, "text/plain"), html = q(accept, "text/html");
  return text === html ? TERMINAL.test(request.headers.get("user-agent") ?? "") : text > html;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const root = url.pathname === "/";
    const text = root && wantsText(request);
    if (url.protocol === "http:" && !text) {
      url.protocol = "https:";
      return new Response(null, { status: 301, headers: { location: url.href, vary: "accept, user-agent" } });
    }
    if (!root) return env.ASSETS.fetch(request);
    const res = await env.ASSETS.fetch(text ? new Request(new URL("/index.txt", url), request) : request);
    const out = new Response(res.body, res);
    out.headers.set("vary", "accept, user-agent");
    if (text) out.headers.set("content-type", "text/plain; charset=utf-8");
    return out;
  },
};
