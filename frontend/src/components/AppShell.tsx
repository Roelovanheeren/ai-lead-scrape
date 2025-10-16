import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  LayoutDashboard, 
  Briefcase, 
  Users, 
  Megaphone, 
  FileText, 
  Settings, 
  Zap,
  Bell,
  User,
  Moon,
  Sun,
  Menu,
  X,
  Search,
  Target
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface AppShellProps {
  children: React.ReactNode
}

const navigation = [
  { name: 'Research', href: '/', icon: Search },
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Leads', href: '/leads', icon: Users },
  { name: 'Target Audience', href: '/target-audience', icon: Target },
  { name: 'Jobs', href: '/jobs', icon: Briefcase },
  { name: 'Campaigns', href: '/campaigns', icon: Megaphone },
  { name: 'Templates', href: '/templates', icon: FileText },
  { name: 'Integrations', href: '/integrations', icon: Zap },
  { name: 'Settings', href: '/settings', icon: Settings },
]

export default function AppShell({ children }: AppShellProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [theme, setTheme] = useState<'light' | 'dark'>('dark')
  const [notifications] = useState(3) // Mock notification count

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light')
    document.documentElement.setAttribute('data-theme', theme === 'light' ? 'dark' : 'light')
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <motion.aside
        initial={false}
        animate={{ x: sidebarOpen ? 0 : '-100%' }}
        className={cn(
          "fixed inset-y-0 left-0 z-50 w-64 bg-card/90 backdrop-blur border-r border-white/10 lg:translate-x-0",
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex h-full flex-col">
          {/* Logo */}
          <div className="flex h-16 items-center justify-between px-4">
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-lg bg-brand flex items-center justify-center">
                <Zap className="h-5 w-5 text-white" />
              </div>
              <span className="font-heading font-semibold text-lg text-brand">
                Elvision Foundations
              </span>
            </div>
            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden"
              onClick={() => setSidebarOpen(false)}
            >
              <X className="h-5 w-5" />
            </Button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-1 px-2 pb-4">
            {navigation.map((item) => {
              const Icon = item.icon
              return (
                <a
                  key={item.name}
                  href={item.href}
                  className="group flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-muted hover:bg-white/5 hover:text-foreground transition-colors"
                >
                  <Icon className="h-5 w-5" />
                  {item.name}
                </a>
              )
            })}
          </nav>

          {/* User section */}
          <div className="border-t border-white/10 p-4">
            <div className="flex items-center gap-3">
              <div className="h-8 w-8 rounded-full bg-brand/20 flex items-center justify-center">
                <User className="h-4 w-4 text-brand" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">John Doe</p>
                <p className="text-xs text-muted truncate">john@elvision.com</p>
              </div>
            </div>
          </div>
        </div>
      </motion.aside>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Header */}
        <header className="sticky top-0 z-30 h-16 flex items-center justify-between px-6 border-b border-white/10 bg-card/60 backdrop-blur">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu className="h-5 w-5" />
            </Button>
            <h1 className="text-xl font-semibold">Research</h1>
          </div>

          <div className="flex items-center gap-3">
            {/* Theme toggle */}
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleTheme}
              className="relative"
            >
              {theme === 'light' ? (
                <Moon className="h-5 w-5" />
              ) : (
                <Sun className="h-5 w-5" />
              )}
            </Button>

            {/* Notifications */}
            <Button
              variant="ghost"
              size="icon"
              className="relative"
            >
              <Bell className="h-5 w-5" />
              {notifications > 0 && (
                <span className="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-red-500 text-xs text-white flex items-center justify-center">
                  {notifications}
                </span>
              )}
            </Button>

            {/* New Job Button */}
            <Button className="shadow-glow">
              <Briefcase className="h-4 w-4 mr-2" />
              New Job
            </Button>
          </div>
        </header>

        {/* Page content */}
        <main className="p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
