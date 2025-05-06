const TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDY2NTE5MDgsImlhdCI6MTc0NjU2NTUwOCwic3ViIjoiMSJ9.j7SnzjX12a_W76-xCZNjkpVIMDX3jhxBwCTEqb7Mwzw"

export function fetchAPI(method, endpoint, body=null) {
    let headers = {};
    if (body !== null) {
        headers = {
            "Content-Type": "application/json"
        }
    }

    return fetch(endpoint, {
        method: method,
        headers: {
            "Authorization": `Bearer ${TOKEN}`,
            ...headers
        },
        body: body
    })
}
