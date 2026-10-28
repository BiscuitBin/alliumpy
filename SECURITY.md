# Security policy

docmirror fetches untrusted HTML from the public web and writes files under the output
directory the user names. Report a vulnerability through a private channel to the
repository owner rather than a public issue, and expect an acknowledgement before any
public discussion.

What the tool does not do: it never executes fetched content outside the browser tier's
sandbox, never writes outside the output directory, never stores credentials, and never
uses proxies, CAPTCHA solvers or paid unblocking services. Cookies a browser tier
collects are kept under `<out>/.docmirror/browser/` and copied only into the same host's
HTTP session.
