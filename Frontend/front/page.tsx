import LoginForm from "@/components/auth/login-form"

export default function Page() {
  return (
    <main className="theme-login relative min-h-dvh overflow-hidden">
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 -z-10 bg-[url('/images/login-bg-analytics.png')] bg-cover bg-center"
      />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 -z-10 bg-gradient-to-tr from-[#0b0721]/70 via-[#120a3a]/40 to-transparent"
      />

      <section className="mx-auto flex max-w-6xl flex-col items-start justify-center gap-8 px-4 py-24 text-left">
        <div className="text-left -ml-3 sm:-ml-2 md:-ml-4 lg:-ml-6">
          <h1 className="text-balance text-3xl font-semibold tracking-tight text-white md:text-4xl">ResearchGuard</h1>
          <p className="mt-2 max-w-xl text-pretty text-white/90">
            Liquid-glass login experience with modern, accessible design.
          </p>
        </div>

        <LoginForm />
      </section>
    </main>
  )
}
