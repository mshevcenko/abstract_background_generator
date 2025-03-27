<a href="https://hub.docker.com/repository/docker/zeltronick/abstract-background-generator/general">Docker hub repository</a>

### Docker api image run command
```bash
docker run --name api -p 8000:8000 -d zeltronick/abstract-background-generator
```

### Docker ui image run command
```bash
docker run -d -p 5002:1573 artemiikolomiichuk/abstractimages
```

### Docker mongo image run command
```bash
docker run --name mongodb -p 27017:27017 -d mongo
```

### Docker compose file run command
```bash
 docker-compose up --build
```