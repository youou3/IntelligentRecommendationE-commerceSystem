export async function request<T>(url: string): Promise<T> {
  const response = await fetch(url)
  const json = await response.json()
  if (!response.ok || json.success === false) {
    throw new Error(json.message || 'Request failed')
  }
  return json.data as T
}
