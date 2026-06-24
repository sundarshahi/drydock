#!/usr/bin/env bash
# Shipyard Session Guard
# Detects if the current project was built with Shipyard and offers
# the user a choice: work with the pipeline or without it.

SUITE_DIR="Shipyard"

# Only fire if the suite directory exists in the current project
if [ ! -d "$SUITE_DIR" ]; then
  exit 0
fi

# Count artifacts for context
ADR_COUNT=$(find "$SUITE_DIR" -name "ADR-*.md" 2>/dev/null | wc -l | tr -d ' ')
RECEIPT_COUNT=$(find "$SUITE_DIR/.orchestrator/receipts" -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
PROTOCOL_COUNT=$(find "$SUITE_DIR/.protocols" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')

cat <<GUARD
# Shipyard Native Project Detected

This project was built with the Shipyard pipeline. The \`$SUITE_DIR/\` directory contains ${ADR_COUNT} architecture decisions, ${RECEIPT_COUNT} pipeline receipts, and ${PROTOCOL_COUNT} protocols.

**IMPORTANT — Before starting work, ask the user how they'd like to proceed using AskUserQuestion:**

Question: "This project was built with the Shipyard pipeline. How would you like to work today?"
Header: "Shipyard Native Project"
Options:
  1. "Use Shipyard (Recommended)" — "Route changes through specialized agents — architecture, security, and test baselines stay intact. Best for features, refactors, and anything that touches system behavior."
  2. "Work directly without the plugin" — "Make changes freely. Good for quick fixes, experiments, or when you know exactly what you're changing. You can always invoke /shipyard later if needed."
  3. "Chat about this" — "Let's discuss what I'm planning and figure out the best approach together."

If the user chooses option 1: invoke /shipyard for their request — it auto-routes to the right mode (Feature, Review, Test, Harden, Ship, Architect, Explore, Optimize).
If the user chooses option 2: proceed normally. Respect the choice fully — no further reminders this session.
If the user chooses option 3: discuss their plans, then recommend an approach.

**Context for the user if they ask why:** This project has ${ADR_COUNT} architecture decisions, ${RECEIPT_COUNT} verified pipeline receipts, and ${PROTOCOL_COUNT} shared protocols. The plugin ensures changes respect these baselines — but it's always your call.
GUARD
