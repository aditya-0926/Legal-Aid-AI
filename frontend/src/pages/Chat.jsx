import { ChatWindow } from '../components/chat/ChatWindow'
import { Footer } from '../components/shared/Footer'

export default function Chat() {
  return (
    <div className="flex flex-col h-[calc(100vh-3.5rem)]">
      <div className="flex-1 overflow-hidden">
        <ChatWindow />
      </div>
      <Footer />
    </div>
  )
}
