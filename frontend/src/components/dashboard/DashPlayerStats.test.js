import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { shallowMount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('@/utils/apiFetch', () => ({ apiFetch: vi.fn() }))

import { useMatchesStore } from '@/stores/matches.js'
import DashPlayerStats from './DashPlayerStats.vue'

const MATCHES = [1, 2, 3, 4].map(id => ({
    id, result: id % 2 ? 'win' : 'loss', ended_at: `2026-10-0${id}T12:00:00Z`,
}))

class SilentResizeObserver {
    observe() {}
    disconnect() {}
}

function mountStats(width, height) {
    vi.spyOn(Element.prototype, 'getBoundingClientRect').mockReturnValue({ width, height })
    const pinia = createPinia()
    setActivePinia(pinia)
    useMatchesStore().matches = MATCHES
    return shallowMount(DashPlayerStats, { global: { plugins: [pinia] } })
}

describe('DashPlayerStats chart size', () => {
    beforeEach(() => vi.stubGlobal('ResizeObserver', SilentResizeObserver))
    afterEach(() => {
        vi.restoreAllMocks()
        vi.unstubAllGlobals()
    })

    it('does not draw while the container has no size', () => {
        const wrapper = mountStats(0, 0)
        expect(wrapper.element.querySelector('svg')).toBeNull()
    })

    it('draws when the container has a size', () => {
        const wrapper = mountStats(400, 300)
        expect(wrapper.element.querySelector('svg')).not.toBeNull()
    })
})
