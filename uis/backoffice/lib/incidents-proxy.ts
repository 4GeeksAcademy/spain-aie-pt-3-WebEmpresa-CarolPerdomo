const apiUrl = process.env.INCIDENTS_API_URL ?? "http://127.0.0.1:8000";
const maxBytes = 10 * 1024 * 1024;

export async function forwardIncidentsRequest(request: Request, path: string) {
  try {
    let body: ArrayBuffer | undefined;
    if (request.method === "POST") {
      const length = Number(request.headers.get("content-length"));
      if (length > maxBytes) {
        return Response.json({ error: "El fichero supera el límite de 10 MB." }, { status: 413 });
      }
      body = await request.arrayBuffer();
      if (body.byteLength > maxBytes) {
        return Response.json({ error: "El fichero supera el límite de 10 MB." }, { status: 413 });
      }
    }
    const requestHeaders = new Headers();
    const contentType = request.headers.get("content-type");
    const ifMatch = request.headers.get("if-match");
    if (contentType) requestHeaders.set("Content-Type", contentType);
    if (ifMatch) requestHeaders.set("If-Match", ifMatch);
    const response = await fetch(`${apiUrl}${path}`, {
      method: request.method,
      headers: requestHeaders,
      body,
      cache: "no-store",
      signal: AbortSignal.timeout(30000),
    });
    const headers = new Headers({
      "Content-Type": response.headers.get("content-type") ?? "application/json",
      "Cache-Control": "no-store",
    });
    const disposition = response.headers.get("content-disposition");
    if (disposition) headers.set("Content-Disposition", disposition);
    return new Response(response.body, { status: response.status, headers });
  } catch {
    return Response.json({ error: "No se puede conectar con el servicio de incidencias." }, { status: 503 });
  }
}