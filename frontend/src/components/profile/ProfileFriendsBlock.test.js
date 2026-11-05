import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'

const { push } = vi.hoisted(() => ({ push: vi.fn() }))
vi.mock('vue-router', () => ({ useRouter: () => ({ push }) }))
vi.mock('@/utils/apiFetch', () => ({ apiFetch: vi.fn() }))
vi.mock('@/services/wsService.js', () => ({ send: vi.fn() }))

import { apiFetch } from '@/utils/apiFetch'
import { useChatStore } from '@/stores/chat.js'
import ProfileFriendsBlock from './ProfileFriendsBlock.vue'

const player = (id, nickname) => ({ id, nickname, is_online: true, avatar: null, wins: 1, losses: 1 })

const FRIENDS = {
    friends: [{ id: 10, status: 'accepted', friend: player(2, 'friend') }],
    incoming: [{ id: 20, status: 'pending', friend: player(3, 'asking') }],
    outgoing: [{ id: 30, status: 'pending', friend: player(4, 'waiting') }],
}
const USERS = [player(2, 'friend'), player(3, 'asking'), player(4, 'waiting'), player(5, 'zoe'), player(6, 'max')]

const ok = data => ({ ok: true, json: async () => data })

async function mountBlock() {
    const pinia = createPinia()
    setActivePinia(pinia)
    const wrapper = mount(ProfileFriendsBlock, { global: { plugins: [pinia] } })
    await flushPromises()
    return wrapper
}

const button = (wrapper, label) =>
    wrapper.findAll('button').find(b => b.text() === label || b.attributes('aria-label') === label)

const callsTo = (url, method) =>
    apiFetch.mock.calls.filter(([u, options]) => u === url && options?.method === method)

describe('ProfileFriendsBlock', () => {
    let friendsUpdated

    beforeEach(() => {
        push.mockReset()
        apiFetch.mockReset()
        apiFetch.mockImplementation(async (url) => {
            if (url === '/api/users/friends/') return ok(FRIENDS)
            if (url === '/api/users/list/') return ok(USERS)
            return ok({})
        })
        friendsUpdated = vi.fn()
        window.addEventListener('friends-updated', friendsUpdated)
    })
    afterEach(() => window.removeEventListener('friends-updated', friendsUpdated))

    it('accepts an incoming request and tells the rest of the app', async () => {
        const wrapper = await mountBlock()
        await button(wrapper, 'Accept').trigger('click')
        await flushPromises()

        const [[, options]] = callsTo('/api/users/friends/20/', 'PATCH')
        expect(JSON.parse(options.body)).toEqual({ action: 'accept' })
        expect(friendsUpdated).toHaveBeenCalledOnce()
    })

    it('removes a friend only on the second click', async () => {
        const wrapper = await mountBlock()

        await button(wrapper, 'Remove friend').trigger('click')
        expect(callsTo('/api/users/friends/10/', 'DELETE')).toHaveLength(0)

        await button(wrapper, 'Sure?').trigger('click')
        await flushPromises()
        expect(callsTo('/api/users/friends/10/', 'DELETE')).toHaveLength(1)
    })

    it('opens the chat with the chosen friend', async () => {
        const wrapper = await mountBlock()

        await button(wrapper, 'Message').trigger('click')

        expect(useChatStore().activeContactId).toBe(2)
        expect(push).toHaveBeenCalledWith('/chat')
    })

    it('invites a friend to play through the lobby', async () => {
        const wrapper = await mountBlock()
        await button(wrapper, 'Invite to play').trigger('click')
        expect(push).toHaveBeenCalledWith({ path: '/lobby', query: { opponent: 2 } })
    })

    it('filters the friends list by search', async () => {
        const wrapper = await mountBlock()
        expect(wrapper.text()).toContain('friend')

        await wrapper.find('input').setValue('nobody')
        expect(button(wrapper, 'Message')).toBeUndefined()
        expect(wrapper.text()).toContain('No players found')
    })

    it('offers only players without a relation and filters them by search', async () => {
        const wrapper = await mountBlock()
        await button(wrapper, 'Add friend').trigger('click')
        await flushPromises()

        const addList = () => wrapper.findAll('button').filter(b => b.text() === 'Add')
        expect(addList()).toHaveLength(2)
        await wrapper.find('input').setValue('zo')
        expect(addList()).toHaveLength(1)
        expect(wrapper.text()).toContain('zoe')
    })

    it('shows an error when an action fails', async () => {
        const wrapper = await mountBlock()
        apiFetch.mockResolvedValueOnce({ ok: false })

        await button(wrapper, 'Decline').trigger('click')
        await flushPromises()
        expect(wrapper.text()).toContain('Something went wrong')
        expect(friendsUpdated).not.toHaveBeenCalled()
    })
})
