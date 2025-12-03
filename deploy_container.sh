#Exit if anay command fails
set -e


# Variable (will be set by GitHub Actions)
ECR_REGISTRY= ${ECR_REGISTRY}
ECR_REPSONITORY= ${ECR_REPOSITORY}
IMAGE_TAG=${IMAGE_TAG}


#Update system packages
sudo apt-get update

# Install Docker if not installed
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    sudo apt-get install -y apt-transpart-https ca-cartificates curl software-properties-common
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    sudo apt-get update
    sudo apt-get install -y docker-ce
    sudo usermod -aG docker ubuntu
fi 


#Install AWS CLT if not installed
if ! command -v aws &> /dev/null; then
    echo "Installing AWS CLT..."
    sudo apt-get install -y unzip
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip awscliv2.zip
    sudo ./aws/install
fi

# Create nginx config if it does't exist
if [ ! -f "/etc/nginx/sites-available/streamlit" ];
then
    echo "Creating Nginx configuration.."
    cat > /tmp/streamlit_nginx << 'EOL'

server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass https://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgreade;
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400; 
    
    }
}
EOL
    sudo cp /tmp/streamlit_nginx /etc/nginx/sites-available/streamlit
    sudo ln -sf /etc/nginx/sites-available/streamlit /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    sudo nginx -t
    sudo systemct1 restart nginx
fi

# Login to ECR
echo "Logging in to Amazon ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker_login -- username AWS --password-stdin $ {ECT_REGISTRY}

# Stop any running container
echo "Stopping any existing container..."
docker stop streamlit-container 2>/dev/null || true
docker rm streamlit-container 2>/dev/null || true

#Pull the latest image
echo "Pulling the latest image from ECR..."
docker pull ${ECR_REGISTRY}/${ECR_RESPOSITORY}:${IMAGE_TAG}

#Run the container
echo "Starting the container"
docker run -d --name streamlit-container -p8501:8501 --restart always ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}

#Show completed
echo "Deployment completed Successfully!!"