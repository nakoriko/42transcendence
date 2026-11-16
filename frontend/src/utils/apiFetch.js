    import router from "@/router"

    let refreshPromise = null // one promise for all parallel cals

    function isTokenExpiring(token, bufferSeconds = 10) {
        try {
            const payload = JSON.parse(atob(token.split('.')[1]))
            const expiresAt = payload.exp * 1000 // to ms
            return Date.now() >= expiresAt - bufferSeconds * 1000
        } catch {
            return true //se non siamo riusciti a fare parse, lo consideriamo come exp
        }
    }

    async function tryRefresh() {
        //se refresh gia in corso, aspettiamo prima di lanciare un nuovo
        if(refreshPromise) return refreshPromise

        refreshPromise = (async() => {
            const refresh = localStorage.getItem('refresh')
            if(!refresh) return false
    
            const res = await fetch('/api/users/token/refresh/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh })
            }) 
    
            if(res.ok) {
                const data = await res.json() //waits for getting new access token
                localStorage.setItem('access', data.access)
                return true
            }
            return false
        }) ()

        try {
            return await refreshPromise
        } finally {
            refreshPromise = null // reset for next exp token and new refresh
        }

    }

    //refresh failed: sessien is dead, stops redidrect to /profile
    function clearSessionAndRedirect(){
        localStorage.removeItem('access')
        localStorage.removeItem('refresh')
        router.push('/login')
    }

    function buildHeaders(token, options) {
        const headers = { 'Authorization': `Bearer ${token}` }
        if(!(options.body instanceof FormData)) {
            headers['Content-Type'] = 'application/json'
        }
        return { ...headers, ...options.headers }
    }
    
    export async function apiFetch(url, options = {}) {
        let token = localStorage.getItem('access')

        if(!token) {
            router.push('/login')
            return null
        }
        //proactive refresh prima di response 401
        if(isTokenExpiring(token)) {
            const refreshed = await tryRefresh()
            if(!refreshed) {
                clearSessionAndRedirect()
                return null
            }
            token = localStorage.getItem('access')
        }

        const response = await fetch(url, {
            ...options,
            headers: buildHeaders(token, options)
        })

        if(response.status === 401) {
            const refreshed = await tryRefresh()
            if(!refreshed) {
                clearSessionAndRedirect()
                return null
            }
            const newToken = localStorage.getItem('access')
            return fetch(url, {
                ...options,
                headers: buildHeaders(newToken, options)
            })
        }
        return response
    }



