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
        # Initialize LLM providers
        self.groq = GroqProvider()
        self.gemini = GeminiProvider()
        
        # Log available providers
        if self.groq.is_available():
            logger.info(f"✓ Primary LLM: {self.groq.name}")
        if self.gemini.is_available():
            logger.info(f"✓ Fallback LLM: {self.gemini.name}")
        if not self.groq.is_available() and not self.gemini.is_available():
            logger.warning("⚠ No LLM providers available - using rule-based fallback only")

    def get_agent_response(self, user_message: str, conversation_history: list, form_data: dict, language: str = 'en') -> dict:
        """
        Get agent response based on conversation context.
        The LLM is tasked with returning a JSON object containing the response and form updates.
        """
        logger.info("="*50)
        logger.info(f"User message: {user_message}")
        logger.info(f"Current form data: {json.dumps(form_data, indent=2)}")
        logger.info("="*50)
        
        try:
            llm_response_str = None
            
            primary_provider = None
            fallback_provider = None

            if language in ["hi", "kn"]:
                primary_provider = self.gemini if self.gemini.is_available() else self.groq
                fallback_provider = self.groq if primary_provider == self.gemini and self.groq.is_available() else None
            else:
                primary_provider = self.groq if self.groq.is_available() else self.gemini
                fallback_provider = self.gemini if primary_provider == self.groq and self.gemini.is_available() else None

            llm_response_str = None
            
            if primary_provider:
                try:
                    logger.info(f"Attempting to generate response with primary provider: {primary_provider.name}")
                    llm_response_str = self._generate_with_llm(
                        primary_provider,
                        user_message,
                        conversation_history,
                        form_data,
                        language
                    )
                except Exception as e:
                    logger.error(f"Primary LLM provider {primary_provider.name} failed: {e}", exc_info=True)
                    
                    if fallback_provider:
                        try:
                            logger.info(f"Attempting to generate response with fallback provider: {fallback_provider.name}")
                            llm_response_str = self._generate_with_llm(
                                fallback_provider,
                                user_message,
                                conversation_history,
                                form_data,
                                language
                            )
                        except Exception as fallback_e:
                            logger.error(f"Fallback LLM provider {fallback_provider.name} failed: {fallback_e}", exc_info=True)
                            llm_response_str = None  # Ensure it's None if fallback also fails
            
            # Initialize default values
            agent_message = "I'm sorry, I had trouble understanding that. Could you please rephrase?"
            form_updates = {}

            if llm_response_str:
                try:
                    cleaned_response = self._clean_llm_response(llm_response_str)
                    # The LLM's entire response should be a JSON string
                    llm_json = json.loads(cleaned_response)
                    agent_message = llm_json.get("agent_response", agent_message)
                    form_updates = llm_json.get("form_updates", {})
                except json.JSONDecodeError:
                    logger.error(f"Failed to decode LLM JSON response: {llm_response_str}")
                    # If JSON is bad, we keep the default error message
            else:
                # Fallback to rule-based if all LLMs fail
                logger.info("Using rule-based fallback as no LLM was available or all failed.")
                agent_message = self._get_rule_based_response(user_message, form_data, language)

            final_form_data = {**form_data, **form_updates}
            is_complete = self._check_form_complete(final_form_data)
            
            return {
                "agent_response": agent_message,
                "form_updates": form_updates,
                "is_complete": is_complete,
                "next_action": "generate_pdf" if is_complete else "continue_conversation"
            }
        
        except Exception as e:
            logger.error(f"Agent error in get_agent_response: {e}", exc_info=True)
            raise

    def _clean_llm_response(self, response_str: str) -> str:
        """Cleans the LLM response by removing markdown code blocks."""
        cleaned_str = response_str.strip()
        if cleaned_str.startswith("```json"):
            cleaned_str = cleaned_str[7:]
        if cleaned_str.endswith("```"):
            cleaned_str = cleaned_str[:-3]
        return cleaned_str.strip()
    
    def _generate_with_llm(
        self,
        provider,
        user_message: str,
        conversation_history: list,
        form_data: dict,
        language: str
    ) -> str:
        """Generate response using an LLM provider"""
        messages = []
        for msg in conversation_history[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": user_message})
        
        system_prompt = self._get_system_prompt(language, form_data)
        
        # logger.info("--- Sending to LLM ---")
        # logger.info(f"System Prompt:\n{system_prompt}")
        # logger.info(f"Messages:\n{json.dumps(messages, indent=2)}")
        # logger.info("-----------------------")

        response = provider.generate(
            messages=messages,
            system_prompt=system_prompt,
            max_tokens=500,  # Increased for JSON structure
            temperature=0.5  # Reduced for more predictable JSON
        )
        
        logger.info("--- LLM Response ---")
        logger.info(response)
        logger.info("--------------------")
        
        return response
    
    def _get_system_prompt(self, language: str, form_data: dict) -> str:
        """Get strict system prompt for the agent"""
        
        language_instructions = {
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
        
        lang_info = language_instructions.get(language, language_instructions['en'])
        gender_instruction = lang_info.get('gender', '')
        
        # Department suggestion logic
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
    
    def _build_context(self, form_data: dict, language: str) -> str:
        """Build context string from form data"""
        context_parts = []
        
        if form_data.get('information_sought'):
            context_parts.append(f"Information sought: {form_data['information_sought']}")
        if form_data.get('department'):
            context_parts.append(f"Department: {form_data['department']}")
        if form_data.get('applicant_name'):
            context_parts.append(f"Name: {form_data['applicant_name']}")
        if form_data.get('address'):
            context_parts.append(f"Address: {form_data['address']}")
        
        return "\n".join(context_parts) if context_parts else "No information collected yet"
    
    def _check_form_complete(self, form_data: dict) -> bool:
        """Check if all required fields are filled"""
        required_fields = ['applicant_name', 'address', 'information_sought', 'department']
        return all(form_data.get(field) for field in required_fields)
    
    def _get_rule_based_response(self, user_message: str, form_data: dict, language: str) -> str:
        """
        Generate rule-based response when LLMs are unavailable
        Simple conversational logic based on what's missing
        """
        responses = {
            'en': {
                'need_info': "Thank you! I understand you want information about {topic}. Which government department should I address this request to?",
                'need_dept': "Got it! Now, what is your name for the RTI application?",
                'need_name': "Thank you, {name}! What is your address?",
                'need_address': "Perfect! Let me confirm the details:\n- Information: {info}\n- Department: {dept}\n- Name: {name}\n- Address: {address}\n\nIs this correct?",
                'complete': "Great! Your RTI application is complete. Would you like me to generate the PDF document?",
                'acknowledge': "I understand. {message}"
            },
            'hi': {
                'need_info': "धन्यवाद! मैं समझ गया कि आप {topic} के बारे में जानकारी चाहते हैं। मुझे किस सरकारी विभाग को यह अनुरोध भेजना चाहिए?",
                'need_dept': "समझ गया! अब, आरटीआई आवेदन के लिए आपका नाम क्या है?",
                'need_name': "धन्यवाद, {name}! आपका पता क्या है?",
                'need_address': "बिल्कुल सही! मुझे विवरण की पुष्टि करने दें:\n- जानकारी: {info}\n- विभाग: {dept}\n- नाम: {name}\n- पता: {address}\n\nक्या यह सही है?",
                'complete': "बढ़िया! आपका आरटीआई आवेदन पूरा हो गया है। क्या आप चाहते हैं कि मैं पीडीएफ दस्तावेज़ बनाऊं?",
                'acknowledge': "मैं समझ गया। {message}"
            },
            'kn': {
                'need_info': "ಧನ್ಯವಾದಗಳು! ನೀವು {topic} ಬಗ್ಗೆ ಮಾಹಿತಿ ಬಯಸುತ್ತೀರಿ ಎಂದು ನಾನು ಅರ್ಥಮಾಡಿಕೊಂಡಿದ್ದೇನೆ. ನಾನು ಈ ವಿನಂತಿಯನ್ನು ಯಾವ ಸರ್ಕಾರಿ ಇಲಾಖೆಗೆ ಕಳುಹಿಸಬೇಕು?",
                'need_dept': "ಅರ್ಥವಾಯಿತು! ಈಗ, ಆರ್‌ಟಿಐ ಅರ್ಜಿಗಾಗಿ ನಿಮ್ಮ ಹೆಸರು ಏನು?",
                'need_name': "ಧನ್ಯವಾದಗಳು, {name}! ನಿಮ್ಮ ವಿಳಾಸ ಏನು?",
                'need_address': "ಪರಿಪೂರ್ಣ! ವಿವರಗಳನ್ನು ದೃಢೀಕರಿಸೋಣ:\n- ಮಾಹಿತಿ: {info}\n- ಇಲಾಖೆ: {dept}\n- ಹೆಸರು: {name}\n- ವಿಳಾಸ: {address}\n\nಇದು ಸರಿಯಾಗಿದೆಯೇ?",
                'complete': "ಅದ್ಭುತ! ನಿಮ್ಮ ಆರ್‌ಟಿಐ ಅರ್ಜಿ ಪೂರ್ಣಗೊಂಡಿದೆ. ನಾನು ಪಿಡಿಎಫ್ ದಾಖಲೆಯನ್ನು ರಚಿಸಬೇಕೆ?",
                'acknowledge': "ನಾನು ಅರ್ಥಮಾಡಿಕೊಂಡಿದ್ದೇನೆ। {message}"
            }
        }
        
        lang_responses = responses.get(language, responses['en'])
        
        # Determine what to ask based on what's missing
        if not form_data.get('information_sought'):
            return lang_responses['acknowledge'].format(message=user_message)
        elif not form_data.get('department'):
            topic = form_data.get('information_sought', 'this')
            return lang_responses['need_info'].format(topic=topic)
        elif not form_data.get('applicant_name'):
            return lang_responses['need_dept']
        elif not form_data.get('address'):
            name = form_data.get('applicant_name', '')
            return lang_responses['need_name'].format(name=name)
        else:
            # All fields present - confirm
            return lang_responses['need_address'].format(
                info=form_data.get('information_sought', ''),
                dept=form_data.get('department', ''),
                name=form_data.get('applicant_name', ''),
                address=form_data.get('address', '')
            )
    
    def get_initial_greeting(self, language: str) -> str:
        """Get initial greeting message"""
        greetings = {
            'en': "Hello! I'm your RTI assistant. I'll help you file a Right to Information application. What information would you like to request from the government?",
            
            'hi': "नमस्ते! मैं आपकी आरटीआई सहायक हूँ। मैं आपको सूचना का अधिकार आवेदन दाखिल करने में मदद करूँगी। आप सरकार से कौन सी जानकारी प्राप्त करना चाहती हैं?",
            
            'kn': "ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ ಆರ್‌ಟಿಐ ಸಹಾಯಕ. ನಾನು ನಿಮಗೆ ಮಾಹಿತಿ ಹಕ್ಕು ಅರ್ಜಿ ಸಲ್ಲಿಸಲು ಸಹಾಯ ಮಾಡುತ್ತೇನೆ. ನೀವು ಸರ್ಕಾರದಿಂದ ಯಾವ ಮಾಹಿತಿಯನ್ನು ವಿನಂತಿಸಲು ಬಯಸುತ್ತೀರಿ?"
        }
        return greetings.get(language, greetings['en'])
