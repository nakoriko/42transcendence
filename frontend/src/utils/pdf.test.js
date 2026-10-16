import { describe, it, expect } from 'vitest'
import { fitPdfPage, PDF_MAX_SIDE } from './pdf'

describe('fitPdfPage', () => {
    it('keeps small pages as is', () => {
        expect(fitPdfPage(1000, 800)).toEqual({ width: 1000, height: 800, orientation: 'landscape' })
    })
    it('scales tall pages to the PDF limit keeping proportions', () => {
        const { width, height } = fitPdfPage(2000, 30000)
        expect(height).toBe(PDF_MAX_SIDE)
        expect(width).toBeCloseTo(2000 * PDF_MAX_SIDE / 30000)
    })
    it('uses portrait orientation for tall sections', () => {
        expect(fitPdfPage(2000, 30000).orientation).toBe('portrait')
    })
})