"""Brains: response generation strategies.

Each 'brain' is a strategy that takes an ExecutionContext and produces
a response string. Different response modes may use different brains.

Future implementations:
  - ReflectBrain: empathetic, exploratory responses
  - CrisisBrain: deterministic safety-first responses
  - PlanBrain: structured goal-oriented responses
"""
