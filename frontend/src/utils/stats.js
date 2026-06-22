export function calcWinRate(wins, losses) {
    const total = (wins ?? 0) + (losses ?? 0)
    if(total === 0) return 0
    return Math.round(wins / total * 100)
}

export function calcTotalMatches(wins, losses) {
    return (wins ?? 0) + (losses ?? 0)
}