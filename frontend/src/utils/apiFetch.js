    import router from "@/router"
    
    export async function apiFetch(url, options = {}) {
        const token = localStorage.getItem('access')

        if(!token) {
            router.push('/login')
            return null
        }
        return fetch(url, {
            ...options,
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
                ...options.headers //...options - spred operator, that recognise what was passed as method, body etc
            }
        })
    }