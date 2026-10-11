import { describe, it, expect, vi, beforeEach } from 'vitest'
import { shallowMount, flushPromises } from '@vue/test-utils'
import { createPinia } from 'pinia'

vi.mock('@/utils/apiFetch', () => ({ apiFetch: vi.fn() }))

import { apiFetch } from '@/utils/apiFetch'
import DashMatchHistory from './DashMatchHistory.vue'
import RecentMatchesList from '../RecentMatchesList.vue'
import DashRallyTimeline from './DashRallyTimeline.vue'


function deferred() {
    let resolve
    const promise = new Promise(r => { resolve = r} )
    return { promise, resolve}
}

const json = (data) => ({ ok: true, json: async () => data })


describe('DashMatchHistory', () => {
    let pending

    beforeEach(() => {
        pending = {}
        apiFetch.mockReset()
        apiFetch.mockImplementation((url) => {
            const m = url.match(/matches\/(\d+)\/events/)
            if (m) {
                pending[m[1]] = deferred()
                return pending[m[1]].promise
            }
            return Promise.resolve(json([]))
        })
    })


    function mountHistory() {
        return shallowMount(DashMatchHistory, { global: { plugins: [createPinia()] } })
    }
    const select = (wrapper, match) => 
        wrapper.findComponent(RecentMatchesList).vm.$emit('match-click', match)
    const shownEvents = (wrapper) =>
        wrapper.findComponent(DashRallyTimeline).props('events')

    it('loads events for the selected match', async () => {
        const wrapper = mountHistory()
        await flushPromises()

        select(wrapper, { id: 1 })
        await flushPromises()
        pending[1].resolve(json([{ id: 10, match: 1 }]))
        await flushPromises()

        expect(shownEvents(wrapper)).toEqual([{ id: 10, match: 1}])
    })


    it('ignores a late response for a previosly selected match', async () => {
        const wrapper = mountHistory()
        await flushPromises()

        select(wrapper, { id: 1 })
        await flushPromises()
        select(wrapper, { id: 2 })
        await flushPromises()
        
        pending[2].resolve(json([{ id: 20, match: 2 }]))
        await flushPromises()
        pending[1].resolve(json([{ id: 10, match: 1 }]))
        await flushPromises()

        expect(shownEvents(wrapper)).toEqual([{ id: 20, match: 2 }])
    })

})
