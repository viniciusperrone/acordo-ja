"use client";

import React from "react";

type InputProps = React.InputHTMLAttributes<HTMLInputElement> & {
  label?: string;
  error?: string;
};

export default function Input({ label, error, className = "", ...props }: InputProps) {
  return (
    <div className="form-field">
      {label && <label>{label}</label>}
      <input className={["input", className].filter(Boolean).join(" ")} {...props} />
      {error && (
        <span className="muted" style={{ color: "var(--color-primary)" }}>
          {error}
        </span>
      )}
    </div>
  );
}
