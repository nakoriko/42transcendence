import { describe, it, vi, beforeEach, expect } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { apiFetch } from '@/utils/apiFetch'

vi.mock('@/utils/apiFetch', () => ({ apiFetch: vi.fn()}))

import { useMatchesStore } from './matches'

describe('matchesStore', () => {
    beforeEach(() => {
        setActivePinia(createPinia())
        apiFetch.mockReset()
        apiFetch.mockResolvedValue({ ok: true, json: async () => [{ id: 1, result: 'win'}] })

    })

    it('caches matches between load calls', async () => {
        const store = useMatchesStore()
        await store.load()
        await store.load()
        expect(apiFetch).toHaveBeenCalledTimes(1)
    })

    it('finishMatch sends result and invalidates cached history', async() => {
        const store = useMatchesStore()
        await store.load()

        await store.finishMatch(10, { winner: 1, score_player1: 5, score_player2: 3 })

        const [url, options] = apiFetch.mock.calls[1]
        expect(url).toBe('/api/game/matches/10/finish/')
        expect(options.method).toBe('PATCH')
        expect(JSON.parse(options.body)).toEqual({ winner: 1, score_player1: 5, score_player2: 3 })

        await store.load()
        expect(apiFetch).toHaveBeenCalledTimes(3)

    })
})