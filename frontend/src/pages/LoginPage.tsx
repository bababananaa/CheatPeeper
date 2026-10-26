// The login screen: the first thing a user sees when they open the app.
//
// How it works:
//   1. The user types their email and password.
//   2. When they press "Sign In", we check the inputs (validateForm).
//   3. If the inputs look OK, we send them to the backend (login() in api/auth.ts).
//   4. We show a success message or an error message. The user stays on this
//      page either way. Moving to another page after signing in is for a later sprint.
import { useState, type SubmitEvent } from 'react'
import { login } from '../api/auth.ts'

// Only UF emails can sign up (see require_ufl in backend/schemas.py), so we
// catch anything else right away instead of asking the backend.
// This pattern means: some characters with no spaces or "@", then "@ufl.edu".
const UF_EMAIL_PATTERN = /^[^\s@]+@ufl\.edu$/

// Checks what the user typed before we contact the backend.
// Returns a message describing the problem, or null if everything looks fine.
function validateForm(email: string, password: string): string | null {
  if (!email) return 'Please enter your email.'
  if (!UF_EMAIL_PATTERN.test(email)) return 'Please use your @ufl.edu email.'
  if (!password) return 'Please enter your password.'
  return null
}

// Who is signed in, once login works.
type Session = {
  email: string
  // The access token from the backend. It isn't used yet. In later sprints
  // we'll send it with requests (as "Authorization: Bearer <token>") so the
  // backend knows who is asking. It only lives in memory, so refreshing the
  // page signs the user out.
  token: string
}

// Tailwind classes shared by both text boxes, giving the iOS look: light gray
// rounded box that turns white with a turquoise outline when you click into it.
// (The 17px text size matches iOS, and anything 16px or larger also stops
// iPhones from zooming in when the box is tapped.)
const inputClasses =
  'h-12 w-full rounded-xl bg-neutral-100 px-4 text-[17px] text-black placeholder:text-neutral-400 ' +
  'outline-none transition focus:bg-white focus:ring-2 focus:ring-turquoise-400'

