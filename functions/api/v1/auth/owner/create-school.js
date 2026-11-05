const VALID_OWNER_KEYS = ["14756", "alikhan14756", "alikhan", "ownerpass2026!", "03215423874", "+923215423874"];

export async function onRequest(context) {
  const { request, env } = context;
  const origin = request.headers.get("Origin") || "*";

  const corsHeaders = {
    "Access-Control-Allow-Origin": origin || "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
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
    const schoolName = (body.school_name || "").trim();
    const username = (body.username || "").trim().toLowerCase();
    const password = (body.password || "").trim();
    const principal = (body.principal_name || "Principal").trim();
    const phone = (body.phone_number || "+923215423874").trim();
    const quota = body.quota || "Unlimited";

    const ownerKeyHeader = request.headers.get("X-Owner-Key") || "";
    const ownerKeyBody = body.owner_key || "";
    const authHeader = request.headers.get("Authorization") || "";

    const isOwner = VALID_OWNER_KEYS.includes(ownerKeyHeader) || 
                    VALID_OWNER_KEYS.includes(ownerKeyBody) || 
                    authHeader.includes("jwt_owner");

    if (!isOwner) {
      return new Response(JSON.stringify({ detail: "Owner authorization required" }), {
        status: 401,
        headers: { "Content-Type": "application/json", ...corsHeaders }
      });
    }

    if (!schoolName || !username || !password) {
      return new Response(JSON.stringify({ detail: "School name, username, and password required" }), {
        status: 400,
        headers: { "Content-Type": "application/json", ...corsHeaders }
      });
    }

    const schoolId = "sch-" + username + "-" + Date.now().toString(36);
    const userId = "usr-" + username + "-" + Date.now().toString(36);

    if (env && env.DB) {
      try {
        const existing = await env.DB.prepare("SELECT id FROM users WHERE LOWER(username) = ?").bind(username).first();
        if (existing) {
          return new Response(JSON.stringify({ detail: `Username '${username}' is already taken.` }), {
            status: 400,
            headers: { "Content-Type": "application/json", ...corsHeaders }
          });
        }

        await env.DB.prepare(
          `INSERT INTO schools (id, name, principal_name, phone_number, subscription_status, quota)
           VALUES (?, ?, ?, ?, 'active', ?)`
        ).bind(schoolId, schoolName, principal, phone, quota).run();

        await env.DB.prepare(
          `INSERT INTO users (id, school_id, username, email, password_hash, role, is_active)
           VALUES (?, ?, ?, ?, ?, 'school_admin', 1)`
        ).bind(userId, schoolId, username, `${username}@examforge.pk`, password).run();

      } catch (dbErr) {
        console.error("D1 Insert Error:", dbErr);
        return new Response(JSON.stringify({ detail: "Database insert error: " + dbErr.message }), {
          status: 500,
          headers: { "Content-Type": "application/json", ...corsHeaders }
        });
      }
    }

    return new Response(JSON.stringify({
      success: true,
      message: `School '${schoolName}' created successfully on Cloudflare! Valid across all devices.`,
      school: {
        id: schoolId,
        name: schoolName,
        username: username,
        quota: quota
      }
    }), {
      status: 201,
      headers: { "Content-Type": "application/json", ...corsHeaders }
    });

  } catch (err) {
    return new Response(JSON.stringify({ detail: "Server error: " + err.message }), {
      status: 500,
      headers: { "Content-Type": "application/json", ...corsHeaders }
    });
  }
}
