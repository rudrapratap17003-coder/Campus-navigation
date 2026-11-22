"""
tests/test_phase21_deployment.py
--------------------------------
Comprehensive automated test suite for Phase 21: Deployment & Release Engineering.
Validates:
1. Dockerfile instructions (multi-stage/slim base, non-root user, port 8501, healthcheck, CMD).
2. docker-compose.yml configuration (services, volumes, networks, environment, healthcheck).
3. .dockerignore file exclusions (.env, *.db, backups/, logs/, .git, .venv).
4. nginx/nginx.conf reverse proxy rules (WebSocket proxy headers, client_max_body_size, security headers).
5. Deployment automation scripts (deploy.sh and deploy.ps1 syntax and safety checks).
"""

import os
import re
import unittest


class TestPhase21DeploymentEngineering(unittest.TestCase):
    """Test suite validating production containerization, proxying, and deployment configs."""

    @classmethod
    def setUpClass(cls):
        cls.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        cls.dockerfile_path = os.path.join(cls.root_dir, "Dockerfile")
        cls.compose_path = os.path.join(cls.root_dir, "docker-compose.yml")
        cls.dockerignore_path = os.path.join(cls.root_dir, ".dockerignore")
        cls.nginx_path = os.path.join(cls.root_dir, "nginx", "nginx.conf")
        cls.deploy_sh_path = os.path.join(cls.root_dir, "scripts", "deploy.sh")
        cls.deploy_ps1_path = os.path.join(cls.root_dir, "scripts", "deploy.ps1")

    def test_dockerfile_structure_and_security(self):
        """Verify Dockerfile uses Python 3.11-slim, defines non-root user, and configures healthcheck."""
        self.assertTrue(os.path.isfile(self.dockerfile_path), "Dockerfile must exist at project root")

        with open(self.dockerfile_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Base image
        self.assertIn("FROM python:3.11-slim", content, "Dockerfile should use python:3.11-slim base image")

        # Non-root security user
        self.assertIn("useradd", content, "Dockerfile must create a dedicated system user")
        self.assertIn("appuser", content, "Dedicated user should be appuser")
        self.assertIn("USER appuser", content, "Dockerfile must switch execution to non-root USER")

        # Directory preparation & permissions
        self.assertIn("mkdir -p /app/data /app/database /app/backups /app/logs", content,
                      "Dockerfile must create persistent and log directories")
        self.assertIn("chown -R appuser:appgroup /app", content,
                      "App directories must be owned by the non-root appuser")

        # Port & Healthcheck & CMD
        self.assertIn("EXPOSE 8501", content, "Streamlit port 8501 must be exposed")
        self.assertIn("HEALTHCHECK", content, "Dockerfile must define a container HEALTHCHECK instruction")
        self.assertIn("_stcore/health", content, "Healthcheck must probe Streamlit's health endpoint")
        self.assertIn("main.py", content, "CMD must launch main.py")

    def test_docker_compose_configuration(self):
        """Verify docker-compose.yml contains required service, persistent volume mounts, and network."""
        self.assertTrue(os.path.isfile(self.compose_path), "docker-compose.yml must exist at project root")

        with open(self.compose_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("services:", content, "docker-compose.yml must define services")
        self.assertIn("campus-navigator:", content, "campus-navigator service must be defined")
        self.assertIn("restart: unless-stopped", content, "Restart policy must be unless-stopped")

        # Ports
        self.assertIn('"8501:8501"', content, "Port 8501 must be mapped")

        # Volume mounts
        self.assertIn("./data:/app/data", content, "./data volume mount must be present")
        self.assertIn("./database:/app/database", content, "./database volume mount must be present")
        self.assertIn("./backups:/app/backups", content, "./backups volume mount must be present")
        self.assertIn("./logs:/app/logs", content, "./logs volume mount must be present")

        # Environment variables
        self.assertIn("CAMPUS_ENV=production", content)
        self.assertIn("CAMPUS_PORT=8501", content)
        self.assertIn("CAMPUS_DB_JOURNAL_MODE=WAL", content)

    def test_dockerignore_coverage(self):
        """Verify .dockerignore excludes sensitive files, databases, virtualenvs, and backups."""
        self.assertTrue(os.path.isfile(self.dockerignore_path), ".dockerignore must exist at project root")

        with open(self.dockerignore_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]

        self.assertIn(".git", lines, ".git must be ignored")
        self.assertIn(".env", lines, ".env must be ignored to prevent secret leakage")
        self.assertTrue(any(p in lines for p in ["*.db", "*.sqlite", "*.sqlite3"]),
                        "Database binary files must be ignored")
        self.assertIn("backups/", lines, "Backups directory must be ignored")
        self.assertIn("logs/", lines, "Logs directory must be ignored")
        self.assertTrue(any(p in lines for p in [".venv", "venv"]), "Virtualenv must be ignored")

    def test_nginx_reverse_proxy_configuration(self):
        """Verify nginx.conf includes WebSocket proxy rules, security headers, and body size limits."""
        self.assertTrue(os.path.isfile(self.nginx_path), "nginx/nginx.conf must exist")

        with open(self.nginx_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Upstream and proxy pass
        self.assertIn("upstream streamlit_backend", content, "Upstream backend definition must exist")
        self.assertIn("campus-navigator:8501", content, "Upstream backend must target port 8501")

        # Streamlit WebSocket configuration
        self.assertIn("proxy_set_header Upgrade $http_upgrade;", content, "WebSocket upgrade header required")
        self.assertIn('proxy_set_header Connection "upgrade";', content, "WebSocket connection header required")
        self.assertIn("proxy_http_version 1.1;", content, "HTTP 1.1 required for WebSockets")

        # Security headers
        self.assertIn("X-Frame-Options", content, "X-Frame-Options header must be set")
        self.assertIn("X-Content-Type-Options", content, "X-Content-Type-Options header must be set")
        self.assertIn("client_max_body_size 25M;", content, "Body size limit must match Streamlit 25M")

    def test_deployment_scripts_integrity(self):
        """Verify automated deployment scripts exist, are non-empty, and perform backups & health checks."""
        self.assertTrue(os.path.isfile(self.deploy_sh_path), "scripts/deploy.sh must exist")
        self.assertTrue(os.path.isfile(self.deploy_ps1_path), "scripts/deploy.ps1 must exist")

        with open(self.deploy_sh_path, "r", encoding="utf-8") as f:
            sh_content = f.read()

        self.assertIn("docker compose", sh_content, "deploy.sh must invoke docker compose")
        self.assertIn("campus_backup_", sh_content, "deploy.sh must trigger database backup")
        self.assertIn("_stcore/health", sh_content, "deploy.sh must verify application health")

        with open(self.deploy_ps1_path, "r", encoding="utf-8") as f:
            ps1_content = f.read()

        self.assertIn("docker compose", ps1_content, "deploy.ps1 must invoke docker compose")
        self.assertIn("campus_backup_", ps1_content, "deploy.ps1 must trigger database backup")
        self.assertIn("_stcore/health", ps1_content, "deploy.ps1 must verify application health")


if __name__ == "__main__":
    unittest.main()
