import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Tattoo Portal",
  description: "Discover tattoo designs you would seriously consider getting.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
