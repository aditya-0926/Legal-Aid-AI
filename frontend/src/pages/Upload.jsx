import { useState } from 'react'
import { Upload, CheckCircle, AlertCircle, FileText } from 'lucide-react'
import { uploadLaw } from '../services/api'
import { Button } from '../components/ui/Button'

export default function UploadPage() {
  const [file, setFile] = useState(null)
  const [actName, setActName] = useState('')
  const [domain, setDomain] = useState('')
  const [status, setStatus] = useState(null) // null | 'loading' | 'success' | 'error'
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  const DOMAINS = [
    'constitution', 'criminal_law', 'criminal_procedure', 'evidence',
    'tenant_rights', 'labor_law', 'domestic_violence', 'rti',
    'consumer_rights', 'property_dispute', 'family_law',
    'motor_vehicles', 'it_law', 'environmental', 'general',
  ]

  const handleSubmit = async () => {
    if (!file || !actName.trim()) {
      setError('Please select a PDF and enter an act name.')
      return
    }
    setError('')
    setStatus('loading')
    const fd = new FormData()
    fd.append('file', file)
    fd.append('act_name', actName.trim())
    fd.append('domain', domain)
    try {
      const res = await uploadLaw(fd)
      setResult(res)
      setStatus('success')
    } catch (e) {
      setError(e.message)
      setStatus('error')
    }
  }

  return (
    <div className="max-w-xl mx-auto px-4 py-10 space-y-6">
      <div>
        <h1 className="font-display font-bold text-2xl text-gray-900 dark:text-gray-100">
          Upload Legal PDF
        </h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Add a new Indian bare act to the knowledge base. The PDF will be automatically parsed, chunked, and indexed.
        </p>
      </div>

      <div className="space-y-4 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
        {/* File drop */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
            PDF File *
          </label>
          <label className="flex flex-col items-center justify-center border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-xl p-6 cursor-pointer hover:border-primary transition-colors">
            {file ? (
              <div className="flex items-center gap-2 text-primary">
                <FileText size={20} />
                <span className="text-sm font-medium">{file.name}</span>
              </div>
            ) : (
              <>
                <Upload size={24} className="text-gray-400 mb-2" />
                <span className="text-sm text-gray-500">Click to select PDF (max 50 MB)</span>
              </>
            )}
            <input
              type="file"
              accept=".pdf"
              className="hidden"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
            />
          </label>
        </div>

        {/* Act name */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
            Act Name *
          </label>
          <input
            value={actName}
            onChange={(e) => setActName(e.target.value)}
            placeholder="e.g. Right to Information Act 2005"
            className="w-full px-3 py-2.5 text-sm border border-gray-200 dark:border-gray-600 rounded-lg
                       bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100
                       focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        {/* Domain */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
            Domain (auto-detected if left blank)
          </label>
          <select
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
            className="w-full px-3 py-2.5 text-sm border border-gray-200 dark:border-gray-600 rounded-lg
                       bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100
                       focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="">Auto-detect</option>
            {DOMAINS.map((d) => (
              <option key={d} value={d}>{d.replace(/_/g, ' ')}</option>
            ))}
          </select>
        </div>

        {error && (
          <div className="flex items-start gap-2 text-red-600 dark:text-red-400 text-sm bg-red-50 dark:bg-red-900/20 p-3 rounded-lg">
            <AlertCircle size={16} className="mt-0.5 flex-shrink-0" />
            {error}
          </div>
        )}

        <Button
          onClick={handleSubmit}
          disabled={status === 'loading'}
          size="lg"
          className="w-full"
        >
          {status === 'loading' ? 'Processing PDF...' : 'Upload & Ingest'}
        </Button>
      </div>

      {status === 'success' && result && (
        <div className="flex items-start gap-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700 rounded-xl p-4">
          <CheckCircle size={20} className="text-green-600 flex-shrink-0 mt-0.5" />
          <div className="text-sm">
            <p className="font-semibold text-green-800 dark:text-green-300">{result.message}</p>
            <p className="text-green-700 dark:text-green-400 mt-1">
              {result.sections_extracted} sections extracted · {result.chunks_created} chunks indexed
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
