function startOfDay(ts) {
    const d = new Date(ts)
    d.setHours(0, 0, 0, 0)
    return d.getTime()
}

export function dayLabel(ts, now = Date.now()) {
    const day = startOfDay(ts)
    const today = startOfDay(now)
    const yesterday = new Date (today)
    yesterday.setDate(yesterday.getDate() - 1)

    if(day === today) return 'Today'
    if(day === yesterday.getTime()) return 'Yesterday'
    return new Date(ts).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })
}

// adds to every message what the chat window needs to draw it:
// - day- day divider label before the message (first message of a day), otherwise null
// - showTime - time under the message (last message of a run from the same sender)
export function chatTimeline(messages, now = Date.now()) {
    return messages.map((msg, i) => {
        const prev = messages[i - 1]
        const next = messages[i + 1]
        const day = startOfDay(msg.timeStamp)
        const newDay = !prev || startOfDay(prev.timeStamp) !== day
        const lastInRun = !next || next.self !== msg.self || startOfDay(next.timeStamp) !== day
        return { ...msg, day: newDay ? dayLabel(msg.timeStamp, now) : null, showTime: lastInRun }
    })
}