// ============================================================================
// Copied VERBATIM from the private FENRIR development repository
// (common/component_state.h) on 2026-07-17. The one health vocabulary: every
// actuator node, firmware module, ROS node, API message, and UI status pill
// speaks exactly these seven states.
// ============================================================================
// FENRIR component state machine — C/C++ mirror of component_state.py.
// THE one health vocabulary (CLAUDE.md Rule 4). Keep in lockstep with the
// Python mirror: same names, same values, same version. Changing this enum
// is a message-contract change (Rule 3): append-only, version bump, decision doc.
#ifndef FENRIR_COMPONENT_STATE_H
#define FENRIR_COMPONENT_STATE_H

#include <stdint.h>

#define COMPONENT_STATE_VERSION 1

typedef enum : uint8_t {
  COMPONENT_OFFLINE = 0,      // not present / no communication
  COMPONENT_DISCOVERED = 1,   // announced on bus, not yet configured
  COMPONENT_CALIBRATING = 2,  // zeroing, self-test, configuration in progress
  COMPONENT_READY = 3,        // configured and idle, safe to activate
  COMPONENT_ACTIVE = 4,       // participating in control / running
  COMPONENT_DEGRADED = 5,     // alive but impaired (missed heartbeats, derate)
  COMPONENT_FAULT = 6,        // failed; requires intervention or recovery
} ComponentState;

#endif  // FENRIR_COMPONENT_STATE_H
