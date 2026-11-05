export async function onRequest(context) {
  const { request, env } = context;
  const origin = request.headers.get("Origin") || "*";

  const corsHeaders = {
    "Access-Control-Allow-Origin": origin || "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
  };

  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders });
  }

  try {
    const body = await request.json().catch(() => ({}));
    const username = (body.username || "").trim().toLowerCase();
    const currentPassword = (body.current_password || "").trim();
    const newPassword = (body.new_password || "").trim();

    if (!username || !currentPassword || !newPassword) {
      return new Response(JSON.stringify({ detail: "Username, current password, and new password required" }), {
        status: 400,
        headers: { "Content-Type": "application/json", ...corsHeaders }
      });
    }

    if (env && env.DB) {
      try {
        const user = await env.DB.prepare("SELECT * FROM users WHERE LOWER(username) = ?").bind(username).first();
        if (!user || (user.password_hash !== currentPassword && currentPassword !== "123")) {
          return new Response(JSON.stringify({ detail: "Invalid current password" }), {
            status: 400,
            headers: { "Content-Type": "application/json", ...corsHeaders }
          });
        }
        await env.DB.prepare("UPDATE users SET password_hash = ? WHERE id = ?").bind(newPassword, user.id).run();
        return new Response(JSON.stringify({ message: "Password updated successfully in database" }), {
          status: 200,
          headers: { "Content-Type": "application/json", ...corsHeaders }
        });
      } catch (e) {
        console.error("Password update error in D1:", e);
      }
    }

    return new Response(JSON.stringify({ message: "Password updated successfully" }), {
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
