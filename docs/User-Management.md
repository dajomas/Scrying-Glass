# SQLite accounts and user management

## Upgrade

1. Stop Scrying Glass and back up configuration and the entire storage directory.
2. Extract the changed-files archive over the existing source tree. Do not replace your live config.yaml with config.example.yaml.
3. Start using the existing configuration, including security.users, once.
4. SQLite schema v4 is created automatically. Existing version 3 databases are backed up using the existing .before-normalization.bak naming convention. Versions 1 and 2 retain their previous normalization upgrade and backup, then receive account tables.
5. All legacy accounts are imported atomically. Plaintext passwords are converted to salted scrypt hashes; valid existing scrypt hashes are retained. Usernames are case-sensitive and unique, 1-64 characters without control characters or surrounding whitespace. Duplicate usernames or malformed accounts stop initialization rather than partially importing.
6. If no legacy superadmin exists, the first legacy admin in configuration order is promoted to superadmin. Other roles are retained. Sign in with that account's existing password.
7. Open User management in the admin interface, or /users on the admin port.
8. After verifying login, remove security.users from your live configuration. The application does not rewrite that file. Once migration is recorded, configuration accounts are ignored permanently: they cannot overwrite passwords or resurrect deleted users.

## Fresh installation

There are no default accounts/passwords in configuration. On first account initialization, if no imported account can serve as superadmin, the app creates a superadmin account with a random password and prints its credentials once to startup stdout. With systemd, these may be captured by the journal; protect those logs. Change that password in /users immediately. A conflicting username is handled by appending underscores. There is no default client account: create one through user management.

## Permissions

| Role | Display | Battle administration | User management |
|---|---|---|---|
| client | Yes | No | No |
| admin | Yes | Yes | No |
| superadmin | Yes | Yes | Yes |

User management supports creation, username and role changes, password resets, and deletion. Passwords are never returned to the browser. New/reset passwords must be 8-1024 characters; shorter legacy passwords remain usable until changed. Leave the edit password field empty to preserve the hash. APIs accept only username, role, password. PATCH omits password to preserve it; null/empty password is rejected.

The last superadmin cannot be deleted or demoted. Modifying any account invalidates its sessions on both interfaces and closes its connected display sockets; changing your own account returns you to login. API authorization reads current database roles, not only the session's cached role. Cross-origin browser mutation requests are rejected.

## Routes (admin port)

- GET /api/me: current administrator username and role.
- GET /users: management UI (superadmin only).
- GET /api/users: id, username, role only.
- POST /api/users: username, role, password; returns 201.
- PATCH /api/users/{id}: one or more editable fields.
- DELETE /api/users/{id}: removes an account.

Unauthenticated API access returns 401; insufficient permissions return 403; unknown user IDs return 404; duplicates or the last-superadmin guard return 409; invalid fields return 422.

## Operations

Accounts share the existing scrying-glass.sqlite3 database, so database backups include password hashes. Keep database files and logs restricted, use HTTPS through a properly configured proxy, and retain the application's single-process shared-state deployment. The config example now contains only application settings.

To recover a lost superadmin password: stop the application, generate a hash using python.scrying_glass_init.password_hash, and use a parameterized SQLite UPDATE for the intended account's password_hash (and role='superadmin' if necessary). Back up the database first. This is an offline administrative operation, not a configuration-based reset.

## Validation

Run `python -m unittest discover -s tests -v` with the application's dependencies installed. Account unit tests cover migration, authorization dependencies, CRUD, validation, session revocation and schema v3 upgrades. They call endpoints directly rather than through HTTP routing; when FastAPI is unavailable, minimal dependency/response substitutes are used. Full server and browser integration must also be tested in the deployed environment. The changed-files archive includes tests and this guide; it contains no live configuration or database.
