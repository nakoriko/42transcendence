import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

vi.mock('@/router', () => ({ default: { push:vi.fn() } }))

import router from '@/router'
import { apiFetch } from './apiFetch'

function makeToken(secondsFromNow) {
    const payload = btoa(JSON.stringify({ exp: Math.floor(Date.now() / 1000) + secondsFromNow}))
    return `header.${payload}.signature`
}

function response(status, body ={}) {
    return { ok: status >= 200 && status < 300, status, json: async () => body }
}

describe('apiFetch', () => {
    beforeEach(() => {
        localStorage.clear()
        router.push.mockClear()
    })
    afterEach(() => {
        vi.unstubAllGlobals()
    })


    it('sends request with access token when token is valid', async () => {
        const token = makeToken(3600)
        localStorage.setItem('access', token)
        const fetchMock = vi.fn().mockResolvedValue(response(200))
        vi.stubGlobal('fetch', fetchMock)

        const res = await apiFetch('/api/x/')

        expect(res.status).toBe(200)
        expect(fetchMock).toHaveBeenCalledTimes(1)
        expect(fetchMock.mock.calls[0][1].headers.Authorization).toBe(`Bearer ${token}`)
    })

    it('refreshes expired access token and sends request with the new one', async () => {
        localStorage.setItem('access', makeToken(-60))
        localStorage.setItem('refresh', 'refresh-token')
        const newToken = makeToken(3600)
        const fetchMock = vi.fn()
            .mockResolvedValueOnce(response(200, { access: newToken}))
            .mockResolvedValueOnce(response(200))
        vi.stubGlobal('fetch', fetchMock)

        const res = await apiFetch('/api/x/')
        expect(res.status).toBe(200)
        expect(localStorage.getItem('access')).toBe(newToken)
        expect(fetchMock.mock.calls[1][1].headers.Authorization).toBe(`Bearer ${newToken}`)
    })

    it('clears token when refresh fails for an expired access token', async() => {
        localStorage.setItem('access', makeToken(-60))
        localStorage.setItem('refresh', 'expired-refresh')
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue(response(401)))

        const res = await apiFetch('/api/x/')

        expect(res).toBeNull()
        expect(router.push).toHaveBeenCalledWith('/login')
        expect(localStorage.getItem('access')).toBeNull()
        expect(localStorage.getItem('refresh')).toBeNull()
    })

    it('clears tokens when server returns 401 and refresh fails', async() => {
        localStorage.setItem('access', makeToken(3600))
        localStorage.setItem('refresh', 'revoked-refresh')
        vi.stubGlobal('fetch', vi.fn()
            .mockResolvedValueOnce(response(401))
            .mockResolvedValueOnce(response(401)))

        const res = await apiFetch('/api/x/')
        expect(res).toBeNull()
        expect(localStorage.getItem('access')).toBeNull()
        expect(localStorage.getItem('refresh')).toBeNull()
    })

    it('retries refresh after a network error', async () => {
        localStorage.setItem('access', makeToken(-60))
        localStorage.setItem('refresh', 'refresh-token')
        const newToken = makeToken(3600)
        const fetchMock = vi.fn()
            .mockRejectedValueOnce(new Error('network down'))
            .mockResolvedValueOnce(response(200, { access: newToken }))
            .mockResolvedValueOnce(response(200))
        vi.stubGlobal('fetch', fetchMock)

        await expect(apiFetch('/api/x/')).rejects.toThrow('network down')
        const res = await apiFetch('/api/x/')
        expect(res.status).toBe(200)
    })

    it('does not set JSON content type for FromDataa body', async () => {
        localStorage.setItem('access', makeToken(3600))
        const fetchMock = vi.fn().mockResolvedValue(response(200))
        vi.stubGlobal('fetch', fetchMock)

        await apiFetch('/api/users/avatar/', { method: 'PATCH', body: new FormData () })
        expect(fetchMock.mock.calls[0][1].headers['Content-Type']).toBeUndefined()
    })

})