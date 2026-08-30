"""Auditoria estruturada de eventos relevantes."""

import json
import logging

logger = logging.getLogger("document_intelligence.audit")


def audit(event: str, **fields) -> None:
    logger.info(json.dumps({"event": event, **fields}, ensure_ascii=False))
