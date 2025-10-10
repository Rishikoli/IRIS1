import { Suspense } from 'react'
import IRISDashboard from '@/components/IRISDashboard'

export default function IRISPage() {
  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Background Gradient - Light neumorphic theme */}
      <div className="fixed inset-0 bg-gradient-to-br from-slate-50/10 to-gray-50/10" style={{ backgroundColor: '#fcfcfc', zIndex: 0 }}></div>

      {/* Main Content */}
      <div className="relative z-10">
        <Suspense fallback={<div className="flex items-center justify-center min-h-screen">
          <div className="neumorphic-card rounded-3xl p-8 max-w-md mx-auto text-center" style={{ background: '#f0f0f0', boxShadow: '12px 12px 24px #d0d0d0, -12px -12px 24px #ffffff' }}>
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 mx-auto mb-6" style={{ borderColor: '#f2a09e' }}></div>
            <h3 className="text-2xl font-bold mb-4" style={{ color: '#333' }}>Loading IRIS Dashboard...</h3>
            <p className="text-slate-600">Initializing forensic analysis platform</p>
          </div>
        </div>}>
          <IRISDashboard />
        </Suspense>
      </div>
    </div>
  )
}
