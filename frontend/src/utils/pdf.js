export const PDF_MAX_SIDE = 14400
export function fitPdfPage(w, h) {
    const k = Math.min(1, PDF_MAX_SIDE / Math.max(w, h))
    return { width: w * k, height: h * k, orientation: w>= h ? 'landscape' : 'portrait' }
}