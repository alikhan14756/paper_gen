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
    const subject = body.subject || "Physics";
    const grade = body.grade || "9";
    const totalMarks = body.total_marks || 50;

    const geminiKey = (env && env.GEMINI_API_KEY) || body.gemini_key;
    const groqKey = (env && env.GROQ_API_KEY) || body.groq_key;

    const prompt = `Generate a formal board-standard school examination paper for Class ${grade}th, Subject: ${subject}. Total marks: ${totalMarks}.
Return valid JSON with format:
{
  "mcqs": [ {"text": "Question?", "options": ["(A)...", "(B)...", "(C)...", "(D)..."], "answer": 0, "marks": 1} ],
  "shorts": [ {"text": "Short question?", "marks": 4, "solution": "Answer"} ],
  "longs": [ {"text": "Long detailed question?", "marks": 8, "solution": "Answer"} ]
}`;

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
          return new Response(JSON.stringify({ source: "groq", ...parsed }), {
            status: 200,
            headers: { "Content-Type": "application/json", ...corsHeaders }
          });
        }
      } catch (e) {}
    }

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
          return new Response(JSON.stringify({ source: "gemini", ...JSON.parse(text) }), {
            status: 200,
            headers: { "Content-Type": "application/json", ...corsHeaders }
          });
        }
      } catch (e) {}
    }

    return new Response(JSON.stringify({ detail: "AI API key required" }), {
      status: 400,
      headers: { "Content-Type": "application/json", ...corsHeaders }
    });

  } catch (err) {
    return new Response(JSON.stringify({ detail: "AI generation error: " + err.message }), {
      status: 500,
      headers: { "Content-Type": "application/json", ...corsHeaders }
    });
  }
}
