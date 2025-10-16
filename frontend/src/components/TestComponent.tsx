import React from 'react'

export default function TestComponent() {
  return (
    <div className="min-h-screen bg-background text-foreground p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-white mb-4">
          AI Lead Generation Platform
        </h1>
        <p className="text-muted text-lg mb-8">
          Premium dark mode interface is working!
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-card/90 backdrop-blur border border-white/10 rounded-2xl p-6 shadow-glow">
            <h2 className="text-xl font-semibold text-white mb-2">Research</h2>
            <p className="text-muted">Configure and launch AI research jobs</p>
          </div>
          
          <div className="bg-card/90 backdrop-blur border border-white/10 rounded-2xl p-6 shadow-glow">
            <h2 className="text-xl font-semibold text-white mb-2">Results</h2>
            <p className="text-muted">View and analyze research findings</p>
          </div>
          
          <div className="bg-card/90 backdrop-blur border border-white/10 rounded-2xl p-6 shadow-glow">
            <h2 className="text-xl font-semibold text-white mb-2">Analytics</h2>
            <p className="text-muted">Track performance and insights</p>
          </div>
        </div>
        
        <div className="mt-8 text-center">
          <button className="bg-brand hover:bg-brand/90 text-white px-8 py-3 rounded-xl shadow-glow font-medium">
            Get Started
          </button>
        </div>
      </div>
    </div>
  )
}
