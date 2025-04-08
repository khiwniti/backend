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

# Create or update KV namespaces if they don't exist
echo "Setting up KV namespaces..."
wrangler kv:namespace create "FLOW_KV" 2>/dev/null || true
wrangler kv:namespace create "CACHE_KV" 2>/dev/null || true

# Create D1 database if it doesn't exist
echo "Setting up D1 database..."
wrangler d1 create bitebase_db 2>/dev/null || true

# Set environment variables for production
echo "Setting environment variables..."
wrangler secret put OLLAMA_BASE_URL
wrangler secret put CLOUDFLARE_DEPLOYMENT --value "true"
wrangler secret put LANGFLOW_ENABLED --value "false"

# Deploy to Cloudflare Workers
echo "Deploying to Cloudflare Workers..."
wrangler deploy --env production

echo "Deployment complete!"
