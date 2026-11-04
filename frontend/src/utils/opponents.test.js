import { describe,  it, expect } from 'vitest'
import { rankOpponents } from './opponents'

const user = (nickname, is_online = false, is_friend = false) => ({ nickname, is_online, is_friend })
const isOnline = (u) => u.is_online
const names = (list) => list.map(u => u.nickname)

describe('rankOpponents', () => {
    it('puts online friends first, then online players, then offline', () => {
        const users = [user('off'), user('on', true), user('pal', true, true)]
        expect(names(rankOpponents(users, '', isOnline))).toEqual(['pal', 'on', 'off'])
    })
    it('does not lift an offline friend above online players', () => {
        const users = [user('pal', false, true), user('on', true)]
        expect(names(rankOpponents(users, '', isOnline))).toEqual(['on', 'pal'])
    })
    it('sorts by nickname inside a group', () => {
        const users = [user('zed'), user('amy')]
        expect(names(rankOpponents(users, '', isOnline))).toEqual(['amy', 'zed'])
    })
    it('searches by part of the nickname, ignoring case and spaces', () => {
        const users = [user('Sabino'), user('kira')]
        expect(names(rankOpponents(users, '  SAB ', isOnline))).toEqual(['Sabino'])
    })
    it('does not change the original list', () => {
        const users = [user('zed'), user('amy')]
        rankOpponents(users, '', isOnline)
        expect(names(users)).toEqual(['zed', 'amy'])
    })
})