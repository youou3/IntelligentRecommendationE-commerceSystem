export async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, options)
  const contentType = response.headers.get('content-type') || ''
  if (!contentType.includes('application/json')) {
    const text = await response.text()
    const message = text.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim()
    throw new Error(message || `Request failed: ${response.status}`)
  }
  const json = await response.json()
  if (!response.ok || json.success === false) {
    throw new Error(json.message || 'Request failed')
  }
  return json.data as T
}

export async function postJson<T>(url: string, payload: Record<string, unknown>): Promise<T> {
  return request<T>(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}
