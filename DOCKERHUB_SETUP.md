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

#### Step-by-Step Navigation

1. **Go to your GitHub repository**
   - Navigate to: `https://github.com/st9240202/LGWebOS-remote-api`
   - Or go to your repository's main page

2. **Open Settings**
   - Look at the **top navigation bar** (tabs: Code, Issues, Pull requests, Actions, Projects, Wiki, Security, **Settings**)
   - Click on the **Settings** tab
   - ⚠️ **If you don't see Settings tab**: You may not have admin access. Only repository owners and collaborators with admin permissions can access Settings.

3. **Find Secrets and variables**
   - In the **left sidebar**, scroll down to find the **Security** section
   - Under Security, you'll see:
     - Secrets and variables
     - Code security and analysis
     - Deploy keys
     - etc.
   - Click on **Secrets and variables** to expand it
   - Click on **Actions** (this is where repository secrets are stored)

4. **Add Secrets**
   - Click **New repository secret** button
   - Add the following secrets one by one:

   | Secret Name | Value | Description |
   |------------|-------|-------------|
   | `DOCKERHUB_USERNAME` | Your Docker Hub username | Your Docker Hub account username |
   | `DOCKERHUB_TOKEN` | Your access token | The token you created in step 1 |

   - For each secret:
     - Enter the **Name** (exactly as shown above)
     - Enter the **Secret** value
     - Click **Add secret**

#### Direct URL (Alternative Method)

You can also access secrets directly via URL:
```
https://github.com/st9240202/LGWebOS-remote-api/settings/secrets/actions
```

#### Troubleshooting: Can't Find Settings

**If Settings tab is not visible:**
- Check if you're logged into GitHub
- Verify you have **admin** or **write** permissions on the repository
- If you're a collaborator without admin access, ask the repository owner to add the secrets for you
- Repository owners can grant admin access in: Settings → Collaborators → Manage access

**If "Secrets and variables" is not visible:**
- Make sure you clicked on the **Settings** tab (not Security tab)
- The Security tab shows security overview, but Settings tab has the configuration options
- Scroll down in the left sidebar - it's under the Security section

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

### Can't Find Settings Tab
- **Check permissions**: Only repository owners and collaborators with admin access can see Settings
- **Verify you're logged in**: Make sure you're logged into your GitHub account
- **Check repository URL**: Ensure you're on the correct repository page
- **Ask repository owner**: If you don't have admin access, ask the owner to add secrets or grant you admin permissions

### Can't Find "Secrets and variables"
- **You're on the wrong tab**: Make sure you clicked **Settings** (not Security tab)
- **Security tab vs Settings tab**: 
  - Security tab = Security overview (read-only)
  - Settings tab = Configuration options (includes Secrets)
- **Scroll down**: In Settings, scroll down the left sidebar to find "Secrets and variables" under Security section
- **Direct URL**: Try accessing directly: `https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions`

### Authentication Failed
- Verify `DOCKERHUB_USERNAME` matches your Docker Hub username exactly
- Check that `DOCKERHUB_TOKEN` is correct and hasn't expired
- Ensure the token has **Read & Write** permissions
- Verify secrets are named exactly: `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` (case-sensitive)

### Image Not Found
- Wait for the workflow to complete (check Actions tab)
- Verify the image name matches your Docker Hub username
- Check Docker Hub repository visibility (public/private)
- Ensure the Docker Hub repository exists (it will be created automatically on first push)

### Build Fails
- Check the Actions logs for specific errors
- Verify Dockerfile syntax is correct
- Ensure all required files are in the repository
- Check if secrets are properly set (workflow will fail if secrets are missing)