export default function LoginPage() {
  // ----- State: values React remembers between renders -----
  // Calling a "set..." function updates the value and redraws the page.

  const [email, setEmail] = useState('') // what's typed in the email box
  const [password, setPassword] = useState('') // what's typed in the password box
  const [showPassword, setShowPassword] = useState(false) // is the password visible?
  const [isLoading, setIsLoading] = useState(false) // waiting on the backend?
  const [error, setError] = useState<string | null>(null) // error to show (null = none)
  const [session, setSession] = useState<Session | null>(null) // null = not signed in

  // Runs when the form is submitted (clicking "Sign In" or pressing Enter).
  async function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    // By default the browser reloads the page when a form is submitted.
    // We stop that because we handle the submission ourselves.
    event.preventDefault()

    // Clear any message left over from the previous attempt.
    setError(null)
    setSession(null)

    // Remove accidental spaces and lowercase the email, since emails
    // aren't case-sensitive (the backend stores them lowercase too).
    const cleanEmail = email.trim().toLowerCase()

    // Stop here if the inputs aren't valid.
    const problem = validateForm(cleanEmail, password)
    if (problem) {
      setError(problem)
      return
    }

    setIsLoading(true) // shows the spinner and disables the button
    try {
      const { access_token } = await login(cleanEmail, password)
      setSession({ email: cleanEmail, token: access_token })
    } catch (err) {
      // login() throws errors with user-friendly messages, so show them as-is.
      setError(err instanceof Error ? err.message : 'Something went wrong. Please try again.')
    } finally {
      // "finally" runs whether it worked or not, so the spinner always stops.
      setIsLoading(false)
    }
  }

  // ----- What appears on screen -----
  return (
    // Full-screen background: a soft white-to-turquoise gradient,
    // with the card centered in the middle.
    <main className="flex min-h-dvh items-center justify-center bg-linear-to-br from-white via-turquoise-50 to-turquoise-100 px-5 py-12">
      {/* The white card. It fades in gently when the page loads. */}
      <div className="w-full max-w-sm animate-fade-in rounded-3xl bg-white p-8 shadow-xl ring-1 shadow-turquoise-700/10 ring-black/5">
        {/* App name, in bold black like an iOS "large title" */}
        <header className="mb-8 text-center">
          <h1 className="text-[34px] font-bold tracking-tight text-black">CheatPeeper</h1>
          <p className="mt-1 text-[15px] text-neutral-500">Sign in with your UF email</p>
        </header>

        {/*
          noValidate turns off the browser's built-in popup warnings so our own
          messages (from validateForm) are shown instead, in a consistent style.
        */}
        <form onSubmit={handleSubmit} noValidate className="space-y-4">
          {/* ----- Email field ----- */}
          <div>
            <label htmlFor="email" className="mb-1.5 block text-[13px] font-medium text-neutral-500">
              Email
            </label>
            <input
              id="email"
              type="email" // shows the email keyboard on phones
              autoComplete="email" // lets the browser/password manager fill it in
              placeholder="albert@ufl.edu"
              value={email}
              onChange={(e) => setEmail(e.target.value)} // save every keystroke in state
              className={inputClasses}
            />
          </div>

          {/* ----- Password field ----- */}
          <div>
            <div className="mb-1.5 flex items-center justify-between">
              <label htmlFor="password" className="block text-[13px] font-medium text-neutral-500">
                Password
              </label>
              {/* Placeholder only: the backend has no password reset yet. */}
              <button type="button" className="text-[13px] font-medium text-turquoise-700 hover:opacity-70">
                Forgot password?
              </button>
            </div>

            {/* "relative" lets us place the Show/Hide button inside the box. */}
            <div className="relative">
              <input
                id="password"
                // Switching the type between "password" and "text" hides or shows it.
                type={showPassword ? 'text' : 'password'}
                autoComplete="current-password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className={`${inputClasses} pr-16`} // extra right padding so text doesn't run under the button
              />
              <button
                type="button" // "button" (not "submit") so clicking it doesn't submit the form
                onClick={() => setShowPassword(!showPassword)}
                aria-label={showPassword ? 'Hide password' : 'Show password'} // read aloud by screen readers
                className="absolute inset-y-0 right-0 px-4 text-[15px] font-medium text-turquoise-700 hover:opacity-70"
              >
                {showPassword ? 'Hide' : 'Show'}
              </button>
            </div>
          </div>

          {/*
            Messages. "cond && <element>" means: only show the element when the
            condition is true. role="alert"/"status" makes screen readers announce them.
          */}
          {error && (
            <p role="alert" className="rounded-xl bg-red-50 px-4 py-3 text-[15px] text-red-600">
              {error}
            </p>
          )}
          {session && (
            <p role="status" className="flex items-center gap-2 rounded-xl bg-emerald-50 px-4 py-3 text-[15px] text-emerald-700">
              <CheckIcon />
              Signed in as {session.email}
            </p>
          )}

          {/* ----- Sign In button ----- */}
          <button
            type="submit"
            disabled={isLoading} // prevents double-submitting while we wait
            // active:scale shrinks the button a little while pressed, like iOS.
            className="flex h-12 w-full items-center justify-center gap-2 rounded-xl bg-turquoise-600 text-[17px] font-semibold text-white transition hover:brightness-95 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-70"
          >
            {isLoading ? (
              <>
                <Spinner />
                Signing in…
              </>
            ) : (
              'Sign In'
            )}
          </button>
        </form>

        {/* Placeholder only: there's no sign-up page yet. */}
        <p className="mt-8 text-center text-[15px] text-neutral-500">
          Don't have an account?{' '}
          <button type="button" className="font-semibold text-turquoise-700 hover:opacity-70">
            Create one
          </button>
        </p>
      </div>
    </main>
  )
}

// A small spinning circle shown in the button while we wait for the backend.
// It's a round border with one side solid white, rotated by animate-spin.
// aria-hidden hides it from screen readers, since the "Signing in…" text already says what's happening.
function Spinner() {
  return (
    <span
      aria-hidden="true"
      className="size-5 animate-spin rounded-full border-2 border-white/40 border-t-white"
    />
  )
}

// A check mark inside a circle, shown in the success message.
function CheckIcon() {
  return (
    <svg aria-hidden="true" viewBox="0 0 20 20" fill="currentColor" className="size-5 shrink-0">
      <path
        fillRule="evenodd"
        d="M10 18a8 8 0 1 0 0-16 8 8 0 0 0 0 16Zm3.857-9.809a.75.75 0 0 0-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 1 0-1.06 1.061l2.5 2.5a.75.75 0 0 0 1.137-.089l4-5.5Z"
        clipRule="evenodd"
      />
    </svg>
  )
}
