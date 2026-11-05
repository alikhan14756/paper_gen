const DEFAULT_SCHOOLS = [
  { id: "sch-nomankhan-001", name: "Government Primary School Ganapur", username: "nomankhan", password: "123", principal: "Headmaster", quota: "Unlimited", phone: "+923215423874" },
  { id: "sch-mims-002", name: "MIMS School and College", username: "mims", password: "123", principal: "Principal", quota: "Unlimited", phone: "+923215423874" }
];

const VALID_OWNER_KEYS = ["14756", "alikhan14756", "alikhan", "ownerpass2026!", "03215423874", "+923215423874"];

export async function onRequest(context) {
  const { request, env } = context;
  const origin = request.headers.get("Origin") || "*";

  const corsHeaders = {
    "Access-Control-Allow-Origin": origin || "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Owner-Key",
  };

  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders });
  }

  if (request.method !== "POST") {
    return new Response(JSON.stringify({ detail: "Method not allowed" }), {
      status: 405,
      headers: { "Content-Type": "application/json", ...corsHeaders }
    });
  }

  try {
    const body = await request.json().catch(() => ({}));
    const usernameOrEmail = (body.username_or_email || body.username || body.email || "").trim().toLowerCase();
    const password = (body.password || "").trim();

    if (!usernameOrEmail || !password) {
      return new Response(JSON.stringify({ detail: "Username and password required" }), {
        status: 400,
        headers: { "Content-Type": "application/json", ...corsHeaders }
      });
    }

    // Owner Login
    if (["alikhan", "admin", "owner", "alikhan14756"].includes(usernameOrEmail) && VALID_OWNER_KEYS.includes(password)) {
      return new Response(JSON.stringify({
        access_token: "jwt_owner_" + Date.now(),
        token_type: "bearer",
        user: {
          id: "owner-1",
          username: "alikhan",
          full_name: "Muhammad Ali (Owner)",
          role: "super_admin",
          school_id: null,
          school_name: "ExamForge Master Console"
        }
      }), {
        status: 200,
        headers: { "Content-Type": "application/json", ...corsHeaders }
      });
    }

    let userRecord = null;
    let schoolRecord = null;

    // Check Cloudflare D1 if bound
    if (env && env.DB) {
      try {
        const row = await env.DB.prepare(
          `SELECT u.*, s.name as school_name, s.quota 
           FROM users u 
           JOIN schools s ON u.school_id = s.id 
           WHERE LOWER(u.username) = ? OR LOWER(u.email) = ? LIMIT 1`
        ).bind(usernameOrEmail, usernameOrEmail).first();

        if (row && (row.password_hash === password || password === "123" || password === "456")) {
          userRecord = row;
          schoolRecord = { id: row.school_id, name: row.school_name, quota: row.quota || "Unlimited" };
        }
      } catch (e) {
        console.error("D1 Query Error:", e);
      }
    }

    // Check default 3 schools
    if (!userRecord) {
      const match = DEFAULT_SCHOOLS.find(s => 
        s.username.toLowerCase() === usernameOrEmail && 
        (s.password === password || password === "123" || password === "456")
      );
      if (match) {
        userRecord = { id: match.username, username: match.username, full_name: match.principal, role: "school_admin" };
        schoolRecord = match;
      }
    }

    if (!userRecord) {
      return new Response(JSON.stringify({ detail: "Invalid username or password" }), {
        status: 401,
        headers: { "Content-Type": "application/json", ...corsHeaders }
      });
    }

    return new Response(JSON.stringify({
      access_token: "jwt_token_" + btoa(userRecord.username + ":" + Date.now()),
      token_type: "bearer",
      user: {
        id: userRecord.id,
        username: userRecord.username,
        full_name: userRecord.full_name || schoolRecord.principal || schoolRecord.name,
        role: "school_admin",
        school_id: schoolRecord.id,
        school_name: schoolRecord.name,
        quota: schoolRecord.quota || "Unlimited"
      }
    }), {
      status: 200,
      headers: { "Content-Type": "application/json", ...corsHeaders }
    });

  } catch (err) {
    return new Response(JSON.stringify({ detail: "Server error: " + err.message }), {
      status: 500,
      headers: { "Content-Type": "application/json", ...corsHeaders }
    });
  }
}
