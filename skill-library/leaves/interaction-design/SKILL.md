---
name: interaction-design
description: Design task flows, navigation, forms, onboarding and recovery states for an app. 用户流程、信息架构、操作太绕、表单难用、返回与撤销。Use before visual polish or when usability is the problem.
---
# Interaction design
Begin with the user's concrete job, entry point, device and existing behavior. Preserve established working flows unless their change is requested or necessary.
- Sketch the shortest understandable path to completion. Use the user's vocabulary for navigation and actions; distinguish primary, secondary and destructive actions.
- Account for entry/exit/back, progress, cancellation, retry and preserved input. Treat first use, repeated use, permission-denied and interrupted sessions where relevant.
- Define loading, empty, invalid input, partial failure, success and disabled states. An error should say what happened and what the user can do next; do not discard completed work.
- Reduce repeated input and unnecessary decisions. Provide defaults with evidence, visible labels and sensible keyboard/focus/touch behavior. Hover alone must not hide essential actions.
- Test a low-fidelity flow or actual implementation using a realistic task and representative content. Record dead ends, unclear labels and recovery failures; model review is not evidence of real user testing.
Deliver a compact flow plus a state/action table or clickable prototype as the request warrants. For new visual direction use frontend-design after the flow is clear. For micro-polish use Impeccable; do not load both as competing leads.
Match the platform's native navigation and accessibility conventions. Figma is an output route only when requested; a small flow does not require a Figma file.
