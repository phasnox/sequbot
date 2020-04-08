SEQUBOT_ENV=$1

# Remove image
echo "Stopping all"
docker-compose down

echo "Pulling sequbot_data"
(cd ~/src/sequbot/sequbot_data/ && git fetch --all && git reset --hard origin/$SEQUBOT_ENV)

echo "Pulling sequbot_ai"
(cd ~/src/sequbot/sequbot_ai/ && git fetch --all && git reset --hard origin/$SEQUBOT_ENV)

if [ "$2" == "rebuild" ]; then
    echo "Rebuilding docker image"
    docker-compose build
fi

echo "Starting server"
docker-compose up -d
