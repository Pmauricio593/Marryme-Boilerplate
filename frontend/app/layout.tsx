import { Cormorant_Garamond, Plus_Jakarta_Sans } from "next/font/google";
import { Toaster } from "sonner";
import { AuthHydrate } from "@/components/auth/AuthHydrate";
import "./globals.css";
const cormorant = Cormorant_Garamond({
  subsets: ["latin"],
  variable: "--font-cormorant",
  weight: ["400", "600", "700"],
});

const jakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-jakarta",
});

export const metadata = {
  title: "MarryMe — Sistema Interno",
  description: "Plataforma CS e portal de prestadores",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body className={`${cormorant.variable} ${jakarta.variable} font-sans antialiased`}>
        <AuthHydrate />
        {children}
        <Toaster richColors position="top-right" />
      </body>
    </html>
  );
}
