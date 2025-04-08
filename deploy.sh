#!/bin/bash

# Install Wrangler if not installed
if ! command -v wrangler &> /dev/null
then
    echo "Installing wrangler..."
    npm install -g wrangler
fi

# Login to Cloudflare if needed
echo "Checking Cloudflare authentication..."
wrangler whoami || wrangler login

# Set environment variables for production
echo "Setting environment variables..."
wrangler secret put OLLAMA_BASE_URL
wrangler secret put CLOUDFLARE_DEPLOYMENT --value "true"
wrangler secret put LANGFLOW_ENABLED --value "false"

# Deploy to Cloudflare Workers
echo "Deploying to Cloudflare Workers..."
wrangler deploy --env production

echo "Deployment complete!"