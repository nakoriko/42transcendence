export function formatTime(ts) {
    return new Date(ts).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })
}

export function formatShortDate(isoString) {
    if(!isoString) return '-'
    return new Date(isoString).toLocaleDateString('en-US', { day: 'numeric', month: 'short' })
}