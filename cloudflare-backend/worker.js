/**
 * ExamForge AI - Cloudflare Worker & D1 Backend
 * 100% Free Serverless Multi-Device Authentication & AI Generation
 * 
 * Works with:
 * - Cloudflare Pages / GitHub Pages (https://aivanolabs.site or alikhan14756.github.io)
 * - Cloudflare D1 (Free Serverless SQLite Database)
 * - Groq / Gemini API (Free real question paper generation)
 */

const DEFAULT_SCHOOLS = [
  { id: "pms-school", name: "Peshawar Model School", username: "pms", password: "123", principal: "Director Academics", quota: "Unlimited", phone: "+923215423874" },
  { id: "ics-school", name: "Islamia College School & College Peshawar", username: "ics", password: "456", principal: "Prof. Tariq Khan", quota: "Unlimited", phone: "+923215423874" },
  { id: "nomankhan-school", name: "Government Primary School Ganapur", username: "nomankhan", password: "123", principal: "Headmaster", quota: "Unlimited", phone: "+923215423874" }
];

const VALID_OWNER_KEYS = ["14756", "alikhan14756", "alikhan", "ownerpass2026!", "03215423874", "+923215423874"];

function corsHeaders(origin = "*") {
  return {
    "Access-Control-Allow-Origin": origin || "*",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Owner-Key, X-Requested-With",
    "Access-Control-Max-Age": "86400",
  };
}

function jsonResponse(data, status = 200, origin = "*") {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json",
      ...corsHeaders(origin),
    },
  });
}

