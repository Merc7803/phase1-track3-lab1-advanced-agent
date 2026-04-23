import json
import os
from openai import OpenAI
from typing import Tuple
from .schemas import QAExample, JudgeResult, ReflectionEntry
from .prompts import ACTOR_SYSTEM, EVALUATOR_SYSTEM, REFLECTOR_SYSTEM

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

def actor_answer(example: QAExample, attempt_id: int, agent_type: str, reflection_memory: list[str]) -> Tuple[str, int]:
    context_str = "\n".join([f"[{i+1}] {c.title}: {c.text}" for i, c in enumerate(example.context)])
    prompt = f"Question: {example.question}\n\nContext:\n{context_str}\n"
    
    if reflection_memory and agent_type == "reflexion":
        prompt += "\nPrevious mistakes and strategies to avoid them:\n"
        for i, strategy in enumerate(reflection_memory):
            prompt += f"- {strategy}\n"
            
    prompt += "\nFinal Answer:"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[  
            {"role": "system", "content": ACTOR_SYSTEM},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0
    )
    
    answer = response.choices[0].message.content.strip()
    tokens = response.usage.total_tokens
    return answer, tokens

def evaluator(example: QAExample, answer: str) -> Tuple[JudgeResult, int]:
    prompt = f"Question: {example.question}\nGold Answer: {example.gold_answer}\nPredicted Answer: {answer}"
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": EVALUATOR_SYSTEM},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
        response_format={ "type": "json_object" }
    )
    
    result_str = response.choices[0].message.content.strip()
    tokens = response.usage.total_tokens
    try:
        data = json.loads(result_str)
        return JudgeResult(**data), tokens
    except Exception:
        # Fallback if json parsing fails
        return JudgeResult(score=0, reason="Failed to parse evaluator output.", missing_evidence=[], spurious_claims=[]), tokens

def reflector(example: QAExample, attempt_id: int, judge: JudgeResult, answer: str) -> Tuple[ReflectionEntry, int]:
    context_str = "\n".join([f"[{i+1}] {c.title}: {c.text}" for i, c in enumerate(example.context)])
    prompt = f"Question: {example.question}\nContext:\n{context_str}\n\nPredicted Answer: {answer}\nEvaluator Feedback: {judge.reason}"
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": REFLECTOR_SYSTEM},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
        response_format={ "type": "json_object" }
    )
    
    result_str = response.choices[0].message.content.strip()
    tokens = response.usage.total_tokens
    try:
        data = json.loads(result_str)
        return ReflectionEntry(attempt_id=attempt_id, **data), tokens
    except Exception:
        return ReflectionEntry(attempt_id=attempt_id, failure_reason="Failed to parse reflector output.", lesson="", next_strategy="Try to be more precise."), tokens
