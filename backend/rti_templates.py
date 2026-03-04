"""
RTI Application Templates for Common Requests
These templates help the agent guide users through common RTI scenarios
Fully Multilingual RTI Templates
Supports English (en), Hindi (hi), Kannada (kn)
"""

RTI_TEMPLATES = {

    # =========================
    # EDUCATION
    # =========================
    "education": {
        "en": {
            "name": "Education Information Request",
            "common_questions": [
                "Details of government spending on education in my district",
                "Information about scholarship schemes and eligibility",
                "Details of school infrastructure development projects"
            ],
            "suggested_departments": [
                "Ministry of Education",
                "Department of School Education",
                "University Grants Commission"
            ],
            "guidance": "You may request details about education spending, scholarships, infrastructure, or recruitment."
        },
        "hi": {
            "name": "शिक्षा सूचना अनुरोध",
            "common_questions": [
                "मेरे जिले में शिक्षा पर सरकारी खर्च का विवरण",
                "छात्रवृत्ति योजनाओं और पात्रता की जानकारी",
                "स्कूल बुनियादी ढांचा विकास परियोजनाओं का विवरण"
            ],
            "suggested_departments": [
                "शिक्षा मंत्रालय",
                "स्कूल शिक्षा विभाग",
                "विश्वविद्यालय अनुदान आयोग"
            ],
            "guidance": "आप शिक्षा खर्च, छात्रवृत्ति, बुनियादी ढांचे या भर्ती से संबंधित जानकारी मांग सकते हैं।"
        },
        "kn": {
            "name": "ಶಿಕ್ಷಣ ಮಾಹಿತಿ ವಿನಂತಿ",
            "common_questions": [
                "ನನ್ನ ಜಿಲ್ಲೆಯಲ್ಲಿ ಶಿಕ್ಷಣದ ಮೇಲೆ ಸರ್ಕಾರಿ ವೆಚ್ಚದ ವಿವರಗಳು",
                "ವಿದ್ಯಾರ್ಥಿವೇತನ ಯೋಜನೆಗಳು ಮತ್ತು ಅರ್ಹತೆಯ ಮಾಹಿತಿ",
                "ಶಾಲಾ ಮೂಲಸೌಕರ್ಯ ಅಭಿವೃದ್ಧಿ ಯೋಜನೆಗಳ ವಿವರಗಳು"
            ],
            "suggested_departments": [
                "ಶಿಕ್ಷಣ ಸಚಿವಾಲಯ",
                "ಶಾಲಾ ಶಿಕ್ಷಣ ಇಲಾಖೆ",
                "ವಿಶ್ವವಿದ್ಯಾಲಯ ಅನುದಾನ ಆಯೋಗ"
            ],
            "guidance": "ನೀವು ಶಿಕ್ಷಣ ವೆಚ್ಚ, ವಿದ್ಯಾರ್ಥಿವೇತನ, ಮೂಲಸೌಕರ್ಯ ಅಥವಾ ನೇಮಕಾತಿ ಕುರಿತು ಮಾಹಿತಿ ಕೇಳಬಹುದು."
        }
    },

    # =========================
    # HEALTH
    # =========================
    "health": {
        "en": {
            "name": "Health Information Request",
            "common_questions": [
                "Details of government health schemes in my area",
                "Hospital infrastructure and facilities information",
                "Medicine procurement and distribution details"
            ],
            "suggested_departments": [
                "Ministry of Health and Family Welfare",
                "Department of Health Services",
                "National Health Mission"
            ],
            "guidance": "You may request details about hospitals, medicines, schemes, or public health programs."
        },
        "hi": {
            "name": "स्वास्थ्य सूचना अनुरोध",
            "common_questions": [
                "मेरे क्षेत्र में सरकारी स्वास्थ्य योजनाओं का विवरण",
                "अस्पताल सुविधाओं की जानकारी",
                "दवाओं की खरीद और वितरण का विवरण"
            ],
            "suggested_departments": [
                "स्वास्थ्य और परिवार कल्याण मंत्रालय",
                "स्वास्थ्य सेवा विभाग",
                "राष्ट्रीय स्वास्थ्य मिशन"
            ],
            "guidance": "आप अस्पताल, दवाओं या स्वास्थ्य योजनाओं से संबंधित जानकारी मांग सकते हैं।"
        },
        "kn": {
            "name": "ಆರೋಗ್ಯ ಮಾಹಿತಿ ವಿನಂತಿ",
            "common_questions": [
                "ನನ್ನ ಪ್ರದೇಶದಲ್ಲಿ ಸರ್ಕಾರಿ ಆರೋಗ್ಯ ಯೋಜನೆಗಳ ವಿವರಗಳು",
                "ಆಸ್ಪತ್ರೆ ಸೌಲಭ್ಯಗಳ ಮಾಹಿತಿ",
                "ಔಷಧ ಖರೀದಿ ಮತ್ತು ವಿತರಣೆ ವಿವರಗಳು"
            ],
            "suggested_departments": [
                "ಆರೋಗ್ಯ ಮತ್ತು ಕುಟುಂಬ ಕಲ್ಯಾಣ ಸಚಿವಾಲಯ",
                "ಆರೋಗ್ಯ ಸೇವಾ ಇಲಾಖೆ",
                "ರಾಷ್ಟ್ರೀಯ ಆರೋಗ್ಯ ಮಿಷನ್"
            ],
            "guidance": "ನೀವು ಆಸ್ಪತ್ರೆಗಳು, ಔಷಧಿಗಳು ಅಥವಾ ಆರೋಗ್ಯ ಯೋಜನೆಗಳ ಕುರಿತು ಮಾಹಿತಿ ಕೇಳಬಹುದು."
        }
    },

    # =========================
    # TRANSPORT
    # =========================
    "transport": {
        "en": {
            "name": "Transport Information Request",
            "common_questions": [
                "Road construction projects in my area",
                "Public transport schemes and subsidies",
                "Traffic management measures"
            ],
            "suggested_departments": [
                "Ministry of Road Transport and Highways",
                "Department of Transport",
                "National Highways Authority"
            ],
            "guidance": "You may request information about roads, public transport, or traffic management."
        },
        "hi": {
            "name": "परिवहन सूचना अनुरोध",
            "common_questions": [
                "मेरे क्षेत्र में सड़क निर्माण परियोजनाएं",
                "सार्वजनिक परिवहन योजनाएं",
                "यातायात प्रबंधन उपाय"
            ],
            "suggested_departments": [
                "सड़क परिवहन और राजमार्ग मंत्रालय",
                "परिवहन विभाग",
                "राष्ट्रीय राजमार्ग प्राधिकरण"
            ],
            "guidance": "आप सड़क, परिवहन या यातायात प्रबंधन से संबंधित जानकारी मांग सकते हैं।"
        },
        "kn": {
            "name": "ಸಾರಿಗೆ ಮಾಹಿತಿ ವಿನಂತಿ",
            "common_questions": [
                "ನನ್ನ ಪ್ರದೇಶದಲ್ಲಿ ರಸ್ತೆ ನಿರ್ಮಾಣ ಯೋಜನೆಗಳು",
                "ಸಾರ್ವಜನಿಕ ಸಾರಿಗೆ ಯೋಜನೆಗಳು",
                "ಸಂಚಾರ ನಿರ್ವಹಣಾ ಕ್ರಮಗಳು"
            ],
            "suggested_departments": [
                "ರಸ್ತೆ ಸಾರಿಗೆ ಮತ್ತು ಹೆದ್ದಾರಿ ಸಚಿವಾಲಯ",
                "ಸಾರಿಗೆ ಇಲಾಖೆ",
                "ರಾಷ್ಟ್ರೀಯ ಹೆದ್ದಾರಿ ಪ್ರಾಧಿಕಾರ"
            ],
            "guidance": "ನೀವು ರಸ್ತೆ, ಸಾರಿಗೆ ಅಥವಾ ಸಂಚಾರ ನಿರ್ವಹಣೆ ಕುರಿತು ಮಾಹಿತಿ ಕೇಳಬಹುದು."
        }
    },

    # =========================
    # EMPLOYMENT
    # =========================
    "employment": {
        "en": {
            "name": "Employment Information Request",
            "common_questions": [
                "Government job vacancies",
                "Recruitment process details",
                "Skill development schemes"
            ],
            "suggested_departments": [
                "Ministry of Labour and Employment",
                "Department of Employment",
                "Skill Development Authority"
            ],
            "guidance": "You may request details about jobs, recruitment, or employment schemes."
        },
        "hi": {
            "name": "रोजगार सूचना अनुरोध",
            "common_questions": [
                "सरकारी नौकरी रिक्तियां",
                "भर्ती प्रक्रिया का विवरण",
                "कौशल विकास योजनाएं"
            ],
            "suggested_departments": [
                "श्रम और रोजगार मंत्रालय",
                "रोजगार विभाग",
                "कौशल विकास प्राधिकरण"
            ],
            "guidance": "आप नौकरी, भर्ती या रोजगार योजनाओं के बारे में जानकारी मांग सकते हैं।"
        },
        "kn": {
            "name": "ಉದ್ಯೋಗ ಮಾಹಿತಿ ವಿನಂತಿ",
            "common_questions": [
                "ಸರ್ಕಾರಿ ಉದ್ಯೋಗ ಖಾಲಿ ಹುದ್ದೆಗಳು",
                "ನೇಮಕಾತಿ ಪ್ರಕ್ರಿಯೆಯ ವಿವರಗಳು",
                "ಕೌಶಲ್ಯ ಅಭಿವೃದ್ಧಿ ಯೋಜನೆಗಳು"
            ],
            "suggested_departments": [
                "ಕಾರ್ಮಿಕ ಮತ್ತು ಉದ್ಯೋಗ ಸಚಿವಾಲಯ",
                "ಉದ್ಯೋಗ ಇಲಾಖೆ",
                "ಕೌಶಲ್ಯ ಅಭಿವೃದ್ಧಿ ಪ್ರಾಧಿಕಾರ"
            ],
            "guidance": "ನೀವು ಉದ್ಯೋಗ, ನೇಮಕಾತಿ ಅಥವಾ ಉದ್ಯೋಗ ಯೋಜನೆಗಳ ಬಗ್ಗೆ ಮಾಹಿತಿ ಕೇಳಬಹುದು."
        }
    },

    # =========================
    # GENERAL
    # =========================
    "general": {
        "en": {
            "name": "General Information Request",
            "common_questions": [],
            "suggested_departments": [],
            "guidance": "Please specify which department the information relates to."
        },
        "hi": {
            "name": "सामान्य सूचना अनुरोध",
            "common_questions": [],
            "suggested_departments": [],
            "guidance": "कृपया बताएं कि यह जानकारी किस विभाग से संबंधित है।"
        },
        "kn": {
            "name": "ಸಾಮಾನ್ಯ ಮಾಹಿತಿ ವಿನಂತಿ",
            "common_questions": [],
            "suggested_departments": [],
            "guidance": "ದಯವಿಟ್ಟು ಈ ಮಾಹಿತಿ ಯಾವ ಇಲಾಖೆಗೆ ಸಂಬಂಧಿಸಿದೆ ಎಂದು ತಿಳಿಸಿ."
        }
    }
}


