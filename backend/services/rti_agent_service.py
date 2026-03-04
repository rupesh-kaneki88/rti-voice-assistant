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

    def _get_rule_based_response(self, user_message, form_data, language):
        return "Bedrock is unavailable. This is a fallback response."
    
    def get_agent_response(self, user_message: str, conversation_history: list, form_data: dict, language: str = 'en') -> dict:
        """
        Get agent response based on conversation context
        
        Args:
            user_message: User's current message
            conversation_history: List of previous messages
            form_data: Current form data
            language: Language code
            
        Returns:
            Dict with agent_response, next_question, form_updates, is_complete
        """
        try:
            # Extract form updates from user message first
            form_updates = self._extract_form_updates(user_message, form_data)
            
            # Update form_data with new updates for context
            updated_form_data = {**form_data, **form_updates}
            
            # Try to use LLM providers with conditional switching
            agent_message = None
            
            # Conditional switching: Use Gemini for Hindi/Kannada, Groq for English
            if language in ["hi", "kn"]:
                # Prefer Gemini for Indian languages
                if self.gemini.is_available():
                    try:
                        agent_message = self._generate_with_llm(
                            self.gemini,
                            user_message,
                            conversation_history,
                            updated_form_data,
                            language
                        )
                    except Exception as e:
                        logger.warning(f"Gemini failed: {e}, trying Groq...")
                        if self.groq.is_available():
                            try:
                                agent_message = self._generate_with_llm(
                                    self.groq,
                                    user_message,
                                    conversation_history,
                                    updated_form_data,
                                    language
                                )
                            except Exception as e2:
                                logger.warning(f"Groq also failed: {e2}")
                elif self.groq.is_available():
                    try:
                        agent_message = self._generate_with_llm(
                            self.groq,
                            user_message,
                            conversation_history,
                            updated_form_data,
                            language
                        )
                    except Exception as e:
                        logger.warning(f"Groq failed: {e}")
            else:
                # Prefer Groq for English
                if self.groq.is_available():
                    try:
                        agent_message = self._generate_with_llm(
                            self.groq,
                            user_message,
                            conversation_history,
                            updated_form_data,
                            language
                        )
                    except Exception as e:
                        logger.warning(f"Groq failed: {e}, trying Gemini...")
                        if self.gemini.is_available():
                            try:
                                agent_message = self._generate_with_llm(
                                    self.gemini,
                                    user_message,
                                    conversation_history,
                                    updated_form_data,
                                    language
                                )
                            except Exception as e2:
                                logger.warning(f"Gemini also failed: {e2}")
                elif self.gemini.is_available():
                    try:
                        agent_message = self._generate_with_llm(
                            self.gemini,
                            user_message,
                            conversation_history,
                            updated_form_data,
                            language
                        )
                    except Exception as e:
                        logger.warning(f"Gemini failed: {e}")
            
            # Fallback to rule-based if all LLMs fail
            if not agent_message:
                logger.info("Using rule-based fallback")
                agent_message = self._get_rule_based_response(user_message, updated_form_data, language)
            
            # Check if form is complete
            is_complete = self._check_form_complete(updated_form_data)
            
            return {
                "agent_response": agent_message,
                "form_updates": form_updates,
                "is_complete": is_complete,
                "next_action": "generate_pdf" if is_complete else "continue_conversation"
            }
        
        except Exception as e:
            logger.error(f"Agent error: {e}", exc_info=True)
            raise
    
    def _generate_with_llm(
        self,
        provider,
        user_message: str,
        conversation_history: list,
        form_data: dict,
        language: str
    ) -> str:
        """Generate response using an LLM provider"""
        # Build messages for LLM
        messages = []
        
        # Add conversation history (last 3 exchanges)
        for msg in conversation_history[-6:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Get system prompt
        system_prompt = self._get_system_prompt(language, form_data)
        
        # Generate response
        logger.info(f"Generating with {provider.name} for language={language}")
        response = provider.generate(
            messages=messages,
            system_prompt=system_prompt,
            max_tokens=300,  # Keep responses short
            temperature=0.7
        )
        
        return response
    
    def _get_system_prompt(self, language: str, form_data: dict) -> str:
        """Get strict system prompt for the agent"""
        
        # Check what's missing
        missing_fields = []
        if not form_data.get('applicant_name'):
            missing_fields.append('name')
        if not form_data.get('address'):
            missing_fields.append('address')
        if not form_data.get('information_sought'):
            missing_fields.append('information they want')
        if not form_data.get('department'):
            missing_fields.append('government department')
        
        language_instructions = {
            'en': {
                'lang': 'English',
                'role': 'You are a helpful RTI (Right to Information) assistant helping users file RTI applications in India.'
            },
            'hi': {
                'lang': 'Hindi',
                'role': 'आप एक सहायक आरटीआई (सूचना का अधिकार) सहायक हैं जो भारत में उपयोगकर्ताओं को आरटीआई आवेदन दाखिल करने में मदद कर रहे हैं।'
            },
            'kn': {
                'lang': 'Kannada',
                'role': 'ನೀವು ಭಾರತದಲ್ಲಿ ಆರ್‌ಟಿಐ ಅರ್ಜಿಗಳನ್ನು ಸಲ್ಲಿಸಲು ಬಳಕೆದಾರರಿಗೆ ಸಹಾಯ ಮಾಡುವ ಸಹಾಯಕ ಆರ್‌ಟಿಐ ಸಹಾಯಕರು.'
            }
        }
        
        lang_info = language_instructions.get(language, language_instructions['en'])
        
        prompt = f"""{lang_info['role']}

CRITICAL RULES - YOU MUST FOLLOW THESE:
1. Respond ONLY in {lang_info['lang']} language
2. Ask ONLY ONE question at a time
3. Keep your response under 3 sentences
4. NEVER give legal advice - only help collect information
5. Focus ONLY on collecting missing form fields
6. Be conversational but brief
7. Do NOT explain RTI Act unless asked
8. Do NOT provide examples unless asked

CURRENT FORM STATUS:
{json.dumps(form_data, indent=2, ensure_ascii=False)}

MISSING INFORMATION: {', '.join(missing_fields) if missing_fields else 'None - form is complete!'}

YOUR TASK:
- If information is missing, ask for the NEXT missing field only
- If user provides information, acknowledge briefly and ask for next field
- If form is complete, confirm and offer to generate PDF
- Keep responses SHORT and FOCUSED

CONVERSATION FLOW:
1. information_sought (what they want to know)
2. department (which government department)
3. applicant_name (their name)
4. address (their address)
5. Confirm and generate PDF

Remember: ONE question, under 3 sentences, {lang_info['lang']} only, no legal advice."""

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
    
    def _extract_form_updates(self, user_message: str, current_form_data: dict) -> dict:
        """Extract form field updates from user message"""
        updates = {}
        
        message_lower = user_message.lower()
        
        # Detect category and suggest department
        if not current_form_data.get('department'):
            category = detect_category(user_message)
            if category != "general":
                suggested_depts = get_suggested_departments(category, 'en')
                if suggested_depts:
                    updates['department'] = suggested_depts[0]
        
        # Check for department mentions
        departments = ['education', 'health', 'transport', 'finance', 'agriculture', 
                      'शिक्षा', 'स्वास्थ्य', 'परिवहन', 'वित्त']
        for dept in departments:
            if dept in message_lower:
                if 'education' in message_lower or 'शिक्षा' in message_lower:
                    updates['department'] = 'Ministry of Education'
                elif 'health' in message_lower or 'स्वास्थ्य' in message_lower:
                    updates['department'] = 'Ministry of Health'
                elif 'transport' in message_lower or 'परिवहन' in message_lower:
                    updates['department'] = 'Ministry of Road Transport and Highways'
                break
        
        # Extract name if mentioned
        name_patterns = ['my name is', 'i am', 'मेरा नाम', 'मैं', 'ನನ್ನ ಹೆಸರು']
        for pattern in name_patterns:
            if pattern in message_lower:
                # Extract name after pattern
                parts = user_message.split(pattern, 1)
                if len(parts) > 1:
                    name = parts[1].strip().split('.')[0].split(',')[0]
                    if name and len(name) < 50:
                        updates['applicant_name'] = name
                break
        
        # Extract address if mentioned
        address_patterns = ['address', 'live at', 'residing at', 'पता', 'ವಿಳಾಸ']
        for pattern in address_patterns:
            if pattern in message_lower:
                # Extract address after pattern
                parts = user_message.split(pattern, 1)
                if len(parts) > 1:
                    address = parts[1].strip()
                    if address and len(address) > 5:
                        updates['address'] = address
                break
        
        # If message is long and no specific field identified, it might be information_sought
        if len(user_message.split()) > 5 and not current_form_data.get('information_sought'):
            if not any(word in message_lower for word in ['my name is', 'मेरा नाम', 'i am', 'मैं', 'address', 'पता']):
                updates['information_sought'] = user_message
        
        return updates
    
    def _check_form_complete(self, form_data: dict) -> bool:
        """Check if all required fields are filled"""
        required_fields = ['applicant_name', 'address', 'information_sought', 'department']
        return all(form_data.get(field) for field in required_fields)
    
    def _get_rule_based_response(self, user_message: str, form_data: dict, language: str) -> str:
        """
        Generate rule-based response when Bedrock is unavailable
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
            'hi': "नमस्ते! मैं आपका आरटीआई सहायक हूं। मैं आपको सूचना का अधिकार आवेदन दाखिल करने में मदद करूंगा। आप सरकार से कौन सी जानकारी चाहते हैं?",
            'kn': "ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ ಆರ್‌ಟಿಐ ಸಹಾಯಕ. ನಾನು ನಿಮಗೆ ಮಾಹಿತಿ ಹಕ್ಕು ಅರ್ಜಿ ಸಲ್ಲಿಸಲು ಸಹಾಯ ಮಾಡುತ್ತೇನೆ. ನೀವು ಸರ್ಕಾರದಿಂದ ಯಾವ ಮಾಹಿತಿಯನ್ನು ವಿನಂತಿಸಲು ಬಯಸುತ್ತೀರಿ?"
        }
        return greetings.get(language, greetings['en'])
