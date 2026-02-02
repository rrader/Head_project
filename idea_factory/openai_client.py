"""OpenAI client for generating and improving ideas."""

import json
import os
from typing import Dict, List

from openai import OpenAI


class IdeaGenerator:
    """Client for generating ideas using OpenAI."""
    
    def __init__(self):
        """Initialize the OpenAI client."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv('OPENAI_MODEL', 'gpt-5-mini')
    
    def generate_ideas(self, prompt: str) -> List[Dict[str, any]]:
        """
        Generate ideas based on the user's prompt.
        
        Args:
            prompt: User's brainstorming prompt
        
        Returns:
            List of idea dictionaries with 'title', 'description', 'feasible_in_2_days'
        """
        system_prompt = """Ти - асистент для генерації ідей для шкільного STEAM-хакатону.
Повертай ТІЛЬКИ валідний JSON у форматі:
{
  "ideas": [
    {"title": "назва ідеї", "description": "опис 1-2 речення", "feasible_in_2_days": true},
    ...
  ]
}

Генеруй 6-8 ідей. Кожна ідея має бути реалістичною для виконання за 1-2 дні в школі.
Пиши українською."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            result = json.loads(content)
            
            # Validate structure
            if 'ideas' not in result or not isinstance(result['ideas'], list):
                raise ValueError("Invalid response structure")
            
            return result['ideas']
        
        except json.JSONDecodeError:
            # Retry with explicit instruction
            return self._retry_with_json_instruction(prompt)
        except Exception as e:
            print(f"Error generating ideas: {e}")
            raise
    
    def improve_idea(self, idea: Dict[str, str], instruction: str) -> Dict[str, str]:
        """
        Improve an idea based on user instruction.
        
        Args:
            idea: Dictionary with 'title' and 'description'
            instruction: User's improvement instruction
        
        Returns:
            Dictionary with 'title', 'description', 'changes_summary'
        """
        system_prompt = """Ти - асистент для покращення ідей для шкільного STEAM-хакатону.
Повертай ТІЛЬКИ валідний JSON у форматі:
{
  "title": "покращена назва",
  "description": "покращений опис",
  "changes_summary": "що змінилось"
}

Пиши українською."""

        user_prompt = f"""Ідея:
Назва: {idea.get('title', '')}
Опис: {idea.get('description', '')}

Інструкція для покращення: {instruction}

Покращ цю ідею згідно з інструкцією."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            result = json.loads(content)
            
            # Validate structure
            required_keys = ['title', 'description']
            if not all(key in result for key in required_keys):
                raise ValueError("Invalid response structure")
            
            return result
        
        except json.JSONDecodeError:
            # Retry with explicit instruction
            return self._retry_improve_with_json_instruction(idea, instruction)
        except Exception as e:
            print(f"Error improving idea: {e}")
            raise
    
    def _retry_with_json_instruction(self, prompt: str) -> List[Dict[str, any]]:
        """Retry idea generation with explicit JSON instruction."""
        retry_prompt = f"{prompt}\n\nВАЖЛИВО: Поверни ТІЛЬКИ валідний JSON, без додаткового тексту."
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Return valid JSON only."},
                {"role": "user", "content": retry_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        result = json.loads(content)
        return result.get('ideas', [])
    
    def _retry_improve_with_json_instruction(self, idea: Dict[str, str], instruction: str) -> Dict[str, str]:
        """Retry idea improvement with explicit JSON instruction."""
        retry_prompt = f"""Idea: {idea.get('title')} - {idea.get('description')}
Instruction: {instruction}

Return ONLY valid JSON with title, description, and changes_summary."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Return valid JSON only."},
                {"role": "user", "content": retry_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
