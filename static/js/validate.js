import { auth } from "./init.js";

const pathname = window.location.pathname;
if (auth.isAuthenticated) {
  if (pathname === "/signin.html" || pathname === "/signup") {
    window.location.replace("/index.html");
  }
} else {
  if (
    pathname === "/index.html" ||
    pathname === "/index" ||
    pathname === "/" ||
    pathname === "/app" ||
    pathname === "/app.html"
  ) {
    auth.signOut();
    window.location.replace("/signin.html");
  }
}
