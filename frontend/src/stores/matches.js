import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiFetch } from '@/utils/apiFetch'

export const useMatchesStore = defineStore('matches', () => {
    const matches = ref([])
    const loaded = ref(false)
    let inflight = null

    async function load (force = false) {
        if(loaded.value && !force) return matches.value
        if(inflight) return inflight

        //race condition control
        inflight = (async () => {
            try {
                const res = await apiFetch ('/api/game/matches/?limit=200')
                if (res) {
                    matches.value = await res.json()
                    loaded.value = true
                }
                return matches.value
            } finally {
                inflight = null
            }
        }) ()
        return inflight
    }

    function invalidate() {
        loaded.value = false
        matches.value = []
    }
    return { matches, loaded, load, invalidate }
})