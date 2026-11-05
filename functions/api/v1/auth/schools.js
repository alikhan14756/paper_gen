const DEFAULT_SCHOOLS = [
  { id: "sch-nomankhan-001", name: "Government Primary School Ganapur", username: "nomankhan", principal: "Headmaster", quota: "Unlimited", phone: "+923215423874" },
  { id: "sch-mims-002", name: "MIMS School and College", username: "mims", principal: "Principal", quota: "Unlimited", phone: "+923215423874" }
];

export async function onRequest(context) {
  const { request, env } = context;
  const origin = request.headers.get("Origin") || "*";

  const corsHeaders = {
    "Access-Control-Allow-Origin": origin || "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
  };

  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders });
  }

  let list = [];
  if (env && env.DB) {
    try {
      const rows = await env.DB.prepare(
        `SELECT s.id, s.name, s.principal_name, s.phone_number, s.quota, u.username
         FROM schools s
         LEFT JOIN users u ON s.id = u.school_id`
      ).all();
      list = rows.results || [];
    } catch (e) {
      console.error("D1 Error:", e);
    }
  }

  if (list.length === 0) {
    list = DEFAULT_SCHOOLS;
  }

  return new Response(JSON.stringify(list), {
    status: 200,
    headers: { "Content-Type": "application/json", ...corsHeaders }
  });
}
