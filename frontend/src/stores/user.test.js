import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

vi.mock('@/utils/apiFetch', () => ({ apiFetch: vi.fn()}))
vi.mock('@/services/wsService.js', () => ({connect: vi.fn(), disconnect: vi.fn(), send: vi.fn() }))

import { apiFetch } from '@/utils/apiFetch'
import { useUserStore } from './user'
import { useMatchesStore } from './matches'
import { useChatStore } from './chat'
import { usePresenceStore } from './presence'

describe('userStore.logout', () => {
    beforeEach(() => {
        setActivePinia(createPinia())
        apiFetch.mockReset()
        apiFetch.mockResolvedValue({ ok: true, json: async () => [{ id: 1, result: 'win'}] })
    })

    it ('clears cached matches so the next user fetches their own', async () => {
        const matches = useMatchesStore()
        await matches.load()

        useUserStore().logout()

        expect(matches.matches).toEqual([])
        expect(matches.loaded).toBe(false)
        await matches.load()
        expect(apiFetch).toHaveBeenCalledTimes(2)
    })

    it('clears chat messages and unread markers', () => {
        const chat = useChatStore()
        chat.receiveMessage({ from_user: { id: 2}, content: 'hi' })

        useUserStore().logout()

        expect(chat.messages).toEqual({})
        expect(chat.hasUnread).toBe(false)
    })

    it('clears presence state', () => {
        const presence = usePresenceStore()
        presence.setCount(5)
        presence.setStatus(2, true)

        useUserStore().logout()

        expect(presence.onlineCount).toBe(0)
        expect(presence.online).toEqual({})
    })
})

describe('userStore.refreshUser', () => {
    const profile = (nickname) => ({ ok: true, json: async() => ({ id: 1, nickname, avatar: null }) })

    beforeEach(() => {
        setActivePinia(createPinia())
        apiFetch.mockReset()
    })

    it('fetchUser does not refetch when user is already loaded', async () => {
        apiFetch.mockResolvedValue(profile('old'))
        const store = useUserStore()

        await store.fetchUser()
        await store.fetchUser()

        expect(apiFetch).toHaveBeenCalledTimes(1)
    })

    it('keeps current user while reloading, then replace it', async () => {
        const store = useUserStore()
        apiFetch.mockResolvedValueOnce(profile('old'))
        await store.fetchUser()

        let resolve 
        apiFetch.mockReturnValueOnce(new Promise( r=> { resolve = r }))
        const pending = store.refreshUser()

        expect(store.currentUser).not.toBeNull()
        expect(store.currentUser.nickname).toBe('old')

        resolve(profile('new'))
        await pending

        expect(store.currentUser.nickname).toBe('new')
        expect(apiFetch).toHaveBeenCalledTimes(2)
    })
})