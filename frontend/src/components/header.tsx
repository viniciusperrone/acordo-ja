"use client";

import Image from "next/image";
import Link from "next/link";
import { Menu } from "lucide-react";
import { useState } from "react";

import logo from "../assets/logo.png";

const navigation = [
  { name: "Página Inicial", href: "#home" },
  { name: "Quem Somos", href: "#about" },
  { name: "Serviços", href: "#services" },
  { name: "Central de Ajuda", href: "#help" },
];

export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 w-full border-b border-zinc-200 bg-white/90 backdrop-blur-md px-[15%]">
      <div className="mx-auto flex h-20 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Logo + CTA */}
        <div className="flex items-center gap-4">
          <Link
            href="/"
            aria-label="Ir para página inicial"
            className="flex items-center gap-3"
          >
            <Image
              src={logo}
              alt="Acordo Já logo"
              width={65}
              height={65}
              priority
              className="h-auto w-auto"
            />
          </Link>
        </div>

        {/* Desktop Navigation */}
        <nav
          className="hidden items-center gap-8 text-sm font-medium text-zinc-800 md:flex"
          aria-label="Navegação principal"
        >
          {navigation.map((item) => (
            <Link
              key={item.name}
              href={item.href}
              className="transition-colors hover:text-green-600"
            >
              {item.name}
            </Link>
          ))}
          <Link
            href="/login"
            className="hidden rounded-lg bg-green-600 px-4 py-3 text-sm font-semibold text-white transition-colors hover:bg-green-700 md:inline-flex"
          >
            Colaborador
          </Link>
        </nav>

        {/* Mobile Button */}
        <button
          type="button"
          aria-label="Abrir menu"
          onClick={() => setMobileMenuOpen((prev) => !prev)}
          className="inline-flex items-center justify-center rounded-md p-2 text-zinc-700 transition hover:bg-zinc-100 md:hidden"
        >
          <Menu size={24} />
        </button>
      </div>

      {/* Mobile Navigation */}
      {mobileMenuOpen && (
        <div className="border-t border-zinc-200 bg-white md:hidden">
          <nav className="flex flex-col px-4 py-4">
            {navigation.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                onClick={() => setMobileMenuOpen(false)}
                className="rounded-md px-3 py-3 text-sm font-medium text-zinc-800 transition hover:bg-zinc-100 hover:text-green-600"
              >
                {item.name}
              </Link>
            ))}

            <Link
              href="/login"
              className="mt-4 inline-flex items-center justify-center rounded-lg bg-green-600 px-4 py-3 text-sm font-semibold text-white transition-colors hover:bg-green-700"
            >
              Colaborador
            </Link>
          </nav>
        </div>
      )}
    </header>
  );
}