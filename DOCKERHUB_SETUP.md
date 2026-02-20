# Docker Hub Setup Guide

This guide explains how to configure GitHub Actions to push Docker images to Docker Hub.

## Prerequisites

- A Docker Hub account ([sign up](https://hub.docker.com/signup) if you don't have one)
- Access to your GitHub repository settings

## Setup Steps

### 1. Create Docker Hub Access Token

1. Log in to [Docker Hub](https://hub.docker.com/)
2. Go to **Account Settings** → **Security**
3. Click **New Access Token**
4. Give it a name (e.g., "github-actions")
5. Set permissions to **Read & Write** (or **Read, Write & Delete**)
6. Click **Generate**
7. **Copy the token** - you won't be able to see it again!

### 2. Add Secrets to GitHub Repository

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secrets:

   | Secret Name | Value | Description |
   |------------|-------|-------------|
   | `DOCKERHUB_USERNAME` | Your Docker Hub username | Your Docker Hub account username |
   | `DOCKERHUB_TOKEN` | Your access token | The token you created in step 1 |

### 3. Update Workflow (if needed)

The workflow uses the image name: `YOUR_DOCKERHUB_USERNAME/lgwebos-remote-api`

If you want to change the image name, edit `.github/workflows/docker-build-dockerhub.yml`:

```yaml
images: ${{ env.DOCKERHUB_USERNAME }}/your-custom-name
```

## How It Works

- **On push to `init` or `main`**: Builds and pushes images with branch tags and `latest`
- **On tag (e.g., `v1.0.0`)**: Builds and pushes with semantic version tags
- **On pull request**: Builds only (doesn't push)

## Image Tags

Images will be tagged as:
- `latest` - Latest build from `main` or `init` branch
- `init` - Builds from `init` branch
- `main` - Builds from `main` branch
- `v1.0.0` - Semantic version tags
- `init-<sha>` - Branch name + commit SHA

## Pulling Images

After the workflow runs, you can pull images:

```bash
# Latest
docker pull YOUR_DOCKERHUB_USERNAME/lgwebos-remote-api:latest

# Specific branch
docker pull YOUR_DOCKERHUB_USERNAME/lgwebos-remote-api:init

# Specific version
docker pull YOUR_DOCKERHUB_USERNAME/lgwebos-remote-api:v1.0.0
```

## Troubleshooting

### Authentication Failed
- Verify `DOCKERHUB_USERNAME` matches your Docker Hub username exactly
- Check that `DOCKERHUB_TOKEN` is correct and hasn't expired
- Ensure the token has **Read & Write** permissions

### Image Not Found
- Wait for the workflow to complete (check Actions tab)
- Verify the image name matches your Docker Hub username
- Check Docker Hub repository visibility (public/private)

### Build Fails
- Check the Actions logs for specific errors
- Verify Dockerfile syntax is correct
- Ensure all required files are in the repository
