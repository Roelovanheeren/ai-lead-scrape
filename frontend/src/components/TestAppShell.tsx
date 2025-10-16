import React from 'react'

export default function TestAppShell() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">AppShell Test</h1>
      <p className="text-muted-foreground">
        If you can see this, the AppShell is working correctly.
      </p>
      <div className="mt-4">
        <a href="/target-audience" className="text-brand hover:underline">
          Go to Target Audience Intelligence →
        </a>
      </div>
    </div>
  )
}
