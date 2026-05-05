"""Tests for MemoryService — extraction, deduplication, and retrieval scoring.

Run from backend/ with:
    .\\venv-win\\Scripts\\Activate.ps1
    python -m pytest tests/test_memory.py -v
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone, timedelta

from src.services.memory import MemoryService, MemoryFact, _keywords


# ── Keyword extraction ────────────────────────────────────────────────────────

class TestKeywords:
    def test_removes_stop_words(self):
        result = _keywords("I am really stressed about my job")
        assert "stressed" in result
        assert "job" in result
        assert "i" not in result
        assert "am" not in result
        assert "really" not in result
        assert "my" not in result

    def test_short_words_excluded(self):
        result = _keywords("go to the gym")
        assert "gym" in result
        assert "go" not in result  # len 2

    def test_deduplicates(self):
        result = _keywords("work work work")
        assert result.count("work") == 1


# ── Extraction: stressors ─────────────────────────────────────────────────────

class TestExtractStressors:
    svc = MemoryService()

    def test_stressed_about(self):
        facts = self.svc.extract_from_message("I've been so stressed about work lately")
        stressors = [f for f in facts if f.category == "stressor"]
        assert len(stressors) >= 1
        assert "work" in stressors[0].content

    def test_overwhelmed_by(self):
        facts = self.svc.extract_from_message("I'm overwhelmed by everything at home")
        stressors = [f for f in facts if f.category == "stressor"]
        assert len(stressors) >= 1

    def test_struggling_with(self):
        facts = self.svc.extract_from_message("I've been struggling with my anxiety for months")
        stressors = [f for f in facts if f.category == "stressor"]
        assert len(stressors) >= 1
        assert "anxiety" in stressors[0].content

    def test_my_job_is_stressful(self):
        facts = self.svc.extract_from_message("My job has been really stressful lately")
        stressors = [f for f in facts if f.category == "stressor"]
        assert len(stressors) >= 1
        assert "job" in stressors[0].content

    def test_no_false_positive_positive_message(self):
        facts = self.svc.extract_from_message("I had a great day today, feeling good!")
        stressors = [f for f in facts if f.category == "stressor"]
        assert len(stressors) == 0


# ── Extraction: coping strategies ────────────────────────────────────────────

class TestExtractCoping:
    svc = MemoryService()

    def test_gerund_helps_me(self):
        facts = self.svc.extract_from_message("Going for walks really helps me a lot")
        coping = [f for f in facts if f.category == "coping"]
        assert len(coping) >= 1
        assert "walking" in coping[0].content or "going" in coping[0].content

    def test_find_calming(self):
        facts = self.svc.extract_from_message("I find journaling really calming when I'm upset")
        coping = [f for f in facts if f.category == "coping"]
        assert len(coping) >= 1
        assert "journaling" in coping[0].content

    def test_when_i_feel_better(self):
        facts = self.svc.extract_from_message("when I meditate, I feel calmer")
        coping = [f for f in facts if f.category == "coping"]
        assert len(coping) >= 1


# ── Extraction: preferences ───────────────────────────────────────────────────

class TestExtractPreferences:
    svc = MemoryService()

    def test_prefer_you_to(self):
        facts = self.svc.extract_from_message("I prefer you to just listen rather than give advice")
        prefs = [f for f in facts if f.category == "preference"]
        assert len(prefs) >= 1
        assert "listen" in prefs[0].content

    def test_please_dont(self):
        facts = self.svc.extract_from_message("Please don't tell me what to do right now")
        prefs = [f for f in facts if f.category == "preference"]
        assert len(prefs) >= 1

    def test_dont_want_you_to(self):
        facts = self.svc.extract_from_message("I don't want you to give me advice today")
        prefs = [f for f in facts if f.category == "preference"]
        assert len(prefs) >= 1


# ── Extraction: goals ─────────────────────────────────────────────────────────

class TestExtractGoals:
    svc = MemoryService()

    def test_trying_to(self):
        facts = self.svc.extract_from_message("I'm trying to sleep better and reduce my stress")
        goals = [f for f in facts if f.category == "goal"]
        assert len(goals) >= 1
        assert "sleep" in goals[0].content

    def test_my_goal_is(self):
        facts = self.svc.extract_from_message("My goal is to exercise more consistently")
        goals = [f for f in facts if f.category == "goal"]
        assert len(goals) >= 1

    def test_really_want_to(self):
        facts = self.svc.extract_from_message("I really want to get better at managing my time")
        goals = [f for f in facts if f.category == "goal"]
        assert len(goals) >= 1


# ── Extraction: support needs ─────────────────────────────────────────────────

class TestExtractSupportNeeds:
    svc = MemoryService()

    def test_need_to_vent(self):
        facts = self.svc.extract_from_message("I just need to vent, I don't want advice")
        needs = [f for f in facts if f.category == "support_need"]
        assert len(needs) >= 1
        assert "vent" in needs[0].content

    def test_not_looking_for_advice(self):
        facts = self.svc.extract_from_message("I'm not looking for advice, just support")
        needs = [f for f in facts if f.category == "support_need"]
        assert len(needs) >= 1

    def test_need_someone_to_listen(self):
        facts = self.svc.extract_from_message("I just need someone to listen right now")
        needs = [f for f in facts if f.category == "support_need"]
        assert len(needs) >= 1


# ── Extraction: personal context ──────────────────────────────────────────────

class TestExtractPersonalContext:
    svc = MemoryService()

    def test_occupation_im_a(self):
        facts = self.svc.extract_from_message("I'm a nurse and work night shifts")
        ctx = [f for f in facts if f.category == "personal_context"]
        assert len(ctx) >= 1
        assert "nurse" in ctx[0].content

    def test_occupation_work_as(self):
        facts = self.svc.extract_from_message("I work as a teacher at a primary school")
        ctx = [f for f in facts if f.category == "personal_context"]
        assert len(ctx) >= 1
        assert "teacher" in ctx[0].content

    def test_has_kids(self):
        facts = self.svc.extract_from_message("I have two kids and it's been exhausting")
        ctx = [f for f in facts if f.category == "personal_context"]
        assert len(ctx) >= 1
        assert "two" in ctx[0].content or "kids" in ctx[0].content

    def test_lives_alone(self):
        facts = self.svc.extract_from_message("I live alone and sometimes it gets really quiet")
        ctx = [f for f in facts if f.category == "personal_context"]
        assert len(ctx) >= 1
        assert "alone" in ctx[0].content


# ── Extraction: nothing from crisis-level text ────────────────────────────────

class TestExtractionConservatism:
    svc = MemoryService()

    def test_no_memory_from_trivial_message(self):
        facts = self.svc.extract_from_message("hey how are you doing today")
        assert facts == []

    def test_no_memory_from_greeting(self):
        facts = self.svc.extract_from_message("hi")
        assert facts == []

    def test_keywords_populated(self):
        facts = self.svc.extract_from_message("I'm struggling with anxiety at work")
        assert all(len(f.keywords) > 0 for f in facts)

    def test_confidence_meets_threshold(self):
        facts = self.svc.extract_from_message("I'm a teacher and find mindfulness calming")
        assert all(f.confidence >= 0.70 for f in facts)


# ── Deduplication ─────────────────────────────────────────────────────────────

class TestDeduplication:
    svc = MemoryService()

    def _make_memory(self, category, content, keywords_list):
        m = MagicMock(spec=["category", "keywords", "times_reinforced", "last_reinforced_at"])
        m.category = category
        m.keywords = json.dumps(keywords_list)
        m.times_reinforced = 1
        m.last_reinforced_at = datetime.now(timezone.utc)
        return m

    def test_duplicate_detected(self):
        existing = self._make_memory("stressor", "stressed about work", ["stressed", "work"])
        new_fact = MemoryFact(
            category="stressor",
            content="stressed about work pressure",
            keywords=["stressed", "work", "pressure"],
            confidence=0.85,
        )
        result = self.svc._find_duplicate(new_fact, [existing])
        assert result is existing

    def test_different_category_not_duplicate(self):
        existing = self._make_memory("goal", "wants better sleep", ["better", "sleep"])
        new_fact = MemoryFact(
            category="stressor",
            content="stressed about sleep",
            keywords=["stressed", "sleep"],
            confidence=0.85,
        )
        result = self.svc._find_duplicate(new_fact, [existing])
        assert result is None

    def test_low_overlap_not_duplicate(self):
        existing = self._make_memory("stressor", "stressed about money", ["stressed", "money"])
        new_fact = MemoryFact(
            category="stressor",
            content="struggling with relationships",
            keywords=["struggling", "relationships"],
            confidence=0.80,
        )
        result = self.svc._find_duplicate(new_fact, [existing])
        assert result is None


# ── Retrieval scoring ─────────────────────────────────────────────────────────

class TestRetrievalScoring:
    svc = MemoryService()

    def _make_memory(self, category, content, keywords_list, days_old=0, reinforced=1):
        m = MagicMock()
        m.category = category
        m.content = content
        m.keywords = json.dumps(keywords_list)
        m.times_reinforced = reinforced
        m.last_reinforced_at = datetime.now(timezone.utc) - timedelta(days=days_old)
        return m

    def test_keyword_overlap_increases_score(self):
        mem_relevant = self._make_memory("stressor", "stressed about work", ["stressed", "work"])
        mem_irrelevant = self._make_memory("goal", "wants better sleep", ["sleep"])
        now = datetime.now(timezone.utc)
        query_words = {"stressed", "work", "overwhelmed"}
        score_rel = self.svc._score(mem_relevant, query_words, now)
        score_irrel = self.svc._score(mem_irrelevant, query_words, now)
        assert score_rel > score_irrel

    def test_recent_memory_scores_higher(self):
        mem_fresh = self._make_memory("stressor", "stressed about work", ["work"], days_old=0)
        mem_old = self._make_memory("stressor", "stressed about work", ["work"], days_old=25)
        now = datetime.now(timezone.utc)
        query_words = {"work"}
        score_fresh = self.svc._score(mem_fresh, query_words, now)
        score_old = self.svc._score(mem_old, query_words, now)
        assert score_fresh > score_old

    def test_reinforced_memory_scores_higher(self):
        mem_many = self._make_memory("coping", "walking helps", ["walking"], reinforced=5)
        mem_once = self._make_memory("coping", "walking helps", ["walking"], reinforced=1)
        now = datetime.now(timezone.utc)
        query_words = set()
        score_many = self.svc._score(mem_many, query_words, now)
        score_once = self.svc._score(mem_once, query_words, now)
        assert score_many > score_once


# ── Integration: extract_from_message returns useful keywords ─────────────────

class TestKeywordsOnFacts:
    svc = MemoryService()

    def test_stressor_keywords_include_subject(self):
        facts = self.svc.extract_from_message("I'm so stressed about my relationship")
        stressors = [f for f in facts if f.category == "stressor"]
        assert any("relationship" in f.keywords for f in stressors)

    def test_personal_context_keywords_include_occupation(self):
        facts = self.svc.extract_from_message("I'm a doctor and it's very demanding")
        ctx = [f for f in facts if f.category == "personal_context"]
        assert any("doctor" in f.keywords for f in ctx)
