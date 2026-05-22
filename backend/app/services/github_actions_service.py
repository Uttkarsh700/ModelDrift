"""
GitHub Actions workflow trigger integration for ModelDrift.

Provides service to trigger retraining via GitHub Actions workflow_dispatch API.
"""

import os
import requests
from typing import Optional, dict, list


class GitHubActionsService:
    """Service for interacting with GitHub Actions."""

    GITHUB_API_URL = "https://api.github.com"

    @staticmethod
    def is_configured() -> tuple[bool, list[str]]:
        """
        Check if GitHub Actions environment variables are configured.

        Returns:
            (is_configured: bool, missing_vars: list[str])
        """
        required_vars = ["GITHUB_TOKEN", "GITHUB_OWNER", "GITHUB_REPO"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]

        return len(missing_vars) == 0, missing_vars

    @staticmethod
    def trigger_retraining(
        model_name: str = "credit_risk",
        model_version: str = "v1",
        trigger_reason: str = "manual",
    ) -> dict:
        """
        Trigger retraining via GitHub Actions workflow_dispatch.

        Args:
            model_name: Model name (e.g., "credit_risk")
            model_version: Model version (e.g., "v1")
            trigger_reason: Reason for trigger (e.g., "high drift detected")

        Returns:
            {
                "status": "triggered" | "error",
                "workflow_file": str,
                "ref": str,
                "message": str
            }
        """
        # Check if configured
        is_configured, missing_vars = GitHubActionsService.is_configured()
        if not is_configured:
            return {
                "status": "error",
                "message": f"GitHub Actions not configured. Missing environment variables: {', '.join(missing_vars)}",
                "workflow_file": None,
                "ref": None,
            }

        # Get config from environment
        github_token = os.getenv("GITHUB_TOKEN")
        github_owner = os.getenv("GITHUB_OWNER")
        github_repo = os.getenv("GITHUB_REPO")
        workflow_file = os.getenv("GITHUB_WORKFLOW_FILE", "retrain-model.yml")
        ref = os.getenv("GITHUB_REF", "main")

        # Prepare request
        url = f"{GitHubActionsService.GITHUB_API_URL}/repos/{github_owner}/{github_repo}/actions/workflows/{workflow_file}/dispatches"

        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "ModelDrift",
        }

        payload = {
            "ref": ref,
            "inputs": {
                "model_name": model_name,
                "model_version": model_version,
                "trigger_reason": trigger_reason,
            },
        }

        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=10,
            )

            # GitHub returns 204 No Content on success
            if response.status_code == 204:
                return {
                    "status": "triggered",
                    "workflow_file": workflow_file,
                    "ref": ref,
                    "message": f"Retraining workflow triggered on {ref}",
                }

            # Handle errors
            error_detail = response.text
            try:
                error_detail = response.json().get("message", response.text)
            except Exception:
                pass

            return {
                "status": "error",
                "message": f"GitHub API error ({response.status_code}): {error_detail}",
                "workflow_file": workflow_file,
                "ref": None,
            }

        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "message": "GitHub API request timed out",
                "workflow_file": workflow_file,
                "ref": None,
            }

        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"Error calling GitHub API: {str(e)}",
                "workflow_file": workflow_file,
                "ref": None,
            }
