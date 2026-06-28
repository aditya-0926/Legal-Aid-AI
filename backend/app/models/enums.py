from enum import Enum


class LegalDomain(str, Enum):
    CONSTITUTION = "constitution"
    CRIMINAL_LAW = "criminal_law"
    CRIMINAL_PROCEDURE = "criminal_procedure"
    EVIDENCE = "evidence"
    TENANT_RIGHTS = "tenant_rights"
    LABOR_LAW = "labor_law"
    DOMESTIC_VIOLENCE = "domestic_violence"
    RTI = "rti"
    CONSUMER_RIGHTS = "consumer_rights"
    POLICE_MISCONDUCT = "police_misconduct"
    PROPERTY_DISPUTE = "property_dispute"
    FAMILY_LAW = "family_law"
    MOTOR_VEHICLES = "motor_vehicles"
    IT_LAW = "it_law"
    ENVIRONMENTAL = "environmental"
    GENERAL = "general"


class Language(str, Enum):
    ENGLISH = "en"
    HINDI = "hi"
    MARATHI = "mr"


class EmbeddingProvider(str, Enum):
    SENTENCE_TRANSFORMERS = "sentence_transformers"
    BAAI_BGE = "baai_bge"
