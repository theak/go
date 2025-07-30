# go/: Self-hosted URL shortener

Create and manage custom go/ links for local networks or enterprises. Simple, fast, open source.

Create custom redirects like:
`go/short-url` → https://example.com/my-much-longer-url

<img width="969" height="502" alt="image" src="https://github.com/user-attachments/assets/702b0971-c703-4a00-9b36-e6f127c0120b" />


## Installation

### Step 1: Run the Docker container

```bash
# Pull the latest image
docker pull akshaykannan/go

# Run the container
docker run -d -p 80:9999 --restart unless-stopped -v [/host/path/to/db]:/go/db akshaykannan/go
```

The app will be available at `http://localhost` (or port 80 of your machine).

**Note:** Replace `[/host/path/to/db]` with where you want to persist the database on the host.

### Step 2: Configure DNS for `go` to work

1. Edit your `hosts` file:
- On Linux/Mac/Pi-hole: `sudo nano /etc/hosts`
- On Windows: edit `C:\Windows\System32\drivers\etc\hosts` as administrator
2. Add this line:
  ```192.168.0.[xxx]   go```

  Replacing the first part with the ip address of your machine running the `go` docker container (use 127.0.0.1 if you're running it on your local machine).

Access the web interface at `http://192.168.0.xxx/` and configure settings at `http://192.168.0.xxx/settings`.

And that's it! You're now up and running with your own `go/` redirection service.

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