def get_template(category: str, language: str = "en") -> dict:
    """Get RTI template for a category and language"""
    template = RTI_TEMPLATES.get(category, RTI_TEMPLATES["general"])
    return template.get(language, template.get("en", {}))


def detect_category(text: str) -> str:
    """Detect RTI category from user text"""
    text_lower = text.lower()
    
    # Education keywords
    if any(word in text_lower for word in ["education", "school", "college", "university", "teacher", "student", "scholarship", "शिक्षा", "स्कूल", "ಶಿಕ್ಷಣ"]):
        return "education"
    
    # Health keywords
    if any(word in text_lower for word in ["health", "hospital", "doctor", "medicine", "medical", "treatment", "स्वास्थ्य", "अस्पताल", "ಆರೋಗ್ಯ"]):
        return "health"
    
    # Transport keywords
    if any(word in text_lower for word in ["road", "transport", "bus", "traffic", "highway", "vehicle", "सड़क", "परिवहन", "ರಸ್ತೆ"]):
        return "transport"
    
    # Employment keywords
    if any(word in text_lower for word in ["job", "employment", "recruitment", "vacancy", "work", "रोजगार", "नौकरी", "ಉದ್ಯೋಗ"]):
        return "employment"
    
    # Welfare keywords
    if any(word in text_lower for word in ["pension", "welfare", "housing", "ration", "subsidy", "पेंशन", "कल्याण", "ಪಿಂಚಣಿ"]):
        return "welfare"
    
    # Environment keywords
    if any(word in text_lower for word in ["environment", "pollution", "forest", "tree", "waste", "पर्यावरण", "प्रदूषण", "ಪರಿಸರ"]):
        return "environment"
    
    return "general"


def get_suggested_questions(category: str, language: str = "en") -> list:
    """Get suggested questions for a category"""
    template = get_template(category, language)
    return template.get("common_questions", [])


def get_suggested_departments(category: str, language: str = "en") -> list:
    """Get suggested departments for a category"""
    template = get_template(category, language)
    return template.get("suggested_departments", [])


def get_guidance(category: str, language: str = "en") -> str:
    """Get guidance text for a category"""
    template = get_template(category, language)
    return template.get("guidance", "")


# Example usage
if __name__ == "__main__":
    # Test category detection
    test_texts = [
        "I want to know about government spending on education",
        "मैं स्वास्थ्य योजनाओं के बारे में जानना चाहता हूं",
        "ನಾನು ರಸ್ತೆ ನಿರ್ಮಾಣದ ಬಗ್ಗೆ ತಿಳಿಯಲು ಬಯಸುತ್ತೇನೆ"
    ]
    
    for text in test_texts:
        category = detect_category(text)
        print(f"\nText: {text}")
        print(f"Category: {category}")
        print(f"Suggested departments: {get_suggested_departments(category)}")
