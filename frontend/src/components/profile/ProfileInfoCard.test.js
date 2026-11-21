import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'

const { refreshUser } = vi.hoisted(() => ({ refreshUser: vi.fn() }))
vi.mock('@/utils/apiFetch.js', () => ({ apiFetch: vi.fn() }))
vi.mock('@/stores/user.js', () => ({ useUserStore: () => ({ refreshUser }) }))

import { apiFetch } from '@/utils/apiFetch.js'
import ProfileInfoCard from './ProfileInfoCard.vue'

const USER = { nickname: 'peer', email: 'peer@example.com', avatar: null }

async function uploadFile(wrapper) {
    const input = wrapper.find('input[type="file"]')
    Object.defineProperty(input.element, 'files', {
        value: [new File(['x'], 'a.png', { type: 'image/png' })],
        configurable: true,
    })
    await input.trigger('change')
    await flushPromises()
}

describe('ProfileInfoCard avatar upload', () => {
    beforeEach(() => {
        apiFetch.mockReset()
        refreshUser.mockReset()
    })

    it('shows the reason returned by the server', async () => {
        apiFetch.mockResolvedValue({ ok: false, json: async () => ({ avatar: ['Upload a valid image.'] }) })
        const wrapper = mount(ProfileInfoCard, { props: { user: USER } })

        await uploadFile(wrapper)

        expect(wrapper.text()).toContain('Upload a valid image.')
        expect(wrapper.emitted('updated')).toBeUndefined()
    })

    it('shows a general message when the error response is not json', async () => {
        apiFetch.mockResolvedValue({ ok: false, json: async () => { throw new SyntaxError('html') } })
        const wrapper = mount(ProfileInfoCard, { props: { user: USER } })

        await uploadFile(wrapper)

        expect(wrapper.text()).toContain('Failed to upload avatar')
    })

    it('shows a general message when the request fails', async () => {
        apiFetch.mockRejectedValue(new TypeError('network'))
        const wrapper = mount(ProfileInfoCard, { props: { user: USER } })

        await uploadFile(wrapper)

        expect(wrapper.text()).toContain('Failed to upload avatar')
    })

    it('clears the error after a successful upload', async () => {
        apiFetch.mockResolvedValueOnce({ ok: false, json: async () => ({ avatar: ['Upload a valid image.'] }) })
        apiFetch.mockResolvedValueOnce({ ok: true })
        const wrapper = mount(ProfileInfoCard, { props: { user: USER } })

        await uploadFile(wrapper)
        await uploadFile(wrapper)

        expect(wrapper.text()).not.toContain('Upload a valid image.')
        expect(refreshUser).toHaveBeenCalledOnce()
        expect(wrapper.emitted('updated')).toHaveLength(1)
    })
})
