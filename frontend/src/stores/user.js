import  { defineStore } from 'pinia'
import  { ref } from 'vue'
import { apiFetch } from '@/utils/apiFetch'

export const useUserStore = defineStore('user', () => {
    const currentUser = ref(null)

    async function fetchUser() {
        if(currentUser.value) return
        const res = await apiFetch('/api/users/profile')
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
    return { currentUser, fetchUser, clear }
})

//const userStore = useUserStore()
//userStore.currentUser.nickname