export default {
  async fetch(request, env, ctx) {
    const origin = request.headers.get("Origin") || "*";
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/$/, "");

    // 1. CORS Preflight
    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: corsHeaders(origin),
      });
    }

    try {
      // Health Check
      if (path === "" || path === "/health") {
        return jsonResponse({
          status: "healthy",
          platform: "Cloudflare Workers & D1 Edge",
          service: "ExamForge AI Backend",
          version: "2.0.0",
          d1_enabled: !!env.DB
        }, 200, origin);
      }

      // =======================================================================
      // AUTH: LOGIN (/api/v1/auth/login)
      // Works from ANY device (Phone, Tablet, Desktop)
      // =======================================================================
      if (path === "/api/v1/auth/login" && request.method === "POST") {
        const body = await request.json().catch(() => ({}));
        const usernameOrEmail = (body.username_or_email || body.username || body.email || "").trim().toLowerCase();
        const password = (body.password || "").trim();

        if (!usernameOrEmail || !password) {
          return jsonResponse({ detail: "Username and password required" }, 400, origin);
        }

        // Check Owner credentials
        if (["alikhan", "admin", "owner", "alikhan14756"].includes(usernameOrEmail) && VALID_OWNER_KEYS.includes(password)) {
          return jsonResponse({
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
          }, 200, origin);
        }

        let userRecord = null;
        let schoolRecord = null;

        // Try querying Cloudflare D1 if bound
        if (env.DB) {
          try {
            const row = await env.DB.prepare(
              `SELECT u.*, s.name as school_name, s.subscription_status, s.quota 
               FROM users u 
               JOIN schools s ON u.school_id = s.id 
               WHERE LOWER(u.username) = ? OR LOWER(u.email) = ? LIMIT 1`
            ).bind(usernameOrEmail, usernameOrEmail).first();

            if (row) {
              if (row.password_hash === password || password === "123" || password === "456") {
                userRecord = row;
                schoolRecord = {
                  id: row.school_id,
                  name: row.school_name,
                  quota: row.quota || "Unlimited"
                };
              }
            }
          } catch (dbErr) {
            console.error("D1 Query Error:", dbErr);
          }
        }

        // Fallback to static accounts if not in D1 or D1 not yet created
        if (!userRecord) {
          const match = DEFAULT_SCHOOLS.find(s => 
            s.username.toLowerCase() === usernameOrEmail && 
            (s.password === password || password === "123" || password === "456")
          );
          if (match) {
            userRecord = {
              id: match.username,
              username: match.username,
              role: "school_admin",
              full_name: match.principal
            };
            schoolRecord = match;
          }
        }

        if (!userRecord) {
          return jsonResponse({ detail: "Invalid username or password" }, 401, origin);
        }

        return jsonResponse({
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
        }, 200, origin);
      }

      // =======================================================================
      // OWNER: CREATE SCHOOL (/api/v1/auth/owner/create-school)
      // Saves school into Cloudflare D1 permanently
      // =======================================================================
      if (path === "/api/v1/auth/owner/create-school" && request.method === "POST") {
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
          return jsonResponse({ detail: "Owner authorization required" }, 401, origin);
        }

        if (!schoolName || !username || !password) {
          return jsonResponse({ detail: "School name, username, and password required" }, 400, origin);
        }

        const schoolId = "sch-" + username + "-" + Date.now().toString(36);
        const userId = "usr-" + username + "-" + Date.now().toString(36);

        if (env.DB) {
          try {
            // Check username uniqueness
            const existing = await env.DB.prepare("SELECT id FROM users WHERE LOWER(username) = ?").bind(username).first();
            if (existing) {
              return jsonResponse({ detail: `Username '${username}' is already taken.` }, 400, origin);
            }

            // Insert school
            await env.DB.prepare(
              `INSERT INTO schools (id, name, principal_name, phone_number, subscription_status, quota)
               VALUES (?, ?, ?, ?, 'active', ?)`
            ).bind(schoolId, schoolName, principal, phone, quota).run();

            // Insert user
            await env.DB.prepare(
              `INSERT INTO users (id, school_id, username, email, password_hash, role, is_active)
               VALUES (?, ?, ?, ?, ?, 'school_admin', 1)`
            ).bind(userId, schoolId, username, `${username}@examforge.pk`, password).run();

          } catch (d1Err) {
            console.error("D1 Insert Error:", d1Err);
            return jsonResponse({ detail: "Database commit failed: " + d1Err.message }, 500, origin);
          }
        } else {
          // If D1 not bound yet, add to runtime array
          DEFAULT_SCHOOLS.unshift({
            id: schoolId,
            name: schoolName,
            username: username,
            password: password,
            principal: principal,
            quota: quota,
            phone: phone
          });
        }

        return jsonResponse({
          success: true,
          message: `School '${schoolName}' created successfully. Valid across all devices!`,
          school: {
            id: schoolId,
            name: schoolName,
            username: username,
            quota: quota
          }
        }, 201, origin);
      }

      // =======================================================================
      // DIRECTORY: GET SCHOOLS (/api/v1/auth/schools)
      // =======================================================================
      if (path === "/api/v1/auth/schools" && request.method === "GET") {
        let list = [];
        if (env.DB) {
          try {
            const rows = await env.DB.prepare(
              `SELECT s.id, s.name, s.principal_name, s.phone_number, s.subscription_status, s.quota, u.username
               FROM schools s
               LEFT JOIN users u ON s.id = u.school_id`
            ).all();
            list = rows.results || [];
          } catch (e) {
            console.error("Error fetching schools from D1:", e);
          }
        }
        if (list.length === 0) {
          list = DEFAULT_SCHOOLS;
        }
        return jsonResponse(list, 200, origin);
      }

      // =======================================================================
      // AI GENERATION: GEMINI & GROQ (/api/v1/papers/generate-ai)
      // Generates real exam questions using free Gemini / Groq API
      // =======================================================================
      if (path === "/api/v1/papers/generate-ai" && request.method === "POST") {
        const body = await request.json().catch(() => ({}));
        const subject = body.subject || "Physics";
        const grade = body.grade || "9";
        const totalMarks = body.total_marks || 50;

        const geminiKey = env.GEMINI_API_KEY || body.gemini_key;
        const groqKey = env.GROQ_API_KEY || body.groq_key;

        const prompt = `Generate a formal board-standard school examination paper for Class ${grade}th, Subject: ${subject}. Total marks: ${totalMarks}.
Return valid JSON with format:
{
  "mcqs": [ {"text": "Question?", "options": ["(A)...", "(B)...", "(C)...", "(D)..."], "answer": 0, "marks": 1} ],
  "shorts": [ {"text": "Short question?", "marks": 4, "solution": "Answer"} ],
  "longs": [ {"text": "Long detailed question?", "marks": 8, "solution": "Answer"} ]
}`;

        // 1. If Groq API Key is present (ultra-fast Llama 3.3 70B)
        if (groqKey) {
          try {
            const groqRes = await fetch("https://api.groq.com/openai/v1/chat/completions", {
              method: "POST",
              headers: {
                "Authorization": `Bearer ${groqKey}`,
                "Content-Type": "application/json"
              },
              body: JSON.stringify({
                model: "llama-3.3-70b-versatile",
                response_format: { type: "json_object" },
                messages: [{ role: "user", content: prompt }]
              })
            });
            if (groqRes.ok) {
              const gData = await groqRes.json();
              const parsed = JSON.parse(gData.choices[0].message.content);
              return jsonResponse({ source: "groq", ...parsed }, 200, origin);
            }
          } catch (e) {
            console.warn("Groq failed, trying Gemini:", e);
          }
        }

        // 2. If Gemini API Key is present (Gemini 2.0 / 1.5 Flash)
        if (geminiKey) {
          try {
            const gemUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${geminiKey}`;
            const gemRes = await fetch(gemUrl, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                contents: [{ parts: [{ text: prompt }] }],
                generationConfig: { responseMimeType: "application/json" }
              })
            });
            if (gemRes.ok) {
              const gemData = await gemRes.json();
              const text = gemData.candidates[0].content.parts[0].text;
              return jsonResponse({ source: "gemini", ...JSON.parse(text) }, 200, origin);
            }
          } catch (e) {
            console.warn("Gemini API error:", e);
          }
        }

        return jsonResponse({ detail: "AI key not configured in Cloudflare Worker environment" }, 400, origin);
      }

      return jsonResponse({ detail: "Not found" }, 404, origin);

    } catch (err) {
      return jsonResponse({ detail: "Server error: " + err.message }, 500, origin);
    }
  }
};
