#sequbot-ai

##Install docker

Follow the [docker installation instructions](https://docs.docker.com/engine/installation/) for your distro.


##Create the image
```bash
docker build -t sequbot-ai .
```

##To run the hive server
```bash
docker sequbot-ai run server
```

##To run a hive node
```bash
docker sequbot-ai run node
```
