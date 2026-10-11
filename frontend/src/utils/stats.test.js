import { describe, it, expect } from 'vitest'
import { calcWinRate, calcTotalMatches } from './stats'

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

