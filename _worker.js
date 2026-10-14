// Cloudflare Worker 中转脚本
// 作用：在 GitHub Pages 前端和 DeepSeek API 之间做中转，
// 把 API key 存在 Worker 环境变量 DEEPSEEK_API_KEY 里（用 wrangler secret 注入，不进代码库），
// 同时解决浏览器跨域限制。
export default {
  async fetch(request, env) {
    // CORS 预检
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        status: 204,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Headers': 'Content-Type',
          'Access-Control-Allow-Methods': 'POST, OPTIONS',
        },
      });
    }

    const url = new URL(request.url);
    if (request.method !== 'POST' || url.pathname !== '/api/deepseek') {
      return new Response('Not found', { status: 404 });
    }

    const key = (env.DEEPSEEK_API_KEY || '').trim();
    if (!key) {
      return json({ ok: false, error: '未配置 DEEPSEEK_API_KEY，请用 wrangler secret put DEEPSEEK_API_KEY 注入' }, 500);
    }

    try {
      const body = await request.json();
      const payload = {
        model: 'deepseek-chat',
        messages: body.messages,
        temperature: 0.3,
        max_tokens: 8192,
      };
      if (body.json_mode) {
        payload.response_format = { type: 'json_object' };
      }

      const resp = await fetch('https://api.deepseek.com/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + key,
        },
        body: JSON.stringify(payload),
      });
      const data = await resp.json();
      if (!resp.ok) {
        throw new Error((data && data.error && data.error.message) || ('HTTP ' + resp.status));
      }
      const content = data.choices[0].message.content;
      return json({ ok: true, content });
    } catch (e) {
      return json({ ok: false, error: String((e && e.message) || e) }, 500);
    }
  },
};

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Access-Control-Allow-Origin': '*',
    },
  });
}
