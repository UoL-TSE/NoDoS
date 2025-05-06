const TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDY2NTE5MDgsImlhdCI6MTc0NjU2NTUwOCwic3ViIjoiMSJ9.j7SnzjX12a_W76-xCZNjkpVIMDX3jhxBwCTEqb7Mwzw"

export function fetchAPI(method, endpoint, body=null) {
    return fetch(endpoint, {
        method: method,
        headers: {
            "Authorization": `Bearer ${TOKEN}`
        },
        body: body
    })
}
