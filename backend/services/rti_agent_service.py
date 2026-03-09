"""
RTI Agent Service - Conversational AI agent for RTI application filing
Uses Groq (primary) and Gemini (fallback) for LLM inference
"""
import json
import logging
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.config import settings
from rti_templates import detect_category, get_suggested_departments, get_guidance
from llm import GroqProvider, GeminiProvider

logger = logging.getLogger(__name__)


class RTIAgentService:
    """Conversational AI agent for guiding users through RTI application"""
    
    def __init__(self):
        self.groq = GroqProvider()
        self.gemini = GeminiProvider()
        if self.groq.is_available():
            logger.info(f"✓ Primary LLM: {self.groq.name}")
        if self.gemini.is_available():
            logger.info(f"✓ Fallback LLM: {self.gemini.name}")
        if not self.groq.is_available() and not self.gemini.is_available():
            logger.warning("⚠ No LLM providers available - using rule-based fallback only")
        
        self.language_instructions = {
            'en': {
                'lang': 'English',
                'role': 'You are a helpful RTI (Right to Information) assistant helping users file RTI applications in India.'
            },
            'hi': {
                'lang': 'Hindi',
                'role': 'आप भारत में उपयोगकर्ताओं को आरटीआई आवेदन दाखिल करने में मदद करने वाली एक महिला आरटीआई सहायक हैं।',
                'gender': 'आप एक महिला सहायक हैं। अपनी प्रतिक्रियाओं में स्त्री व्याकरण का प्रयोग करें (उदाहरण: "कर रही हूँ" कहें, "कर रहा हूँ" नहीं)।'
            },
            'kn': {
                'lang': 'Kannada',
                'role': 'ನೀವು ಭಾರತದಲ್ಲಿ ಆರ್‌ಟಿಐ ಅರ್ಜಿಗಳನ್ನು ಸಲ್ಲಿಸಲು ಬಳಕೆದಾರರಿಗೆ ಸಹಾಯ ಮಾಡುವ ಸಹಾಯಕ ಆರ್‌ಟಿಐ ಸಹಾಯಕರು.'
            }
        }

    def _get_providers(self, language: str):
        """Selects primary and fallback providers based on language."""
        is_indic = language in ["hi", "kn"]
        
        if is_indic and self.gemini.is_available():
            primary = self.gemini
            fallback = self.groq if self.groq.is_available() else None
            return primary, fallback

        if self.groq.is_available():
            primary = self.groq
            fallback = self.gemini if self.gemini.is_available() else None
            return primary, fallback

        if self.gemini.is_available():
            return self.gemini, None
            
        return None, None

    def get_agent_response(self, user_message: str, conversation_history: list, form_data: dict, language: str, mode: str) -> dict:
        """
        Get agent response based on conversation context and current mode.
        """
        logger.info(f"Processing in mode: {mode} for language: {language}")

        if mode == 'initial':
            return self._handle_initial_mode(user_message, language)
        elif mode == 'knowledge':
            return self._handle_knowledge_mode(user_message, conversation_history, language)
        elif mode == 'form-filling':
            return self._handle_form_filling_mode(user_message, conversation_history, form_data, language)
        else:
            # Default or error case
            return {
                "agent_response": "I'm sorry, something went wrong with my internal state. Could we start over?",
                "form_updates": {},
                "is_complete": False,
                "next_action": "continue_conversation",
                "mode": "initial"
            }

    def _handle_initial_mode(self, user_message: str, language: str) -> dict:
        """Determine the user's desired mode."""
        system_prompt = self._get_mode_selection_prompt(language)
        primary_provider, fallback_provider = self._get_providers(language)
        
        try:
            llm_response_str = self._generate_with_llm_with_fallback(
                primary_provider, fallback_provider, user_message, [], system_prompt, 50, 0.1
            )
            llm_json = json.loads(self._clean_llm_response(llm_response_str))
            new_mode = llm_json.get("mode", "knowledge")
            
            agent_response = ""
            if new_mode == "form-filling":
                # This response is only for the form-filling confirmation
                form_filling_responses = {
                    "en": "Great, let's start a new RTI application. What information would you like to request from the government?",
                    "hi": "ठीक है, चलिए एक नया आरटीआई आवेदन शुरू करते हैं। आप सरकार से कौन सी जानकारी प्राप्त करना चाहेंगे?",
                    "kn": "ಸರಿ, ಹೊಸ ಆರ್‌ಟಿಐ ಅರ್ಜಿಯನ್ನು ಪ್ರಾರಂಭಿಸೋಣ. ನೀವು ಸರ್ಕಾರದಿಂದ ಯಾವ ಮಾಹಿತಿಯನ್ನು ವಿನಂತಿಸಲು ಬಯಸುತ್ತೀರಿ?"
                }
                agent_response = form_filling_responses.get(language, form_filling_responses['en'])

        except Exception as e:
            logger.error(f"Error in initial mode selection: {e}", exc_info=True)
            new_mode = "knowledge"
            error_responses = {
                "en": "I had a little trouble understanding. Let's start with general information. What would you like to know?",
                "hi": "मुझे समझने में थोड़ी कठिनाई हुई। चलिए सामान्य जानकारी से शुरू करते हैं। आप क्या जानना चाहेंगे?",
                "kn": "ನನಗೆ ಅರ್ಥಮಾಡಿಕೊಳ್ಳಲು ಸ್ವಲ್ಪ ಕಷ್ಟವಾಯಿತು. ಸಾಮಾನ್ಯ ಮಾಹಿತಿಯೊಂದಿಗೆ ಪ್ರಾರಂಭಿಸೋಣ. ನೀವು ಏನು ತಿಳಿಯಲು ಬಯಸುತ್ತೀರಿ?"
            }
            agent_response = error_responses.get(language, error_responses['en'])

        return {
            "agent_response": agent_response,
            "form_updates": {"mode": new_mode},
            "is_complete": False,
            "next_action": "continue_conversation",
            "mode": new_mode
        }

    def _handle_knowledge_mode(self, user_message: str, conversation_history: list, language: str) -> dict:
        """Handle general Q&A and detect switch to form-filling mode."""
        system_prompt = self._get_knowledge_prompt(language)
        primary_provider, fallback_provider = self._get_providers(language)
        
        try:
            agent_message = self._generate_with_llm_with_fallback(
                primary_provider, fallback_provider, user_message, conversation_history, system_prompt, 1000, 0.7
            )

            # Check for mode switch command
            if agent_message.strip() == "SWITCH_MODE":
                logger.info("Switching from 'knowledge' to 'form-filling' mode.")
                # The user's message that triggered the switch is the starting point for the form.
                return self._handle_form_filling_mode(user_message, conversation_history, {}, language)

        except Exception as e:
            logger.error(f"Error in knowledge mode: {e}", exc_info=True)
            agent_message = "I'm sorry, I couldn't retrieve that information at the moment."

        return {
            "agent_response": agent_message,
            "form_updates": {},
            "is_complete": False,
            "next_action": "continue_conversation",
            "mode": "knowledge"
        }

    def _handle_form_filling_mode(self, user_message: str, conversation_history: list, form_data: dict, language: str) -> dict:
        """Handle the process of filling the RTI form."""
        system_prompt = self._get_form_filling_prompt(language, form_data)
        primary_provider, fallback_provider = self._get_providers(language)
        
        try:
            llm_response_str = self._generate_with_llm_with_fallback(
                primary_provider, fallback_provider, user_message, conversation_history, system_prompt
            )

            agent_message = "I'm sorry, I had trouble understanding that. Could you please rephrase?"
            form_updates = {}

            if llm_response_str:
                try:
                    llm_json = json.loads(self._clean_llm_response(llm_response_str))
                    agent_message = llm_json.get("agent_response", agent_message)
                    form_updates = llm_json.get("form_updates", {})
                except json.JSONDecodeError:
                    logger.error(f"Failed to decode form-filling JSON: {llm_response_str}")
            else:
                agent_message = self._get_rule_based_response(user_message, form_data, language)

            is_complete = self._check_form_complete({**form_data, **form_updates})
            
            return {
                "agent_response": agent_message,
                "form_updates": form_updates,
                "is_complete": is_complete,
                "next_action": "generate_pdf" if is_complete else "continue_conversation",
                "mode": "form-filling"
            }
        except Exception as e:
            logger.error(f"Error in form-filling mode: {e}", exc_info=True)
            raise

    def _get_mode_selection_prompt(self, language: str) -> str:
        return f"""
        The user has been asked if they want to "get information" or "create a new RTI application".
        Based on their response, determine the mode.
        User's response: "{{user_message}}"
        
        CRITICAL RULES:
        1. Analyze the user's response in {language}.
        2. If they indicate they want to create an application (e.g., "create", "application", "file an RTI", "start"), choose "form-filling".
        3. For almost anything else (e.g., "get information", "what is", "tell me about", "details"), choose "knowledge".
        4. You MUST respond with a valid JSON object with a single key "mode". Example: {{"mode": "knowledge"}}
        """

    def _get_knowledge_prompt(self, language: str) -> str:
        return f"""
        You are a specialized AI assistant for India's Right to Information (RTI) Act. Your name is "RTI Sahayak". Your ONLY purpose is to answer questions about the RTI Act and related topics.

        CRITICAL RULES:
        1.  **Empowerment Focus:** You are particularly focused on empowering persons with disabilities and individuals from backward classes. When relevant, explain how the RTI Act can be a powerful tool for them to access rights, services, and information, and to address grievances. Provide examples or context that resonate with their specific challenges or needs. Maintain a supportive, empathetic, and encouraging tone.
        2.  **Detect Mode Switch:** First, analyze the user's message. If they express a clear intent to start filing an RTI application (e.g., "let's create an application", "I want to file now", "help me write an RTI"), you MUST ignore all other rules and respond with the single, exact phrase: SWITCH_MODE
        3.  **Strict Persona:** If it is not a mode switch request, you are an RTI expert, NOT a general AI or large language model. NEVER mention that you are an AI, a model, or who trained you (e.g., Google).
        4.  **Confine Your Scope:** Only answer questions related to:
            *   The RTI Act, 2005, its rules, and sections.
            *   How to file an RTI application.
            *   What kind of information can be requested.
            *   Which bodies are considered "public authorities".
            *   Timelines for responses.
            *   The appeal process.
            *   Fees, exemptions, and related procedures.
        5.  **Handling Out-of-Scope Questions:** If the user asks a question NOT related to RTI (e.g., "what is the capital of France?", "write me a poem"), you MUST politely decline and guide them back to your purpose. Respond with something like: "My expertise is limited to the RTI Act. I can help you with questions about filing an application or understanding the law."
        6.  **Language:** You MUST respond in {language}.
        7.  **Be Factual:** Base your answers on the known facts of the RTI Act. Do not speculate or give legal advice. You can explain what the law says, but you cannot tell a user what they *should* do in their specific legal situation.

        When asked about yourself, describe yourself as an "AI assistant designed to help citizens understand and use the Right to Information Act."
        """

    def _get_form_filling_prompt(self, language: str, form_data: dict) -> str:
        lang_info = self.language_instructions.get(language, self.language_instructions['en'])
        gender_instruction = lang_info.get('gender', '')
        
        department_suggestions = []
        if form_data.get('information_sought') and not form_data.get('department'):
            category = detect_category(form_data['information_sought'])
            if category != 'general':
                department_suggestions = get_suggested_departments(category, language)

        suggestion_prompt = ""
        if department_suggestions:
            suggestions_str = ", ".join(f'"{d}"' for d in department_suggestions)
            suggestion_prompt = f"""
USER NEEDS HELP WITH THE DEPARTMENT.
Based on their request, here are some suggested departments: {suggestions_str}.
Ask the user to confirm one of these, or provide a different one. For example: 'It seems your query is related to education. Should I address it to the Ministry of Education, or another department?'
"""

        prompt = f"""{lang_info['role']}
{gender_instruction}

CRITICAL RULES:
1. Your primary goal is to collect information for the form by asking one question at a time.
2. You MUST respond with a valid JSON object. No other text or explanation.
3. The JSON object must have two keys: "agent_response" (your conversational reply) and "form_updates" (a JSON object of fields you have updated).
4. Keep your "agent_response" under 3 sentences.
5. If responding in Hindi, ALWAYS use feminine grammar (e.g., "कर रही हूँ").
6. Maintain a supportive, patient, and extra clear tone, especially considering users who may have disabilities or are from marginalized communities. Ensure questions are easy to understand.

CONVERSATION FLOW:
- Your default mode is to be efficient. When the user provides information, update the form and IMMEDIATELY ask the next unanswered question.
- **If the user doesn't know the department, use the suggestions provided below to help them.**
- **Query Refinement**: After capturing the initial `information_sought`, analyze it. If it is brief (under 10 words), help the user expand on it. Suggest specific angles (e.g., "Are you interested in budget details, implementation status, or official reports?"). Ask clarifying questions to collaboratively build a detailed query. Once a detailed query is drafted, confirm it with the user before asking for the department.
- ONLY enter a "correction" mode if the user's message explicitly indicates a mistake (e.g., "no", "wrong", "change", "update", "correct that").
- In correction mode, ask for clarification, update the field, and confirm the change before proceeding.

FORM FIELD SCHEMA:
Your "form_updates" JSON object MUST use these exact keys:
- "applicant_name"
- "address"
- "information_sought"
- "department"

CURRENT FORM STATUS:
{json.dumps(form_data, indent=2, ensure_ascii=False)}
{suggestion_prompt}
YOUR TASK:
Based on the user's message and the conversation flow, generate the JSON output.

EXAMPLE 1: User provides new information (Efficient Flow).
User message: "I want to know about the budget for street lights in my area for the last financial year."
Your JSON output:
{{
  "agent_response": "Thank you. It looks like your request is about transport. Should I send this to the Ministry of Road Transport and Highways, or do you have a different department in mind?",
  "form_updates": {{
    "information_sought": "I want to know about the budget for street lights in my area for the last financial year."
  }}
}}

EXAMPLE 2: User provides the next piece of information.
User message: "The Ministry of Urban Development"
Your JSON output:
{{
  "agent_response": "Got it. What is your full name for the application?",
  "form_updates": {{
    "department": "The Ministry of Urban Development"
  }}
}}

EXAMPLE 3: User wants to make a correction.
User message: "No, the department is wrong, it should be the local municipal corporation"
Your JSON output:
{{
  "agent_response": "My mistake. I've updated the department to 'local municipal corporation'. Is this correct?",
  "form_updates": {{
    "department": "local municipal corporation"
  }}
}}

EXAMPLE 4: User provides a brief query needing refinement.
User message: "Tell me about school accessibility."
Your JSON output:
{{
  "agent_response": "I can help with that. To make your request more effective, we can add more detail. Are you interested in policies regarding accessibility, or data on existing features like ramps and accessible restrooms in schools?",
  "form_updates": {{
    "information_sought": "Tell me about school accessibility."
  }}
}}

EXAMPLE 5: User chooses a refinement path.
User message: "Let's focus on policies."
Your JSON output:
{{
  "agent_response": "Good choice. To be more specific, should we ask for policies at the national level, state level, or for a particular district?",
  "form_updates": {{}}
}}

EXAMPLE 6: User provides final detail, agent synthesizes.
User message: "National level policies for visually impaired students."
Your JSON output:
{{
  "agent_response": "Excellent. I've drafted this detailed query: 'Please provide copies of all current national-level policies and guidelines concerning the accessibility of educational infrastructure and materials for visually impaired students.' Shall I use this for your application?",
  "form_updates": {{
    "information_sought": "Please provide copies of all current national-level policies and guidelines concerning the accessibility of educational infrastructure and materials for visually impaired students."
  }}
}}
"""
        return prompt


    def _clean_llm_response(self, response_str: str) -> str:
        """Cleans the LLM response by removing markdown code blocks."""
        cleaned_str = response_str.strip()
        if cleaned_str.startswith("```json"):
            cleaned_str = cleaned_str[7:]
        if cleaned_str.endswith("```"):
            cleaned_str = cleaned_str[:-3]
        return cleaned_str.strip()
    
    def _generate_with_llm_with_fallback(self, primary_provider, fallback_provider, user_message, conversation_history, system_prompt, max_tokens=500, temperature=0.5):
        """Generate with primary provider and fallback to secondary."""
        llm_response_str = None
        try:
            if not primary_provider:
                raise ValueError("No primary provider available.")
            logger.info(f"Attempting to generate response with primary provider: {primary_provider.name}")
            llm_response_str = self._generate_with_llm(
                primary_provider, user_message, conversation_history, system_prompt, max_tokens, temperature
            )
        except Exception as e:
            logger.error(f"Primary LLM provider {primary_provider.name} failed: {e}", exc_info=True)
            if fallback_provider and fallback_provider.is_available():
                logger.info(f"Attempting to generate response with fallback provider: {fallback_provider.name}")
                llm_response_str = self._generate_with_llm(
                    fallback_provider, user_message, conversation_history, system_prompt, max_tokens, temperature
                )
            else:
                # If no fallback, we just let the exception be handled by the calling function
                llm_response_str = None
        
        if llm_response_str is None:
            raise ValueError("All LLM providers failed to generate a response.")
            
        return llm_response_str

    def _generate_with_llm(self, provider, user_message: str, conversation_history: list, system_prompt: str, max_tokens=500, temperature=0.5) -> str:
        """Generic LLM generation function."""
        messages = [{"role": msg["role"], "content": msg["content"]} for msg in conversation_history[-10:]]
        messages.append({"role": "user", "content": user_message})
        
        # Replace placeholder in prompt
        final_system_prompt = system_prompt.replace("{{user_message}}", user_message)

        response = provider.generate(
            messages=messages,
            system_prompt=final_system_prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
        logger.info(f"--- LLM Response ({provider.name}) ---")
        logger.info(response)
        logger.info("--------------------")
        return response
    
    def _check_form_complete(self, form_data: dict) -> bool:
        """Check if all required fields are filled"""
        required_fields = ['applicant_name', 'address', 'information_sought', 'department']
        return all(form_data.get(field) for field in required_fields)
    
    def _get_rule_based_response(self, user_message: str, form_data: dict, language: str) -> str:
        # ... (existing rule-based logic)
        return "This is a rule-based fallback response."

    def get_initial_greeting(self, language: str) -> str:
        """Get initial greeting message that offers a choice."""
        greetings = {
            'en': "Hello! I am your RTI assistant, here to empower you. Would you like to get information on a topic, or would you like to create a new RTI application?",
            'hi': "नमस्ते! मैं आपकी आरटीआई सहायक हूँ, आपको सशक्त बनाने के लिए यहाँ हूँ। क्या आप किसी विषय पर जानकारी प्राप्त करना चाहेंगी, या आप एक नया आरटीआई आवेदन बनाना चाहेंगी?",
            'kn': "ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ ಆರ್‌ಟಿಐ ಸಹಾಯಕ, ನಿಮಗೆ ಅಧಿಕಾರ ನೀಡಲು ಇಲ್ಲಿದ್ದೇನೆ. ನೀವು ಒಂದು ವಿಷಯದ ಬಗ್ಗೆ ಮಾಹಿತಿ ಪಡೆಯಲು ಬಯಸುತ್ತೀರಾ, ಅಥವಾ ನೀವು ಹೊಸ ಆರ್‌ಟಿಐ ಅರ್ಜಿಯನ್ನು ರಚಿಸಲು ಬಯಸುತ್ತೀರಾ?"
        }
        return greetings.get(language, greetings['en'])
