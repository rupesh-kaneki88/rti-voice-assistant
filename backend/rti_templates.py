"""
RTI Application Templates for Common Requests
These templates help the agent guide users through common RTI scenarios
"""

RTI_TEMPLATES = {
    "education": {
        "en": {
            "name": "Education Information Request",
            "common_questions": [
                "Details of government spending on education in my district",
                "Information about scholarship schemes and eligibility",
                "Details of school infrastructure development projects",
                "Teacher recruitment and vacancy information",
                "Mid-day meal scheme implementation details"
            ],
            "suggested_departments": [
                "Ministry of Education",
                "Department of School Education",
                "University Grants Commission"
            ],
            "guidance": "For education-related information, you can request details about spending, schemes, infrastructure, or policies."
        },
        "hi": {
            "name": "शिक्षा सूचना अनुरोध",
            "common_questions": [
                "मेरे जिले में शिक्षा पर सरकारी खर्च का विवरण",
                "छात्रवृत्ति योजनाओं और पात्रता के बारे में जानकारी",
                "स्कूल बुनियादी ढांचा विकास परियोजनाओं का विवरण"
            ],
            "suggested_departments": [
                "शिक्षा मंत्रालय",
                "स्कूल शिक्षा विभाग"
            ]
        },
        "kn": {
            "name": "ಶಿಕ್ಷಣ ಮಾಹಿತಿ ವಿನಂತಿ",
            "common_questions": [
                "ನನ್ನ ಜಿಲ್ಲೆಯಲ್ಲಿ ಶಿಕ್ಷಣದ ಮೇಲೆ ಸರ್ಕಾರದ ಖರ್ಚಿನ ವಿವರಗಳು",
                "ವಿದ್ಯಾರ್ಥಿವೇತನ ಯೋಜನೆಗಳು ಮತ್ತು ಅರ್ಹತೆಯ ಬಗ್ಗೆ ಮಾಹಿತಿ"
            ],
            "suggested_departments": [
                "ಶಿಕ್ಷಣ ಸಚಿವಾಲಯ"
            ]
        }
    },
    
    "health": {
        "en": {
            "name": "Health Information Request",
            "common_questions": [
                "Details of government health schemes in my area",
                "Information about hospital infrastructure and facilities",
                "Medicine procurement and distribution details",
                "Health worker recruitment and deployment information",
                "COVID-19 vaccination and treatment expenditure"
            ],
            "suggested_departments": [
                "Ministry of Health and Family Welfare",
                "Department of Health Services",
                "National Health Mission"
            ],
            "guidance": "For health-related information, you can request details about schemes, hospitals, medicines, or health programs."
        }
    },
    
    "transport": {
        "en": {
            "name": "Transport Information Request",
            "common_questions": [
                "Details of road construction projects in my area",
                "Information about public transport schemes and subsidies",
                "Traffic management and road safety measures",
                "Vehicle registration and licensing procedures",
                "Details of transport infrastructure development"
            ],
            "suggested_departments": [
                "Ministry of Road Transport and Highways",
                "Department of Transport",
                "National Highways Authority"
            ],
            "guidance": "For transport-related information, you can request details about roads, public transport, or vehicle services."
        }
    },
    
    "employment": {
        "en": {
            "name": "Employment Information Request",
            "common_questions": [
                "Details of government job vacancies and recruitment",
                "Information about employment schemes and programs",
                "Skill development and training initiatives",
                "Unemployment allowance and benefits",
                "Details of government contractor payments"
            ],
            "suggested_departments": [
                "Ministry of Labour and Employment",
                "Department of Employment",
                "Skill Development Authority"
            ],
            "guidance": "For employment-related information, you can request details about jobs, schemes, or training programs."
        }
    },
    
    "welfare": {
        "en": {
            "name": "Social Welfare Information Request",
            "common_questions": [
                "Details of pension schemes and beneficiaries",
                "Information about housing schemes and allotments",
                "Ration card and food subsidy details",
                "Disability benefits and support programs",
                "Details of welfare scheme implementation"
            ],
            "suggested_departments": [
                "Ministry of Social Justice and Empowerment",
                "Department of Social Welfare",
                "Food and Civil Supplies Department"
            ],
            "guidance": "For welfare-related information, you can request details about pensions, housing, food subsidies, or support programs."
        }
    },
    
    "environment": {
        "en": {
            "name": "Environment Information Request",
            "common_questions": [
                "Details of environmental clearances granted",
                "Information about pollution control measures",
                "Forest conservation and tree plantation details",
                "Waste management and sanitation projects",
                "Details of environmental impact assessments"
            ],
            "suggested_departments": [
                "Ministry of Environment, Forest and Climate Change",
                "State Pollution Control Board",
                "Forest Department"
            ],
            "guidance": "For environment-related information, you can request details about clearances, pollution control, or conservation."
        }
    }
}


def get_template(category: str, language: str = "en") -> dict:
    """Get RTI template for a category and language"""
    template = RTI_TEMPLATES.get(category, {})
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
