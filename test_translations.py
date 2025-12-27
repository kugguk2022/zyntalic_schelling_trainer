#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quick test of Zyntalic translations with new embeddings."""

from zyntalic.translator import translate_text

test_sentences = [
    "I love you",
    "The ancient philosopher wrote profound thoughts",
    "Beautiful morning brings hope",
    "Time flows like water",
    "Knowledge is power"
]

print("=" * 80)
print("🌟 Testing Zyntalic Translations (Low Mirror Rate)")
print("=" * 80)

for text in test_sentences:
    # Use low mirror_rate to force plain_sentence_anchored
    result = translate_text(text, mirror_rate=0.0, engine='core')[0]
    target = result["target"]
    
    # Extract just the Zyntalic text (before the context block)
    if "⟦ctx:" in target:
        zyntalic_only = target.split("⟦ctx:")[0].strip()
    else:
        zyntalic_only = target
    
    print(f"\n📝 English:  {text}")
    print(f"🌀 Zyntalic: {zyntalic_only}")
    
    # Show if it contains Hangul and Polish
    has_hangul = any('\uac00' <= c <= '\ud7af' for c in zyntalic_only)
    has_polish = any(c in 'ąćęłńóśźżĄĆĘŁŃÓŚŹŻ' for c in zyntalic_only)
    print(f"   ✓ Contains Hangul: {has_hangul}, Polish chars: {has_polish}")

print("\n" + "=" * 80)
print("✅ Translation test complete!")
print("=" * 80)
