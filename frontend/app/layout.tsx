import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RAGDesk | Support Agent with Grounded Citations",
  description:
    "AI Help Desk powered by Retrieval-Augmented Generation (RAG), mandatory document citations, and automatic support ticketing.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR">
      <body className="min-h-screen bg-slate-950 text-slate-100">
        {children}
      </body>
    </html>
  );
}
