import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
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

    it('keeps current user while reloading, then replaces it', async () => {
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


describe('userStore.logout and the refresh token', () => {
    beforeEach(() => {
        setActivePinia(createPinia())
        localStorage.clear()
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true }))
    })
    afterEach(() => vi.unstubAllGlobals())

    it('sends the refresh token to the server and clears local tokens', () => {
        localStorage.setItem('access', 'a')
        localStorage.setItem('refresh', 'r')

        useUserStore().logout()

        const [url, options] = fetch.mock.calls[0]
        expect(url).toBe('/api/users/logout/')
        expect(options.method).toBe('POST')
        expect(JSON.parse(options.body)).toEqual({ refresh: 'r' })
        expect(localStorage.getItem('access')).toBeNull()
        expect(localStorage.getItem('refresh')).toBeNull()
    })

    it('does not call the server without a refresh token', () => {
        useUserStore().logout()
        expect(fetch).not.toHaveBeenCalled()
    })

    it('still logs out locally when the request fails', async () => {
        fetch.mockRejectedValue(new TypeError('network'))
        localStorage.setItem('refresh', 'r')

        useUserStore().logout()
        await Promise.resolve()

        expect(localStorage.getItem('refresh')).toBeNull()
    })
})
