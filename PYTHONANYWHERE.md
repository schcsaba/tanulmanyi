# Deploying on PythonAnywhere

Production runs on the EU PythonAnywhere site (<https://eu.pythonanywhere.com>, servers in Frankfurt) under the
`bhfto` account, without Docker. The Docker setup in this repository is for development and testing.

Run all commands below in a **Bash console on PythonAnywhere** (Consoles tab), not on your own machine.
Before deploying, run the test suite locally with `make test`.

## Where things live

| What | Where |
|---|---|
| Code (git checkout of `main`) | `/home/bhfto/tanulmanyi` |
| Settings / secrets | `/home/bhfto/tanulmanyi/.env` (read by `python-decouple`, never committed) |
| Uploaded files (regulations, timetables) | `/home/bhfto/media/` |
| Collected static files (admin, TinyMCE) | `/home/bhfto/tanulmanyi/static/` (generated, not in git) |
| System image / Python | **innit** (Ubuntu 22.04), Python 3.13 |
| Virtualenv | `/home/bhfto/.virtualenvs/tanulmanyi313` (set on the Web tab) |
| Database | MySQL 8, `bhfto$...` database; host and name on the Databases tab |
| Logs | Web tab → "Log files" (error log, server log) |
| DNS and HTTPS in front of the site | Cloudflare, `bhf.hu` zone (see "Cloudflare" below) |

### `.env` keys

| Key | Value on PythonAnywhere |
|---|---|
| `SECRET_KEY` | the production secret key |
| `DEBUG` | `False` (the default is `False`, but set it explicitly) |
| `ALLOWED_HOST` | the site's host name(s), comma-separated |
| `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE` | keep the current values |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` | from the Databases tab |
| `MEDIA_ROOT` | `/home/bhfto/media/` (**required**: the default is `media/` inside the repo) |
| `STATIC_ROOT` | optional; the default `/home/bhfto/tanulmanyi/static` matches the Web tab mapping |

### Web tab

- **Static files:** URL `/static/` → directory `/home/bhfto/tanulmanyi/static`.
- **Do not map `/media/`.** Uploaded files are served through the app, which checks who may download them
  (some regulations are for teachers only). A static mapping would let anyone download them without logging in.
- **Virtualenv** and **Python version**: must match (see below).

## Cloudflare

Since October 2026 the `bhf.hu` DNS is on Cloudflare, and `tanulmanyi.bhf.hu` is proxied through it (orange cloud):
visitors connect to Cloudflare, Cloudflare connects to PythonAnywhere.

- **The `bhf.hu` zone's SSL/TLS mode is "Flexible"**, because the server behind `bhf.hu` does not work with "Full".
- **A Configuration Rule switches `tanulmanyi.bhf.hu` to "Full":** Rules → "+ Create rule" → Configuration Rule;
  condition Hostname equals `tanulmanyi.bhf.hu`; setting SSL = Full.
- **Why the rule is needed:** with "Flexible", Cloudflare reaches PythonAnywhere over plain HTTP, PythonAnywhere's
  "Force HTTPS" redirects to HTTPS, and the browser ends up in an endless redirect loop ("too many redirects").
  Don't fix that by turning off Force HTTPS: the traffic between Cloudflare and PythonAnywhere would then be
  unencrypted.
- **To do:** PythonAnywhere has no certificate for `tanulmanyi.bhf.hu` yet; it presents its own
  `*.eu.pythonanywhere.com` one. Create a Cloudflare Origin Certificate (SSL/TLS → Origin Server), install it on
  the Web tab under "Security", reload, then change the rule's SSL setting from Full to **Strict**.

If the site shows "too many redirects" again, check that the rule still exists and is enabled.

## Routine deployment (code changes only)

Use this when `requirements.txt` has not changed.

```bash
cd ~/tanulmanyi
workon tanulmanyi313
git pull
python manage.py migrate
python manage.py collectstatic --noinput
```

Then press **Reload** on the Web tab and check the error log.

If `requirements.txt` changed, run `pip install -r requirements.txt` after `git pull` (inside the virtualenv),
or for bigger upgrades build a fresh virtualenv as in the sections below.

## Switching the system image: haggis → innit, Python 3.10 → 3.13 (done October 2026)

Kept for reference. The account was on the **haggis** system image (Ubuntu 20.04), whose newest Python is 3.10. Python 3.10 reaches end
of life in October 2026, and Django 6 will need Python 3.12 or newer. The **innit** image (Ubuntu 22.04) offers
Python 3.13, the version the Docker setup uses.

Only the Python version changes: no `git pull`, no migrations, no `collectstatic`. Switching the image can break the
current virtualenv, and the Python 3.13 one can only be built after the switch, so do this at a quiet time.

1. Account page → "System image" tab → pencil icon → **innit**.
2. Build the new virtualenv:

   ```bash
   rm -rf ~/.cache/pip
   mkvirtualenv --python=python3.13 tanulmanyi313
   pip install -r ~/tanulmanyi/requirements.txt
   cd ~/tanulmanyi
   python manage.py check
   ```

   If the name `tanulmanyi313` is already taken by a leftover virtualenv, remove it first with
   `rmvirtualenv tanulmanyi313` or pick another name.
3. On the Web tab set **Virtualenv** to `/home/bhfto/.virtualenvs/tanulmanyi313` and **Python version** to 3.13,
   then press **Reload**.
4. If scheduled or always-on tasks run this code, point them at `/home/bhfto/.virtualenvs/tanulmanyi313/bin/python`.
5. Run the smoke test (step 5 of the Django upgrade section below) and check the error log.

**Rollback:** innit also has Python 3.10. Build a 3.10 virtualenv
(`mkvirtualenv --python=python3.10 tanulmanyi310b`, then `pip install -r ~/tanulmanyi/requirements.txt`), set it and
Python 3.10 on the Web tab, and reload.

**Afterwards:** once the site has run fine for a few days, delete the old virtualenvs (Python 3.10 and 3.8) with `rmvirtualenv <name>`.

## One-time upgrade: Django 4.2 → 5.2 (done October 2026)

Kept for reference; it ran on haggis with Python 3.10.

Django 5.2 needs Python 3.10 or newer; the old virtualenv is most likely on Python 3.8 (the Web tab shows it). MySQL
is already on version 8, which Django 5.2 requires. The database schema does not change: the new migrations produce no SQL.

The idea: prepare everything (backup, new virtualenv) while the old version keeps running, then switch over in a
couple of minutes and keep the old virtualenv for rollback.

### 1. Back up (site keeps running)

```bash
cd ~
git -C ~/tanulmanyi rev-parse HEAD > ~/pre-upgrade-commit.txt
mysqldump -u bhfto -h <host from the Databases tab> --set-gtid-purged=OFF --no-tablespaces --column-statistics=0 'bhfto$<database>' > ~/db-backup-$(date +%F).sql
tar czf ~/media-backup-$(date +%F).tar.gz -C /home/bhfto media
cp ~/tanulmanyi/.env ~/env-backup-$(date +%F)
```

The single quotes around the database name are needed because of the `$`. If `mysqldump` says access denied,
add `-p` to be prompted for the database password.

### 2. Check the system image and pick the Python version (site keeps running)

Account page → "System image" tab.

- **innit**: use Python 3.13 (same as the Docker setup).
- **haggis**: use Python 3.10. The app is tested on it, and you avoid switching images during the upgrade.
  Moving to innit and Python 3.13 can be done later as a separate change.
- **anything older**: switch to innit first, **as a separate step on an earlier day**. Switching can break existing
  virtualenvs, including the one you need for rollback. After switching (pencil icon next to the image name),
  run `rm -rf ~/.cache/pip`, reload the site and check it still works on the old code. If it doesn't, rebuild the
  old virtualenv from the current `requirements.txt` with the same Python version, so rollback has a working
  environment.

The commands below use `python3.13` and the name `tanulmanyi313`; on haggis use `python3.10` and e.g.
`tanulmanyi310` instead.

### 3. Build the new virtualenv from the new code (site keeps running)

Install the new requirements without touching the running checkout:

```bash
cd ~/tanulmanyi
git fetch
git show origin/main:requirements.txt > /tmp/requirements-new.txt
mkvirtualenv --python=python3.13 tanulmanyi313
pip install -r /tmp/requirements-new.txt
python -c "import django, MySQLdb; print(django.get_version())"
```

The last line should print `5.2.17`. If `mysqlclient` fails to build, the system image is the usual cause (see
step 2).

### 4. Switch over (a few minutes)

```bash
cd ~/tanulmanyi
git status
```

If `git status` lists changes under `static/`, discard them (they are generated): `git checkout -- static`.

```bash
git pull
```

This removes the old `static/` files from the checkout; `collectstatic` below recreates them. Add
`MEDIA_ROOT=/home/bhfto/media/` to `~/tanulmanyi/.env` (and `DEBUG=False` if missing), then:

```bash
workon tanulmanyi313
python manage.py check
python manage.py migrate
python manage.py collectstatic --noinput
```

On the Web tab:

1. Set **Virtualenv** to `/home/bhfto/.virtualenvs/tanulmanyi313`.
2. Set **Python version** to 3.13 (the version the virtualenv was built with).
3. Press **Reload**.

If there are scheduled or always-on tasks (Tasks tab) that run this code, point them at
`/home/bhfto/.virtualenvs/tanulmanyi313/bin/python` too.

### 5. Smoke test

- Log in as a student and as a teacher; the menu should differ (teachers see "Féléves kurzusok", "Jegyzetfelelősök").
- Szakdolgozatok → "Témavezetők és témaköreik": opens quickly, sections expand.
- "Megírt és folyamatban lévő szakdolgozatok": search for a title with two words; both stay in the search box.
- Mintatantervek: open a curriculum.
- Szabályzatok: download one; as a student, a teacher-only one is refused.
- Admin: open a list page and the "Beállítások" editor (TinyMCE); styling must look normal.
- As staff: download the autumn course list (XLSX).
- Web tab → error log: no new errors.

### Rollback

On the Web tab set the old virtualenv and Python version again, then:

```bash
cd ~/tanulmanyi
rm -rf static
git reset --hard $(cat ~/pre-upgrade-commit.txt)
```

and press **Reload**. The old commit still has the committed `static/` files, and the database needs no rollback
(the schema did not change). Remove `MEDIA_ROOT` from `.env` only if you want to be tidy; the old code ignores it.
