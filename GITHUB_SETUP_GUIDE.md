# GitHub Setup Guide

This guide will walk you through uploading the Network Diagnostics Tool to your GitHub account (@techbutton).

## Prerequisites

- Git installed on your computer
- GitHub account (@techbutton)
- Command line / terminal access

## Step-by-Step Instructions

### 1. Create a New Repository on GitHub

1. Go to https://github.com/new
2. Repository name: `network-diagnostics-tool`
3. Description: `Web-based network diagnostic tool with NSLookup, Ping, Dig, TraceRoute, and port testing`
4. Choose: **Public** (for open source)
5. Do **NOT** initialize with README, .gitignore, or license (we already have these)
6. Click **"Create repository"**

### 2. Prepare Your Local Repository

Open a terminal and navigate to the `network-diagnostics-tool` directory:

```bash
cd /path/to/network-diagnostics-tool
```

### 3. Initialize Git Repository

```bash
# Initialize Git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Network Diagnostics Tool v1.0.0

- Web interface with dual themes (Retro/Modern)
- NSLookup, Ping, Dig, TraceRoute, Port Testing
- Bulk CSV processing
- REST API with full documentation
- Configurable DNS servers
- Production-ready with Waitress WSGI server"
```

### 4. Connect to GitHub

Replace `techbutton` with your actual GitHub username if different:

```bash
# Add GitHub remote
git remote add origin https://github.com/techbutton/network-diagnostics-tool.git

# Verify remote
git remote -v
```

### 5. Push to GitHub

```bash
# Push to GitHub
git push -u origin main
```

If you get a branch name error, try:
```bash
git branch -M main
git push -u origin main
```

### 6. Verify Upload

Visit https://github.com/techbutton/network-diagnostics-tool to see your repository!

## Optional: GitHub Configuration

### Add Topics/Tags

On your GitHub repository page:
1. Click "⚙️ Settings" or the gear icon next to "About"
2. Add topics: `network`, `diagnostics`, `dns`, `nslookup`, `ping`, `flask`, `python`, `network-tools`
3. Save changes

### Set Up GitHub Pages (Optional)

If you want to host documentation:
1. Go to Settings → Pages
2. Source: Deploy from a branch
3. Branch: main, folder: /docs (if you create a docs folder)

### Add a Repository Banner

Create or add a banner image showing the tool's interface:
1. Add image to repository as `assets/banner.png`
2. Reference in README.md: `![Banner](assets/banner.png)`

### Create a Release

Once uploaded:
1. Go to "Releases" → "Create a new release"
2. Tag: `v1.0.0`
3. Title: `Network Diagnostics Tool v1.0.0`
4. Description: Copy from CHANGELOG.md
5. Publish release

## Git Configuration Tips

### Set Your Identity

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Create a .gitattributes File (Optional)

Add to your repository:

```bash
cat > .gitattributes << 'EOF'
# Auto-detect text files
* text=auto

# Python files
*.py text
*.pyw text

# Shell scripts
*.sh text eol=lf
*.ps1 text eol=crlf

# Web files
*.html text
*.css text
*.js text

# Documentation
*.md text
*.txt text

# Binary files
*.png binary
*.jpg binary
*.gif binary
*.ico binary
EOF

git add .gitattributes
git commit -m "Add .gitattributes for consistent line endings"
git push
```

## Common Issues and Solutions

### Authentication Failed

If you get authentication errors:

**Option 1: Use Personal Access Token (Recommended)**
1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `repo` scope
3. Use token as password when prompted

**Option 2: Use SSH**
```bash
# Generate SSH key (if you don't have one)
ssh-keygen -t ed25519 -C "your.email@example.com"

# Add to GitHub: Settings → SSH and GPG keys → New SSH key
cat ~/.ssh/id_ed25519.pub

# Change remote to SSH
git remote set-url origin git@github.com:techbutton/network-diagnostics-tool.git
```

### Large Files Warning

If you get warnings about large files:
```bash
# Create/update .gitignore
echo "logs/" >> .gitignore
echo "bulk_results/" >> .gitignore
echo "*.log" >> .gitignore

git rm --cached -r logs/ bulk_results/
git commit -m "Remove large files from tracking"
```

### Branch Name Issues

GitHub now uses `main` as default, but Git might use `master`:
```bash
# Rename local branch to main
git branch -M main

# Push to main
git push -u origin main
```

## Post-Upload Checklist

After uploading to GitHub:

- [ ] Repository is public
- [ ] README.md displays correctly
- [ ] LICENSE file is present
- [ ] All files uploaded successfully
- [ ] Topics/tags added
- [ ] Release created (v1.0.0)
- [ ] Repository description added
- [ ] Star your own repository ⭐

## Ongoing Maintenance

### Making Changes

```bash
# Make changes to files
# Then:

git add .
git commit -m "Description of changes"
git push
```

### Creating New Releases

When you have new versions:

```bash
# Update version in files
# Update CHANGELOG.md
# Commit changes

git add .
git commit -m "Version 1.1.0"
git tag -a v1.1.0 -m "Version 1.1.0"
git push origin main --tags
```

Then create a release on GitHub using the tag.

## Additional Resources

- [GitHub Documentation](https://docs.github.com/)
- [Git Documentation](https://git-scm.com/doc)
- [Markdown Guide](https://www.markdownguide.org/)
- [Open Source Guide](https://opensource.guide/)

## Sample README Badge Code

Add these to your README.md:

```markdown
![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/github/license/techbutton/network-diagnostics-tool)
![Stars](https://img.shields.io/github/stars/techbutton/network-diagnostics-tool)
![Issues](https://img.shields.io/github/issues/techbutton/network-diagnostics-tool)
![Forks](https://img.shields.io/github/forks/techbutton/network-diagnostics-tool)
```

## Questions?

If you encounter any issues:
1. Check GitHub's [troubleshooting guide](https://docs.github.com/en/get-started/using-git/troubleshooting-the-changing-a-remotes-url-error)
2. Search GitHub's [community forum](https://github.community/)
3. Review Git's [documentation](https://git-scm.com/doc)

---

Good luck with your open-source project! 🚀
