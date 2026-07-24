
Core
- Async Python (asyncio) — everything here runs concurrently across threads/wallets
- HTTP client work (likely httpx/aiohttp) — API calls, headers, cookies, session handling
- SQLite/ORM basics — database.py tracks per-wallet state so runs are resumable

Crypto-specific
- EVM wallet mechanics — private keys, signing messages, eth_account-style libraries
- Privy auth flow — a lot of Web3 apps use Privy for embedded-wallet login; understanding its token/session/refresh dance (seen in privy.py) is fairly niche but reusable across similar projects

Infra/reliability
- Proxy rotation and per-account proxy binding
- Retry/backoff patterns (retry.py) — network calls to third-party sites fail a lot
- Rate limiting / jittered sleep between accounts to avoid bans

Ops/UX
- loguru (colored console logging, easy .opt(colors=True) tags)
- Config-as-code pattern (settings.py as plain constants — simple and effective for this scale)
- Excel/CSV export for reporting results back to a human

Useful skills for harness engineering, write this skills into library