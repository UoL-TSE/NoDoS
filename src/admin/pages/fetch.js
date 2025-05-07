let _token = null;


export function setToken(token) {
    _token = token;
}


export function fetchAPI(method, endpoint, body=null) {
    if (_token === null) {
        throw "No token specified";
    }

    let headers = {};
    if (body !== null) {
        headers = {
            "Content-Type": "application/json"
        }
    }

    return fetch(endpoint, {
        method: method,
        headers: {
            "Authorization": `Bearer ${_token}`,
            ...headers
        },
        body: body
    })
}
