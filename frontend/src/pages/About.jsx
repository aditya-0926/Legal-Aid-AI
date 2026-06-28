export default function About() {
  return (
    <div className="max-w-2xl mx-auto px-4 py-10 space-y-4">
      <h1 className="font-display font-bold text-2xl text-gray-900">About Legal Aid AI</h1>
      <p className="text-gray-600 text-sm leading-relaxed">
        Legal Aid AI is an open-source project that uses RAG (Retrieval-Augmented Generation) to help low-income
        Indian citizens understand their legal rights in their own language. It is backed by 200+ Indian bare acts
        and connected to the NALSA legal aid network.
      </p>
      <p className="text-gray-600 text-sm">
        This tool provides <strong>legal information</strong>, not legal advice. Always consult a licensed
        advocate for your specific case.
      </p>
      <p className="text-sm text-gray-500">NALSA Helpline: <a href="tel:18001110031" className="underline text-primary">1800-11-0031</a></p>
    </div>
  )
}
