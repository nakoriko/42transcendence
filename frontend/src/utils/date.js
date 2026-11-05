export function formatTime(ts) {
    return new Date(ts).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })
}


export function formatLongDate(isoString) {
    return new Date(isoString).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
}

export function formatShortDate(isoString) {
    if(!isoString) return '-'
    return new Date(isoString).toLocaleDateString('en-US', { day: 'numeric', month: 'short' })
}