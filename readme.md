# go/: Self-hosted URL shortener

Create and manage custom go/ links for local networks or enterprises. Simple, fast, open source.

Create custom redirects like:
`go/short-url` → https://example.com/my-much-longer-url

<img width="969" height="502" alt="image" src="https://github.com/user-attachments/assets/702b0971-c703-4a00-9b36-e6f127c0120b" />


## Installation

### Step 1: Run the Docker container

**Run the container directly, or use [docker compose](https://www.composerize.com/):**
```bash
docker run -d -p 80:9999 --restart unless-stopped -v [your_backup_dir]:/go/db akshaykannan/go
```

The web interface will be available at `http://localhost/` (or port 80 of the server running the container).

### Step 2: Configure DNS for `go/` to point to the Docker container

1. Edit your `hosts` file:
- On Linux/Mac: `sudo nano /etc/hosts`
- On Windows: edit `C:\Windows\System32\drivers\etc\hosts` as administrator

2. Add this line:
  ```192.168.0.[xxx]   go```

Replace the ip address with the ip address of the server running `go` (use `127.0.0.1` if it's your local machine).

3. Access the web interface at `http://go/` and configure settings at `http://go/settings`. Once you've done this once, your browser should remember this and let you type in go/linkname.

And that's it! You're now up and running with your own local, private `go/` URL redirection service.

## Local Development (only if you want to make changes)

1. Clone the repository: `git clone https://github.com/theak/go`
2. Set up Python environment: `pip install -r requirements.txt`
3. Initialize database: `python app.py init_db`
4. Run tests: `pytest test_app.py`
5. Start development server: `FLASK_DEBUG=1 flask run --host=0.0.0.0 --port=9999`

