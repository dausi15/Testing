import docker
import time
from hypothesis import given
from hypothesis.strategies import text

client = docker.from_env()
#client.containers.run("ubuntu:latest", "echo hello world")
#client.containers.run("bfirsh/reticulate-splines", detach=True)
print(client.containers.list())
client.containers.prune()
print(client.containers.list())
cons = client.containers.list()
for con in cons:
    print(con.id)
    con.kill()
client.containers.prune()

#client.containers.run("nginx","echo hello world")
client.containers.run("bfirsh/reticulate-splines", "echo hello world")
print("going to sleep")
print(client.containers.list())
#client.images.pull('nginx')
#client.images.list()