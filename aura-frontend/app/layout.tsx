import type { Metadata } from "next";
import Providers from "./providers";
import "./globals.css";

export const metadata: Metadata = {
  title: "Aura — Permission Firewall for AI Agents",
  description:
    "Zero-trust intermediary control plane that ensures AI agents cannot execute destructive actions without explicit human approval.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen font-sans">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
