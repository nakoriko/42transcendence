import { describe, it, expect } from 'vitest'
import { calcWinRate, calcTotalMatches, rollingWinRate } from './stats'

describe('calcWinRate', () => {
    it('returns 0 when there are no matches', () => {
        expect(calcWinRate(0, 0)).toBe(0)
    })
    it('returns rounded percentage', () => {
        expect(calcWinRate(1, 2)).toBe(33)
        expect(calcWinRate(3, 1)).toBe(75)
    })
    it('treats missing wins as 0', () => {
        expect(calcWinRate(undefined, 3)).toBe(0)
        expect(calcWinRate(null, 2)).toBe(0)
    })
})

describe('calcTotalMathces', () => {
    it('treats missing values as 0', () => {
        expect(calcTotalMatches(undefined, 3)).toBe(3)
        expect(calcTotalMatches(null, null)).toBe(0)
    })
})

describe('rollingWinRate', () => {
    // newest first, like matchesStore returns them
    const m = (id, day, result) => ({ id, ended_at: `2026-10-${day}T12:00:00Z`, result })

    it('returns empty array for no matches', () => {
        expect(rollingWinRate([])).toEqual([])
    })
    it('sorts oldest first and slides the window', () => {
        const res = rollingWinRate([m(3, 12, 'loss'), m(2, 11, 'loss'), m(1, 10, 'win')], 2)
        expect(res.map(p => p.id)).toEqual([1, 2, 3])
        expect(res.map(p => p.rate)).toEqual([100, 50, 0])
    })
    it('marks points where the window is not full yet', () => {
        const res = rollingWinRate([m(2, 11, 'win'), m(1, 10, 'win')], 2)
        expect(res.map(p => p.full)).toEqual([false, true])
    })
    it('ignores draws in the rate', () => {
        const res = rollingWinRate([m(2, 11, 'draw'), m(1, 10, 'win')], 2)
        expect(res[1].rate).toBe(100)
    })
})

