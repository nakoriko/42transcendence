import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { shallowMount, flushPromises } from '@vue/test-utils'
import { createPinia } from 'pinia'

const { simulations } = vi.hoisted(() => ({ simulations: [] }))
vi.mock('d3', async (importOriginal) => {
    const real = await importOriginal()
    return {
        ...real,
        forceSimulation: (...args) => {
            const sim = real.forceSimulation(...args)
            simulations.push(sim)
            return sim
        },
    }
})
vi.mock('@/utils/apiFetch', () => ({ apiFetch: vi.fn() }))

import { apiFetch } from '@/utils/apiFetch'
import DashPlayerGraph from './DashPlayerGraph.vue'

const GRAPH = {
    nodes: [
        { id: 1, nickname: 'me', avatar: null, wins: 1, losses: 0, draws: 0, degree: 1, is_current: true },
        { id: 2, nickname: 'rival', avatar: null, wins: 0, losses: 1, draws: 0, degree: 1, is_current: false },
    ],
    edges: [
        { source: 1, target: 2, matches: 1, wins_source: 1, wins_target: 0, draws: 0,
          last_played_at: '2026-10-01T00:00:00Z' },
    ],
    meta: {},
}

// jsdom has neither of them: the graph renders once it becomes visible
class VisibleObserver {
    constructor(callback) { this.callback = callback }
    observe() { this.callback([{ isIntersecting: true }]) }
    disconnect() {}
}

let triggerResize = () => {}
class SilentResizeObserver {
    constructor(callback) { triggerResize = callback }
    observe() {}
    disconnect() {}
}

function setContainerWidth(width) {
    Object.defineProperty(HTMLElement.prototype, 'clientWidth', { configurable: true, get: () => width })
}

beforeEach(() => setContainerWidth(500))
afterEach(() => { delete HTMLElement.prototype.clientWidth })

function setHoverSupport(hasHover) {
    vi.stubGlobal('matchMedia', query => ({ matches: query === '(hover: none)' && !hasHover }))
}

async function mountGraph() {
    const wrapper = shallowMount(DashPlayerGraph, { global: { plugins: [createPinia()] } })
    await flushPromises()
    return wrapper
}

function fireOnNode(wrapper, nickname, type) {
    const circle = [...wrapper.element.querySelectorAll('circle')]
        .find(c => c.__data__.nickname === nickname)
    circle.dispatchEvent(new MouseEvent(type, { bubbles: true }))
}

const lastHovered = wrapper => wrapper.emitted('node-hover').at(-1)[0]?.nickname

describe('DashPlayerGraph simulation', () => {
    beforeEach(() => {
        simulations.length = 0
        vi.stubGlobal('IntersectionObserver', VisibleObserver)
        vi.stubGlobal('ResizeObserver', SilentResizeObserver)
        apiFetch.mockResolvedValue({ ok: true, json: async () => GRAPH })
    })
    afterEach(() => {
        simulations.forEach(s => s.stop())
        vi.unstubAllGlobals()
    })

    it('stops the force simulation when unmounted', async () => {
        const wrapper = await mountGraph()
        expect(simulations).toHaveLength(1)

        const stop = vi.spyOn(simulations[0], 'stop')
        wrapper.unmount()

        expect(stop).toHaveBeenCalled()
    })
})

describe('DashPlayerGraph zero width', () => {
    beforeEach(() => {
        simulations.length = 0
        vi.stubGlobal('IntersectionObserver', VisibleObserver)
        vi.stubGlobal('ResizeObserver', SilentResizeObserver)
        apiFetch.mockResolvedValue({ ok: true, json: async () => GRAPH })
    })
    afterEach(() => {
        simulations.forEach(s => s.stop())
        vi.unstubAllGlobals()
    })

    it('does not draw while the container has no width', async () => {
        setContainerWidth(0)
        const wrapper = await mountGraph()

        expect(wrapper.element.querySelector('svg')).toBeNull()
        expect(simulations).toHaveLength(0)
    })

    it('draws once the container gets its width', async () => {
        setContainerWidth(0)
        const wrapper = await mountGraph()

        setContainerWidth(500)
        triggerResize()
        await new Promise(resolve => setTimeout(resolve, 250))

        expect(wrapper.element.querySelector('svg')).not.toBeNull()
        wrapper.unmount()
    })
})

describe('DashPlayerGraph node selection', () => {
    beforeEach(() => {
        simulations.length = 0
        vi.stubGlobal('IntersectionObserver', VisibleObserver)
        vi.stubGlobal('ResizeObserver', SilentResizeObserver)
        apiFetch.mockResolvedValue({ ok: true, json: async () => GRAPH })
    })
    afterEach(() => {
        simulations.forEach(s => s.stop())
        vi.unstubAllGlobals()
    })

    it('shows the tapped node in the card on touch devices, without leaving the graph', async () => {
        setHoverSupport(false)
        const wrapper = await mountGraph()
        expect(lastHovered(wrapper)).toBe('me')

        fireOnNode(wrapper, 'rival', 'click')

        expect(lastHovered(wrapper)).toBe('rival')
        expect(wrapper.emitted('node-click')).toBeUndefined()
    })

    it('ignores mouse events emulated by a tap, so they do not change the selection', async () => {
        setHoverSupport(false)
        const wrapper = await mountGraph()

        fireOnNode(wrapper, 'rival', 'mouseover')

        expect(lastHovered(wrapper)).toBe('me')
    })

    it('keeps hover and click navigation on desktop', async () => {
        setHoverSupport(true)
        const wrapper = await mountGraph()

        fireOnNode(wrapper, 'rival', 'mouseover')
        expect(lastHovered(wrapper)).toBe('rival')

        fireOnNode(wrapper, 'rival', 'click')
        expect(wrapper.emitted('node-click')[0]).toEqual(['rival'])
    })
})
