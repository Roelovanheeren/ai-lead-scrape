import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import AppShell from './components/AppShell'
import Dashboard from './components/Dashboard'
import ResearchDashboard from './components/ResearchDashboard'
import LeadsTable from './components/LeadsTable'
import JobWizard from './components/JobWizard'
import JobStatus from './components/JobStatus'
import TargetAudienceIntelligence from './components/TargetAudienceIntelligence'
import TestAppShell from './components/TestAppShell'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-background text-foreground">
        <AppShell>
          <Routes>
            <Route path="/" element={<ResearchDashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/research" element={<ResearchDashboard />} />
            <Route path="/leads" element={<LeadsTable />} />
            <Route path="/target-audience" element={<TargetAudienceIntelligence />} />
            <Route path="/jobs" element={<div className="p-6"><h1 className="text-2xl font-bold">Jobs</h1><p className="text-muted">Job management coming soon...</p></div>} />
            <Route path="/jobs/:jobId" element={<JobStatus />} />
            <Route path="/new-job" element={<JobWizard />} />
            <Route path="/campaigns" element={<div className="p-6"><h1 className="text-2xl font-bold">Campaigns</h1><p className="text-muted">Campaign management coming soon...</p></div>} />
            <Route path="/templates" element={<div className="p-6"><h1 className="text-2xl font-bold">Templates</h1><p className="text-muted">Template management coming soon...</p></div>} />
            <Route path="/integrations" element={<div className="p-6"><h1 className="text-2xl font-bold">Integrations</h1><p className="text-muted">Integration management coming soon...</p></div>} />
            <Route path="/settings" element={<div className="p-6"><h1 className="text-2xl font-bold">Settings</h1><p className="text-muted">Settings coming soon...</p></div>} />
          </Routes>
        </AppShell>
      </div>
    </Router>
  )
}

export default App