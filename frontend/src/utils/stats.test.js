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
})

describe('calcTotalMathces', () => {
    it('treats missin values as 0', () => {
        expect(calcTotalMatches(undefined, 3)).toBe(3)
        expect(calcTotalMatches(null, null)).toBe(0)
    })
})

