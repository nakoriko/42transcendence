import  { defineStore } from 'pinia'
import  { ref } from 'vue'
import { apiFetch } from '@/utils/apiFetch'
import  * as wsService from '@/services/wsService.js'
import { useMatchesStore } from './matches'
import { useChatStore } from './chat'
import { usePresenceStore } from './presence'

export const useUserStore = defineStore('user', () => {
    const currentUser = ref(null)

    async function fetchUser(force = false) {
        if(currentUser.value && !force) return
        const res = await apiFetch('/api/users/profile/') 
        if(!res?.ok) return
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
            return {success: false, error: 'Connection eror'}
        }
    }

    // doesn't block logout: if the server is unreachable the user still leaves locally
    function revokeRefreshToken() {
        const refresh = localStorage.getItem('refresh')
        if(!refresh) return
        fetch('/api/users/logout/', {
            method: 'POST',
            headers: {'Content-type': 'application/json'},
            body: JSON.stringify({ refresh }),
            keepalive: true // survives closing the tab right after logout
        }).catch(() => {})
    }

    function logout() {
        revokeRefreshToken()
        localStorage.removeItem('access')
        localStorage.removeItem('refresh')
        wsService.disconnect()
        clear()
        useMatchesStore().invalidate()
        useChatStore().$reset()
        usePresenceStore().$reset()
    }

    async function refreshUser() {
        // currentUser.value = null
        await fetchUser(true)
    }

    return { currentUser, fetchUser, clear, login, logout, refreshUser }
})




//const userStore = useUserStore()
//userStore.currentUser.nickname