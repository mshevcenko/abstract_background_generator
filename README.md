<a href="https://hub.docker.com/repository/docker/zeltronick/abstract-background-generator/general">Docker hub repository</a>

### Docker api image run command
```bash
docker run --name api -p 8000:8000 -d -e MONGO_URL="host.docker.internal:27017" zeltronick/abstract-background-generator
```

### Docker ui image run command
```bash
docker run --name ui -p 1573:1573 -d artemiikolomiichuk/abstractimages
```

### Docker mongo image run command
```bash
docker run --name mongodb -p 27017:27017 -d mongo
```

### Docker compose file run command
```bash
docker-compose up --build
```

### Docker build api command
```bash
docker build -t zeltronick/abstract-background-generator .
```

### Docker push api command
```bash
docker push zeltronick/abstract-background-generator
```