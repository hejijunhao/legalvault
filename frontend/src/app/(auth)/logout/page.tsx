// src/app/logout/page.tsx

// This is a simple logout handler that redirects to the login page
// In the future, this will handle proper session cleanup
import { redirect } from "next/navigation"

export default function LogoutPage() {
  redirect("/login")
}

