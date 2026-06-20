    import router from "@/router"
    
    export async function apiFetch(url, options = {}) {
        const token = localStorage.getItem('access')

        if(!token) {
            router.push('/login')
            return null
        }
        const response = await fetch(url, {
            ...options,
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
                ...options.headers //...options - spred operator, that recognise what was passed as method, body etc
            }
        })
        if(response.status === 401) {
            const refreshed = await tryRefresh()
            if(!refreshed) {
                router.push('/login')
                return null
            }
            const newToken = localStorage.getItem('access')
            return fetch(url, {
                ...options,
                headers: {
                    'Authorization': `Bearer ${newToken}`,
                    'Content-Type': 'application/json',
                    ...options.headers //...options - spred operator, that recognise what was passed as method, body etc
                }
            })
        }
        return response
    }



    async function tryRefresh() {
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
    }