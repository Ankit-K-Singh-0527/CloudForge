function App() {
  return (
    <main className="min-h-screen bg-slate-950 flex items-center justify-center p-6">
      <div className="w-full max-w-md rounded-2xl border border-slate-700 bg-slate-900 p-8 shadow-2xl">
        <div className="mb-5 flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-600 text-xl font-bold text-white">
            C
          </div>

          <div>
            <h1 className="text-xl font-bold text-white">CloudForge</h1>
            <p className="text-sm text-slate-400">Deployment Platform</p>
          </div>
        </div>

        <h2 className="mb-2 text-2xl font-bold text-white">Tailwind CSS is working!</h2>

        <p className="mb-6 text-slate-400">
          Your React application is successfully using Tailwind CSS v4.
        </p>

        <button className="w-full rounded-lg bg-blue-600 px-5 py-3 font-semibold text-white transition hover:bg-blue-500">
          Test Successful
        </button>

        <p className="mt-5 text-center text-xs text-emerald-400">● Frontend styling operational</p>
      </div>
    </main>
  )
}

export default App
