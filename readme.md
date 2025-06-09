# go/: A handy URL shortener that you can self host

Create and manage custom go/ links for any local network or enterprise.

## Step 1: Pull and run the docker container

Pull the latest image
```docker pull akshaykannan/go```

Run the container
```docker run -d -p 80:9999 --restart unless-stopped akshaykannan/go```

The app will be available at `http://localhost` (or on port 80 of the machine you're running it on)

## Step 2: Set up internal DNS to point to the server

Edit `/etc/hosts` on your local machine(s) or Pi-Hole to redirect go/ (or the internal URL of your choice) to the server.

1. Edit your hosts file
	- On Linux/Mac/Pi-Hole: `sudo nano /etc/hosts`
	- On Windows: edit `C:\Windows\System32\drivers\etc\hosts` as an administrator
2. Add the following line to it:
	- ```192.168.0.XXX    go```
		- Replace `192.168.0.XXX` with the IP address of your server running `go` or `127.0.0.1` if running locally
		- Replace `go` with another custom domain name if you desire to use a different name.
3. If on Pi-Hole, restart DNS:
	- `pihole restartdns`


### Local development (optional)

#### Running directly

1. Clone the repo: ```git clone https://github.com/theak/go```
2. In a virtual env, run ```pip install -r requirements.txt```
3. Run ```python app.py init_db``` to initialize the db
4. Run ```FLASK_DEBUG=1 flask run --host=0.0.0.0 --port=9999``` to start the local web server in debug mode with external connections (customize as needed)

#### Building the Docker container locally

1. ```docker build -t go -f Dockerfile .``` to build the docker container
2. ```docker run -it -p 80:9999 go``` to make sure everything works, then ctrl+C to stop
   1. This assumes you want to run on port `80` on the host machine. Change this if you want to run it on a different port.
   2. Navigate to http://192.168.0.xxx/ to load the web interface (replace `192.168.0.xxx` with your server's IP).
   3. Use http://192.168.0.xxx/settings to configure custom settings, such as your domain name if it's not `go/`.
3. ```docker run -d -p 80:9999 --restart unless-stopped go``` to deploy
