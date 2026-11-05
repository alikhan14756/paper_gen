export async function onRequest(context) {
  return new Response(JSON.stringify({
    status: "healthy",
    platform: "Cloudflare Pages Native Functions",
    service: "ExamForge AI",
    version: "2.0.0",
    schools_count: 3
  }), {
    status: 200,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
    }
  });
}
