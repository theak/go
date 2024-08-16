# go/: A handy URL shortener that you can self host

Create and manage custom go/ links for any local network or enterprise.

## Step 1: Get the server up and running

### Option 1: Deploy via Docker (recommended)

1. Clone the repo: ```git clone https://github.com/theak/go```
2. Run ```cd go```
3. Run ```docker build -t go -f Dockerfile .``` to build the docker container
4. Run ```docker run -it -p 80:9999 go``` to make sure everything works, then ctrl+C to stop
5. Run ```docker run -d -p 80:9999 --restart unless-stopped go```

### Option 2: Run directly (for local dev)

1. Clone the repo: ```git clone https://github.com/theak/go```
2. In a virtual env, run ```pip install -r requirements.txt```
3. Run ```flask --app app --debug run``` to start the local web server in debug mode

## Step 2: Access and configure the server

1. Navigate to http://192.168.0.xxx/ to load the web interface, replacing `192.168.0.xxx` with the IP of your server.
2. Use http://192.168.0.xxx/settings to configure any custom settings, such as the name of the domain you're using if it's anything other than `go/`.


## Step 3: Set up a domain to point to the server

### Option 1: Edit /etc/hosts file on your local machine(s)

1. Edit your hosts file
	- On Linux/Mac: `sudo nano /etc/hosts`
	- On Windows: edit `C:\Windows\System32\drivers\etc\hosts` as an administrator
2. Add the following line to it:
	- ```192.168.0.XXX    go```
		- Replace `192.168.0.XXX` with the IP address of your server.
		- Replace `go` with the custom domain you want to use internally if you're using something else.

### Option 2: Edit /etc/hosts file globally if you're using a custom DNS like pihole

1. If you're using a custom DNS server like Pi-Hole, you only need to do this once and it will work across all devices on your network, including mobile phones.
2. `ssh` into the Pi-Hole and add the same entry above to your `/etc/hosts` file (you will need `sudo`):
	- ```192.168.0.XXX   go```
3. Restart Pi-Hole DNS with `pihole restartdns`
