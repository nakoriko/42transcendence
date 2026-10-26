export const TOOLTIP_OFFSET = 12

export function placeTooltip(x, y, tip, box, offset = TOOLTIP_OFFSET) {
    let left = x + offset
    let top =  y + offset
    if (left + tip.width > box.width) left = x - offset - tip.width
    if (top + tip.height > box.height) top = y - offset - tip.height
    return { left: Math.max(0, left), top: Math.max(0, top) }
}