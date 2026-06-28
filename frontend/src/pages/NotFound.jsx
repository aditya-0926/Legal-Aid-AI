import { useNavigate } from 'react-router-dom'
import { Button } from '../components/ui/Button'

export default function NotFound() {
  const navigate = useNavigate()
  return (
    <div className="min-h-screen flex flex-col items-center justify-center text-center gap-4">
      <p className="text-6xl">⚖️</p>
      <h1 className="font-display font-bold text-2xl text-gray-800">Page Not Found</h1>
      <Button onClick={() => navigate('/')}>Go Home</Button>
    </div>
  )
}
