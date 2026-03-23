# Setup GitHub Repo & SSH Key for Backups

To enable automated weekly and daily backups to a secure off-PC location (GitHub private repo), please complete the following:

## 1. Create GitHub Private Repository:
* Go to GitHub.com.
* Create a new private repository named `openclaw-backups`.
* (Optional) Add a README.md explaining the purpose.

## 2. Generate SSH Key:
* Open your terminal on the Mac Mini.
* Run `ssh-keygen -t ed25519 -C "your_email@example.com"` (replace with your email).
* Press Enter to accept default file location (`~/.ssh/id_ed25519`).
* Enter a strong passphrase (optional but recommended).

## 3. Add SSH Key to GitHub:
* Copy your public key: `cat ~/.ssh/id_ed25519.pub`
* Go to your GitHub account settings → SSH and GPG keys → New SSH key.
* Paste the copied public key, give it a title (e.g., "Mac Mini OpenClaw Backup Key").

## 4. Test SSH Connection:
* Run `ssh -T git@github.com`
* You should see a message like "Hi YourUsername! You've successfully authenticated, but GitHub does not provide shell access."

**Once these steps are complete, please let me know. I'll then proceed with writing the backup scripts and setting up the cron jobs.**