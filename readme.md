# go/: Self-hosted URL shortener

Create and manage custom go/ links for local networks or enterprises. Open source, simple (<200 lines of code), and fast.

Create custom redirects like:
`go/short-url` → https://example.com/my-much-longer-url

## Installation

### Step 1: Run the service as a Docker container

```bash
# Pull the latest image
docker pull akshaykannan/go

# Run the container
docker run -d -p 80:9999 --restart unless-stopped -v /host/path/to/db:/go/db akshaykannan/go
```

The app will be available at `http://localhost` (or port 80 of your machine).

**Note:** Replace `/host/path/to/db` with where you want to persist the database.

### Step 2: Set up DNS

Configure your DNS to point `go` to your server by editing your `hosts` file:
- On Linux/Mac/Pi-hole: `sudo nano /etc/hosts`
- On Windows: edit `C:\Windows\System32\drivers\etc\hosts` as administrator

If on Pi-hole, then run: `pihole restartdns`

Access the web interface at `http://192.168.0.xxx/` and configure settings at `http://192.168.0.xxx/settings`.


## Local Development (only if you want to make changes)

1. Clone the repository: `git clone https://github.com/theak/go`

2. Set up Python environment: `pip install -r requirements.txt`

3. Initialize database: `python app.py init_db`

4. Run tests: `bash pytest test_app.py`

5. Start development server: `FLASK_DEBUG=1 flask run --host=0.0.0.0 --port=9999`

### Building Docker image

```bash
# Build for current architecture
docker build -t go -f Dockerfile .

# Build for multiple architectures
docker buildx build --platform linux/amd64,linux/arm64 -t go -f Dockerfile .

# Build and push to registry
docker buildx build --platform linux/amd64,linux/arm64 -t akshaykannan/go -f Dockerfile . --push

# Test the image
docker run -it -p 80:9999 go

# Deploy
docker run -d -p 80:9999 --restart unless-stopped -v /path/to/go-db:/go/db go
```
