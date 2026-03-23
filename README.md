# Mission Control Dashboard

## Running Locally
- Open a terminal and `cd` to the `Mission-Control` directory.
- Run a local server using Python 3:
  ```
  python3 -m http.server 8080
  ```
- Open your browser and go to `http://localhost:8080` to view the dashboard.

## Deployment to Vercel
- Ensure you have the [Vercel CLI](https://vercel.com/cli) installed and configured.
- Within the `Mission-Control` directory, run:
  ```
  vercel deploy --prod
  ```
- For API access during deployment, ensure Tailscale is configured and the OpenClaw API endpoint is accessible via
  `http://100.125.39.76:18789` (adjust IP as needed).

## Updating Data
- Edit the markdown files in the `data` directory:
  - `kanban.md` for Kanban tasks
  - `blockers.md` for blockers
- The dashboard auto-refreshes every 30 seconds to reflect changes.
