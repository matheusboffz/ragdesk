import Link from "next/link";

export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-4xl flex-col items-center justify-center px-6 py-16 text-center">
      <span className="mb-4 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-4 py-1 text-xs font-semibold uppercase tracking-wider text-emerald-400">
        RAG + Help Desk
      </span>
      <h1 className="text-4xl font-bold tracking-tight text-white sm:text-5xl">
        RAGDesk
      </h1>
      <p className="mt-4 max-w-2xl text-base text-slate-400 sm:text-lg">
        Agente de suporte inteligente que responde exclusivamente com base em
        documentos oficiais, cita cada trecho utilizado e abre tickets de
        suporte automaticamente quando não encontra resposta confiável.
      </p>
      <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
        <Link
          href="/chat"
          className="rounded-lg bg-emerald-600 px-6 py-3 text-sm font-semibold text-white transition hover:bg-emerald-500"
        >
          Acessar Chat
        </Link>
        <Link
          href="/login"
          className="rounded-lg border border-slate-700 bg-slate-900 px-6 py-3 text-sm font-semibold text-slate-200 transition hover:border-slate-600 hover:bg-slate-800"
        >
          Entrar / Cadastrar
        </Link>
      </div>
    </main>
  );
}
