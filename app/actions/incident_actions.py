from __future__ import annotations

from dataclasses import dataclass

from app.models.incident import Incident


@dataclass
class ActionResult:
    success: bool
    message: str


def investigate_incident(incident: Incident) -> ActionResult:
    """
    Perform a deterministic local investigation.

    In the production version, this will be replaced or augmented with
    real operational signals such as logs, metrics, traces, or service
    health checks.
    """

    incident.metadata["investigation"] = {
        "service": incident.service,
        "finding": "Service health check completed.",
    }

    return ActionResult(
        success=True,
        message=f"Investigation completed for {incident.service}.",
    )


def remediate_incident(incident: Incident) -> ActionResult:
    """
    Perform a deterministic local remediation.

    The local implementation simulates remediation while keeping the
    action boundary explicit so real operational tools can be connected
    later.
    """

    if incident.metadata.get("force_remediation_failure"):
        return ActionResult(
            success=False,
            message=f"Remediation failed for {incident.service}.",
        )

    if incident.metadata.get("fail_remediation_once"):
       incident.metadata.pop("fail_remediation_once")
       return ActionResult(
           success=False,
           message=f"Remediation temporarily failed for {incident.service}.",
    )

    return ActionResult(
        success=True,
        message=f"Remediation completed for {incident.service}.",
    )


def verify_incident(incident: Incident) -> ActionResult:
    """
    Verify that the incident has recovered.

    By default the local simulation succeeds. Tests can explicitly force
    verification failure using incident metadata.
    """

    if incident.metadata.get("force_verification_failure"):
        return ActionResult(
            success=False,
            message=f"Verification failed for {incident.service}.",
        )

    incident.metadata["verification"] = {
        "service": incident.service,
        "result": "Service recovery confirmed.",
    }

    return ActionResult(
        success=True,
        message=f"Verification completed for {incident.service}.",
    )
