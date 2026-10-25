export function calcWinRate(wins, losses) {
    const total = (wins ?? 0) + (losses ?? 0)
    if(total === 0) return 0
    return Math.round((wins ?? 0) / total * 100)
}

export function calcTotalMatches(wins, losses) {
    return (wins ?? 0) + (losses ?? 0)
}


export function summarizeRecord (matches) {
    const rec = { wins: 0, losses: 0, draws: 0, total: matches.length}
    for (const m of matches) {
        if (m.result === 'win') rec.wins++
        else if (m.result === 'loss') rec.losses++
        else rec.draws++
    }
    return rec
}

export function currentStreak(matches) {
    const first = matches[0]?.result
    if( first !== 'win' && first !== 'loss') return { result: null, count: 0}
    let count = 0
    while( count < matches.length && matches[count].result === first) count++
    return { result: first, count}
}

export function calcRank(players, userId) {
    const ranked = players.filter(p => p.total_matches > 0)
    const me = ranked.find( p => p.id === userId)
    if (!me) return { rank: null, of: ranked.length }
    const better = ranked.filter( p => 
        p.wins > me.wins || (p.wins === me.wins && p.win_rate > me.win_rate))
    return { rank: better.length + 1, of: ranked.length }
}

export function rollingWinRate(matches, size = 10) {
    const sorted = [...matches].sort((a, b) => new Date(a.ended_at) - new Date(b.ended_at))
    return sorted.map((m, i) => {
        const last = sorted.slice(Math.max(0, i - size + 1), i + 1)
        const rec = summarizeRecord(last)
        return {
            id: m.id,
            date: new Date(m.ended_at),
            result: m.result,
            rate: calcWinRate(rec.wins, rec.losses),
            full: last.length === size,
        }
    })
}








