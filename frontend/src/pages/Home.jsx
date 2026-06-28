import { useNavigate } from 'react-router-dom'
import { Scale, Mic, Globe, MapPin } from 'lucide-react'
import { Button } from '../components/ui/Button'
import { useLanguage } from '../hooks/useLanguage'

const FEATURES = [
  { icon: Scale, title: 'Know Your Rights', desc: 'Get plain-language explanations of Indian law' },
  { icon: Mic,   title: 'Voice Support',    desc: 'Speak in Hindi or Marathi — no typing needed' },
  { icon: Globe, title: 'Multilingual',     desc: 'English, Hindi, and Marathi supported' },
  { icon: MapPin,title: 'Find Legal Help',  desc: 'Locate nearest NALSA legal aid center' },
]

export default function Home() {
  const navigate = useNavigate()
  const { t } = useLanguage()
  return (
    <div className="min-h-screen bg-surface flex flex-col items-center px-4 py-12">
      <div className="max-w-2xl w-full text-center space-y-6">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-primary/10 rounded-2xl">
          <Scale size={32} className="text-primary" />
        </div>
        <h1 className="font-display font-bold text-4xl text-gray-900">{t('freeLegalHelp')}</h1>
        <p className="text-gray-500 text-lg">{t('tagline')}</p>
        <Button size="lg" onClick={() => navigate('/chat')}>Get Free Legal Help →</Button>
        <p className="text-xs text-gray-400">100% free · No registration · Confidential</p>
        <div className="grid grid-cols-2 gap-4 mt-8">
          {FEATURES.map((f) => (
            <div key={f.title} className="bg-white rounded-xl p-4 border border-gray-100 text-left">
              <f.icon size={20} className="text-primary mb-2" />
              <p className="font-semibold text-sm text-gray-800">{f.title}</p>
              <p className="text-xs text-gray-500 mt-0.5">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
