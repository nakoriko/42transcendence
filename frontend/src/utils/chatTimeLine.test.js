import { describe, it, expect } from 'vitest'
import { dayLabel, chatTimeline } from './chatTimeline'

const now = new Date(2026, 9, 27, 15, 0).getTime()          // 27 Oct 2026, 15:00 local time
const at = (day, h, m = 0) => new Date(2026, 9, day, h, m).getTime()
const msg = (self, ts) => ({ self, content: 'x', timeStamp: ts })

describe('dayLabel', () => {
    it('says Today for the same day', () => {
        expect(dayLabel(at(27, 9), now)).toBe('Today')
    })
    it('says Yesterday for the day before', () => {
        expect(dayLabel(at(26, 23, 59), now)).toBe('Yesterday')
    })
    it('shows the date for older days', () => {
        expect(dayLabel(at(20, 12), now)).toBe('20 Oct')
    })
})

describe('chatTimeline', () => {
    it('returns an empty list for no messages', () => {
        expect(chatTimeline([], now)).toEqual([])
    })
    it('puts a day label only on the first message of each day', () => {
        const t = chatTimeline([msg(true, at(26, 10)), msg(false, at(26, 11)), msg(true, at(27, 9))], now)
        expect(t.map(m => m.day)).toEqual(['Yesterday', null, 'Today'])
    })
    it('shows time only on the last message of a run from one sender', () => {
        const t = chatTimeline([
            msg(false, at(27, 9)), msg(false, at(27, 9, 1)),
            msg(true, at(27, 9, 2)), msg(true, at(27, 9, 3)),
        ], now)
        expect(t.map(m => m.showTime)).toEqual([false, true, false, true])
    })
    it('ends a run when the day changes', () => {
        const t = chatTimeline([msg(true, at(26, 23)), msg(true, at(27, 8))], now)
        expect(t.map(m => m.showTime)).toEqual([true, true])
    })
    it('keeps the original message fields', () => {
        const [m] = chatTimeline([msg(true, at(27, 9))], now)
        expect(m).toMatchObject({ self: true, content: 'x', timeStamp: at(27, 9) })
    })
})