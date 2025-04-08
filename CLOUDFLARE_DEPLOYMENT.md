# Deploying to Cloudflare Workers

This guide explains how to deploy the BiteBase Intelligence API to Cloudflare Workers.

## Prerequisites

1. A Cloudflare account
2. Node.js and npm installed
3. Wrangler CLI installed (`npm install -g wrangler`)

## Configuration

The application has been configured to work in both local development and Cloudflare Workers environments. The key changes include:

1. Using Cloudflare KV for storage instead of local file system
2. Providing fallbacks for dependencies that don't work in Cloudflare Workers
3. Setting environment variables to control behavior in different environments

## Deployment Steps

1. **Login to Cloudflare**

   ```bash
   wrangler login
   ```

2. **Configure your Cloudflare account**

   Make sure your `wrangler.toml` file has the correct account ID and zone ID.

3. **Set up KV namespaces**

   The application uses two KV namespaces: `FLOW_KV` and `CACHE_KV`. These are already defined in the `wrangler.toml` file, but you need to make sure they exist in your Cloudflare account.

   ```bash
   wrangler kv:namespace create "FLOW_KV"
   wrangler kv:namespace create "CACHE_KV"
   ```

   Then update the `wrangler.toml` file with the IDs returned by these commands.

4. **Set up D1 database**

   The application uses a D1 database for persistent storage. Create it with:

   ```bash
   wrangler d1 create bitebase_db
   ```

   Then update the `wrangler.toml` file with the database ID.

5. **Set environment variables**

   ```bash
   wrangler secret put OLLAMA_BASE_URL --env production
   wrangler secret put CLOUDFLARE_DEPLOYMENT --value "true" --env production
   wrangler secret put LANGFLOW_ENABLED --value "false" --env production
   ```

6. **Deploy the application**

   ```bash
   ./deploy.sh
   ```

   Or manually:

   ```bash
   wrangler deploy --env production
   ```

## Troubleshooting

### Common Issues

1. **File system access errors**

   Cloudflare Workers don't have access to a persistent file system. Make sure all file operations use KV or D1 instead.

2. **Dependency compatibility issues**

   Some Python packages don't work in Cloudflare Workers. The application has been modified to provide fallbacks for these dependencies.

3. **Environment variable issues**

   Make sure all required environment variables are set using `wrangler secret put`.

### Logs and Debugging

To view logs from your deployed application:

```bash
wrangler tail
```

## Local Development with Cloudflare Compatibility

To test Cloudflare compatibility locally:

1. Set the `CLOUDFLARE_DEPLOYMENT` environment variable to `true` in your `.env` file
2. Run the application as usual

This will enable the Cloudflare compatibility mode, which uses the same fallbacks as the deployed application.
