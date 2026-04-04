/**
 * Export utilities for CSV and XML generation from data arrays.
 * Uses semicolon (;) as CSV delimiter for Excel compatibility in Spanish locales.
 */

type DataRow = Record<string, any>

function triggerDownload(content: string, filename: string, mimeType: string) {
    // BOM for UTF-8 encoding so Excel handles accents correctly
    const BOM = '\uFEFF'
    const blob = new Blob([BOM + content], { type: `${mimeType};charset=utf-8` })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
}

/**
 * Export an array of objects to CSV with semicolon delimiter.
 * @param data - Array of objects to export
 * @param filename - Name of the downloaded file (without extension)
 * @param columnMap - Optional map of { key: "Header Label" } to control columns and order
 */
export function exportToCSV(data: DataRow[], filename: string, columnMap?: Record<string, string>) {
    if (!data || data.length === 0) return

    const keys = columnMap ? Object.keys(columnMap) : Object.keys(data[0])
    const headers = columnMap ? Object.values(columnMap) : keys

    const escapeCSV = (val: any): string => {
        if (val === null || val === undefined) return ''
        const str = String(val)
        if (str.includes(';') || str.includes('"') || str.includes('\n')) {
            return `"${str.replace(/"/g, '""')}"`
        }
        return str
    }

    const lines = [
        headers.join(';'),
        ...data.map(row => keys.map(k => escapeCSV(row[k])).join(';'))
    ]

    triggerDownload(lines.join('\n'), `${filename}.csv`, 'text/csv')
}

/**
 * Export an array of objects to XML.
 * @param data - Array of objects to export
 * @param filename - Name of the downloaded file (without extension)
 * @param rootTag - Root element name (default: "Registros")
 * @param rowTag - Each row element name (default: "Registro")
 * @param columnMap - Optional map of { key: "XMLTag" } to control tag names
 */
export function exportToXML(data: DataRow[], filename: string, rootTag = 'Registros', rowTag = 'Registro', columnMap?: Record<string, string>) {
    if (!data || data.length === 0) return

    const keys = columnMap ? Object.keys(columnMap) : Object.keys(data[0])
    const tagNames = columnMap || Object.fromEntries(keys.map(k => [k, k]))

    const escapeXML = (val: any): string => {
        if (val === null || val === undefined) return ''
        return String(val)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
    }

    const rows = data.map(row => {
        const fields = keys.map(k => `    <${tagNames[k]}>${escapeXML(row[k])}</${tagNames[k]}>`)
        return `  <${rowTag}>\n${fields.join('\n')}\n  </${rowTag}>`
    })

    const xml = `<?xml version="1.0" encoding="UTF-8"?>\n<${rootTag}>\n${rows.join('\n')}\n</${rootTag}>`
    triggerDownload(xml, `${filename}.xml`, 'application/xml')
}
