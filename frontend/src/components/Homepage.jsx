import NeonButton from './NeonButton'
import { FaSteam } from 'react-icons/fa'

export default function Homepage() {
  return (
    <div className="min-h-screen bg-black text-white flex flex-col items-center justify-center p-4">
      <header className="text-center mb-12">
        <h1 className="text-6xl font-bold mb-4 animate-pulse">
          <span className="text-blue-500">get</span>{' '}
          <span className="text-pink-500">ur</span>{' '}
          <span className="text-green-500">game<i>!!!</i></span>
        </h1>
        <p className="text-xl text-purple-400">
          discover your next favorite game on Steam.
        </p>
      </header>

      <main className="flex flex-col items-center space-y-6 mb-12">
        <NeonButton color="blue">
          <FaSteam className="w-6 h-6 mr-2" />
          Login with Steam
        </NeonButton>
        <NeonButton color="green">Look Through Your Games</NeonButton>
        <NeonButton color="pink">Get Recommendations</NeonButton>
        <NeonButton color="purple">Logout</NeonButton>
      </main>

      <footer className="text-center text-gray-500">
        <p>© 2025 get ur game!!! All rights reserved.</p>
      </footer>
    </div>
  )
}
