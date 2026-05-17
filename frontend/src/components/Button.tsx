"use client";

import React from "react";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "outline" | "ghost";
};

export default function Button({
  variant = "primary",
  className = "",
  children,
  ...props
}: ButtonProps) {
  const variantClass =
    variant === "primary" ? "btn-primary" : variant === "outline" ? "btn-outline" : "btn-ghost";

  return (
    <button className={["btn", variantClass, className].filter(Boolean).join(" ")} {...props}>
      {children}
    </button>
  );
}
