import  { defineStore } from 'pinia'
import  { ref } from 'vue'
import { apiFetch } from '@/utils/apiFetch'
import  * as wsService from '@/services/wsService.js'

export const useUserStore = defineStore('user', () => {
    const currentUser = ref(null)

    async function fetchUser() {
        if(currentUser.value) return
        const res = await apiFetch('/api/users/profile/') 
        const data = await res.json()
        currentUser.value = {
            id: data.id,
            nickname: data.nickname ?? data.username,
            avatar: data.avatar ?? null
        }
    }

    function clear() {
        currentUser.value = null
    }

    async function login (email, password) {
        try {
            const res = await fetch('/api/users/login/', {
                method: 'POST',
                headers: {'Content-type': 'application/json'}, 
                body: JSON.stringify({email, password})
            })
            const data = await res.json()
            if (!res.ok) return { success: false, error: data.detail || 'login error'}

            localStorage.setItem('access', data.access)
            localStorage.setItem('refresh', data.refresh)
            await fetchUser()
            wsService.connect(data.access)
            return { success: true}
        } catch(err) {
            return {success: false, error: 'Connecton eror'}
        }
    }

    function logout() {
        localStorage.removeItem('access')
        localStorage.removeItem('refresh')
        wsService.disconnect()
        clear()
    }

    async function refreshUser() {
        currentUser.value = null
        await fetchUser()
    }

    return { currentUser, fetchUser, clear, login, logout, refreshUser }
})




//const userStore = useUserStore()
//userStore.currentUser.nickname