// Everything to do with talking to the backend about signing in lives here,
// so the page components don't need to know any of the HTTP details.

// Where the FastAPI backend is running.
// It can be changed in frontend/.env (see .env.example); otherwise we use the
// address the backend runs on during local development.
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// What the backend sends back when sign in works (see Token in backend/schemas.py).
export type LoginResponse = {
  access_token: string // proves who the user is; sent with future requests
  token_type: string // always "bearer"
}

// Sends the email and password to the backend.
// - If they're correct, returns the access token.
// - If anything goes wrong, throws an Error with a message that's safe to
//   show directly to the user.
export async function login(email: string, password: string): Promise<LoginResponse> {
  // The backend's /auth/login uses the standard OAuth2 login format: it expects
  // a *form* (not JSON), and the field must be named "username" even though
  // we're sending an email. The backend accepts an email in that field.
  //
  // URLSearchParams builds the form body ("username=...&password=..."), and
  // fetch automatically sets the matching Content-Type header for it.
  const formData = new URLSearchParams({ username: email, password })

  let response: Response
  try {
    response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      body: formData,
    })
  } catch {
    // fetch only throws when no response came back at all, e.g. the backend
    // isn't running or the user is offline.
    throw new Error("Can't reach the server. Please try again in a moment.")
  }

  // A 2xx status code means the login worked. The body holds the token.
  if (response.ok) {
    return (await response.json()) as LoginResponse
  }

  // Otherwise, turn the backend's status code into a friendly message.
  // These codes come from the login route in backend/main.py.
  if (response.status === 401) {
    throw new Error('Incorrect email or password.')
  }
  if (response.status === 403) {
    throw new Error('Please verify your email before signing in.')
  }
  throw new Error('Something went wrong. Please try again.')
}
