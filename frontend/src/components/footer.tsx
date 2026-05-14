"use client";

import Image from "next/image";
import Link from "next/link";

import logo from "../assets/logo.png";

export default function Footer() {
  return (
    <footer className="w-full border-t border-zinc-200 bg-white">
      <div className="mx-auto flex max-w-7xl items-center justify-center gap-4 px-4 py-6">
        {/* Logo */}
        <Link
          href="/"
          aria-label="Ir para página inicial"
          className="flex items-center"
        >
          <Image
            src={logo}
            alt="Acordo Já logo"
            width={55}
            height={55}
            className="h-auto w-auto"
          />
        </Link>

        {/* Copyright */}
        <p className="text-sm text-[#6D6F74] font-medium">
          © 2026 Acordo Já Ltda. - Todos os direitos reservados
        </p>
      </div>
    </footer>
  );
}