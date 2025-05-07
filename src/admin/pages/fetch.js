let _token = null;
let redirecting = false;


export function setToken(token) {
    window.sessionStorage.setItem("token", token);
    _token = token;
}


export function fetchAPI(method, endpoint, body=null) {
    if (_token === null) {
        _token = window.sessionStorage.getItem("token");
        
        if (_token === null) {
            if (!redirecting) {
                redirecting = true;
                alert("You are not logged in, please log in and try again.");
                window.location.href = "/pages/login.html";
            }

            throw "No token specified";
        }
    }

    let headers = {};
    if (body !== null) {
        headers = {
            "Content-Type": "application/json"
        }
    }
    
    const promise = fetch(endpoint, {
        method: method,
        headers: {
            "Authorization": `Bearer ${_token}`,
            ...headers
        },
        body: body
    });

    promise.then((r) => {
        if (r.status === 401) {
            if (!redirecting) {
                redirecting = true;
                alert("Your login has expired, please login again.");
                window.location.href = "/pages/login.html";
            }

        }
    });

    return promise;
}
