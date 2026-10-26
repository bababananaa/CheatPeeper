// The top-level component of the app.
//
// Right now the login page is the only screen, so it's what every user sees
// first. When we add more pages in later sprints (and decide where to go after
// signing in), this is where we'll choose which page to show.
import LoginPage from './pages/LoginPage.tsx'

export default function App() {
  return <LoginPage />
}
