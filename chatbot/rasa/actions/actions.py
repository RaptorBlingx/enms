from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import random
import re
import json
import os
from difflib import SequenceMatcher
from collections import Counter

# Q&A verisini yükle
QA_DATA = {}
QA_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'qa_data.json')
if os.path.exists(QA_DATA_PATH):
    with open(QA_DATA_PATH, 'r', encoding='utf-8') as f:
        qa_data_raw = json.load(f)
        # Veriyi düzleştir: her intent için question->answer mapping
        for intent, qa_pairs in qa_data_raw.items():
            QA_DATA[intent] = {}
            for qa_pair in qa_pairs:
                if isinstance(qa_pair, list) and len(qa_pair) >= 2:
                    question = qa_pair[0].strip()
                    answer = qa_pair[1].strip().replace('\n', ' ').strip()
                    if question and answer:
                        QA_DATA[intent][question.lower()] = answer


class ActionRetrieveAnswer(Action):
    """Custom action to retrieve the most appropriate answer based on user's question."""
    
    def name(self) -> Text:
        return "action_retrieve_answer"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the latest user message
        latest_message = tracker.latest_message
        user_message = latest_message.get("text", "")
        user_message_lower = user_message.lower()
        intent = latest_message.get("intent", {}).get("name", "")
        
        # Anahtar kelime mapping - hangi kelimeler hangi alt konuya ait
        keyword_to_topic = {
            # DEFINITION topics
            "baseline": "ask_energy_baseline",
            "energy baseline": "ask_energy_baseline",
            "enpi": "ask_enpi",
            "enpis": "ask_enpi",
            "energy performance indicator": "ask_enpi",
            "significant energy use": "ask_significant_energy_use",
            "seu": "ask_significant_energy_use",
            "energy review": "ask_energy_review",
            "scope": "ask_scope",
            "boundary": "ask_scope",
            "terms": "ask_terms_definitions",
            "definitions": "ask_definitions",
            "define": "ask_definitions",
            "meaning": "ask_definitions",
            "exactly is meant by": "ask_terms_definitions",
            "what exactly is meant": "ask_terms_definitions",
            
            # PURPOSE topics
            "pdca": "ask_pdca",
            "plan do check act": "ask_pdca",
            "benchmarking": "ask_benchmarking",
            "iso": "ask_iso_standards",
            "iso 50001": "ask_iso_standards",
            "international standard": "ask_iso_standards",
            "this international standard": "ask_iso_standards",
            "primary objective": "ask_iso_standards",
            "for what purposes": "ask_iso_standards",
            "standard": "ask_iso_standards",
            "general": "ask_general_info",
            
            # PROCESS topics
            "planning": "ask_energy_planning",
            "energy planning": "ask_energy_planning",
            "implementation": "ask_implementation",
            "checking": "ask_checking",
            "monitoring": "ask_monitoring_measurement",
            "measurement": "ask_monitoring_measurement",
            "audit": "ask_internal_audit",
            "internal audit": "ask_internal_audit",
            "management review": "ask_management_review",
            "corrective": "ask_corrective_preventive_action",
            "preventive": "ask_corrective_preventive_action",
            "action plan": "ask_action_plans",
            "action plans": "ask_action_plans",
            "objectives": "ask_objectives_targets",
            "targets": "ask_objectives_targets",
            "operational control": "ask_operational_control",
            "design": "ask_design",
            "procurement": "ask_procurement",
            "communication": "ask_communication",
            "competence": "ask_competence_training",
            "training": "ask_competence_training",
            "documentation": "ask_documentation",
            "records": "ask_records",
            
            # REQUIREMENT topics
            "policy": "ask_energy_policy",
            "energy policy": "ask_energy_policy",
            "legal": "ask_legal_requirements",
            "legal requirements": "ask_legal_requirements",
            "compliance": "ask_compliance",
            "management responsibility": "ask_management_responsibility",
            "top management": "ask_management_responsibility",
        }
        
        # If intent is not in new structure, use default utter action
        if intent not in ["definition", "purpose", "process", "requirement"]:
            # For non-ask intents, use the standard utter action
            if intent in ["greet", "goodbye", "thank", "affirm", "deny"]:
                dispatcher.utter_message(response=f"utter_{intent}")
            return []
        
        # Anahtar kelimelerle alt konuyu belirle
        # Önce uzun keyword'leri kontrol et (daha spesifik olanlar öncelikli)
        topic = None
        best_match_length = 0
        
        # Keyword'leri uzunluklarına göre sırala (uzun olanlar önce - daha spesifik)
        sorted_keywords = sorted(keyword_to_topic.items(), key=lambda x: len(x[0]), reverse=True)
        
        for keyword, topic_name in sorted_keywords:
            # Regex ile kelime sınırlarını kontrol et (daha doğru eşleşme)
            # \b kelime sınırı, (?i) case-insensitive
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, user_message_lower, re.IGNORECASE):
                # Uzun keyword'ler daha yüksek öncelik alır
                if len(keyword) > best_match_length:
                    best_match_length = len(keyword)
                    topic = topic_name
                    # En uzun eşleşmeyi bulduk, devam et (daha uzun olabilir)
        
        # Eğer regex ile bulunamazsa, basit substring kontrolü yap (fallback)
        if not topic:
            for keyword, topic_name in sorted_keywords:
                if keyword in user_message_lower:
                    topic = topic_name
                    break
        
        # Özel durumlar: "international standard" içeren sorular
        if not topic or topic == "ask_terms_definitions":
            if 'international standard' in user_message_lower or 'this international standard' in user_message_lower:
                if 'primary objective' in user_message_lower or 'objective' in user_message_lower:
                    topic = "ask_iso_standards"
                elif 'for what purposes' in user_message_lower or 'what purposes' in user_message_lower:
                    topic = "ask_iso_standards"
                elif 'to what variables' in user_message_lower or ('variables' in user_message_lower and 'applicable' in user_message_lower):
                    topic = "ask_scope"
                elif topic != "ask_iso_standards" and topic != "ask_scope":
                    topic = "ask_iso_standards"
        
        # Eğer topic bulunamazsa, intent'e göre genel bir topic seç
        if not topic:
            if intent == "definition":
                topic = "ask_definitions"
            elif intent == "purpose":
                # Purpose intent'i için daha spesifik kontrol
                if any(term in user_message_lower for term in ['iso', 'standard', 'international standard']):
                    topic = "ask_iso_standards"
                elif any(term in user_message_lower for term in ['scope', 'boundary']):
                    topic = "ask_scope"
                elif any(term in user_message_lower for term in ['benchmark']):
                    topic = "ask_benchmarking"
                elif any(term in user_message_lower for term in ['pdca', 'plan do check act']):
                    topic = "ask_pdca"
                else:
                    topic = "ask_general_info"
            elif intent == "process":
                # Process intent'inde scope/boundary soruları da var
                if any(term in user_message_lower for term in ['scope', 'boundary', 'boundaries']):
                    # Scope soruları process intent'inde, topic'i ask_scope olarak işaretle
                    # ama arama process intent'inde yapılacak
                    topic = "ask_scope"
                else:
                    topic = "ask_energy_planning"
            elif intent == "requirement":
                topic = "ask_energy_policy"
        
        # ÖNEMLİ: Scope/boundary soruları process intent'inde olduğu için özel kontrol
        # Intent definition olsa bile, scope soruları process intent'inde
        scope_keywords = ['scope', 'boundary', 'boundaries']
        user_has_scope = any(keyword in user_message_lower for keyword in scope_keywords)
        
        # Process intent için önce QA_DATA["process"]'e bak
        if intent == "process" and "process" in QA_DATA and QA_DATA["process"]:
            best_answer = self._find_best_answer(user_message_lower, QA_DATA["process"])
            if best_answer:
                dispatcher.utter_message(text=best_answer)
                return []
        
        # Scope soruları için özel kontrol: Intent definition olsa bile process'te ara
        if user_has_scope and "process" in QA_DATA and QA_DATA["process"]:
            best_answer = self._find_best_answer(user_message_lower, QA_DATA["process"])
            if best_answer:
                dispatcher.utter_message(text=best_answer)
                return []
        
        # Topic'e göre Q&A verisinde ara (process intent değilse veya process'te bulunamadıysa)
        # ÖNEMLİ: Scope soruları process intent'inde olduğu için, ask_scope topic'ine bakma
        # sadece process intent'i değilse ve scope keyword'ü yoksa bak
        if topic and topic in QA_DATA and QA_DATA[topic]:
            # Scope soruları process intent'inde, o yüzden ask_scope topic'ine bakma
            if topic == "ask_scope" and (intent == "process" or user_has_scope):
                # Zaten process intent'inde aradık, bulamadık, o yüzden domain response'a geç
                pass
            else:
                best_answer = self._find_best_answer(user_message_lower, QA_DATA[topic])
                if best_answer:
                    dispatcher.utter_message(text=best_answer)
                    return []
        
        # Q&A verisinde bulunamazsa, domain'deki response'ları kullan
        topic_to_response = {
            "ask_energy_baseline": "utter_ask_energy_baseline",
            "ask_enpi": "utter_ask_enpi",
            "ask_significant_energy_use": "utter_ask_significant_energy_use",
            "ask_energy_review": "utter_ask_energy_review",
            "ask_scope": "utter_ask_scope",
            "ask_terms_definitions": "utter_ask_terms_definitions",
            "ask_definitions": "utter_ask_definitions",
            "ask_pdca": "utter_ask_pdca",
            "ask_benchmarking": "utter_ask_benchmarking",
            "ask_iso_standards": "utter_ask_iso_standards",
            "ask_general_info": "utter_ask_general_info",
            "ask_energy_planning": "utter_ask_energy_planning",
            "ask_implementation": "utter_ask_implementation",
            "ask_checking": "utter_ask_checking",
            "ask_monitoring_measurement": "utter_ask_monitoring_measurement",
            "ask_internal_audit": "utter_ask_internal_audit",
            "ask_management_review": "utter_ask_management_review",
            "ask_corrective_preventive_action": "utter_ask_corrective_preventive_action",
            "ask_action_plans": "utter_ask_action_plans",
            "ask_objectives_targets": "utter_ask_objectives_targets",
            "ask_operational_control": "utter_ask_operational_control",
            "ask_design": "utter_ask_design",
            "ask_procurement": "utter_ask_procurement",
            "ask_communication": "utter_ask_communication",
            "ask_competence_training": "utter_ask_competence_training",
            "ask_documentation": "utter_ask_documentation",
            "ask_records": "utter_ask_records",
            "ask_energy_policy": "utter_ask_energy_policy",
            "ask_legal_requirements": "utter_ask_legal_requirements",
            "ask_compliance": "utter_ask_compliance",
            "ask_management_responsibility": "utter_ask_management_responsibility",
        }
        
        response_key = topic_to_response.get(topic, f"utter_ask_general_info")
        responses = domain.get("responses", {}).get(response_key, [])
        
        if not responses:
            # Fallback: use the standard utter action
            dispatcher.utter_message(response=response_key)
            return []
        
        # Select the most appropriate response based on keywords in user message
        selected_response = self._select_best_response(user_message_lower, responses, topic or intent)
        
        # Send the selected response
        dispatcher.utter_message(text=selected_response)
        
        return []
    
    def _extract_keywords(self, text: str) -> set:
        """Extract important keywords from text, filtering out stop words."""
        # Stop words listesi
        stop_words = {
            'what', 'is', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'from', 'as', 'are', 'was', 'were', 'been', 'be', 'have', 'has', 
            'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might', 'must',
            'can', 'this', 'that', 'these', 'those', 'it', 'its', 'they', 'them', 'their', 'there',
            'when', 'where', 'why', 'how', 'which', 'who', 'whom', 'whose', 'about', 'into', 'onto',
            'if', 'then', 'than', 'so', 'such', 'more', 'most', 'very', 'just', 'only', 'also',
            'must', 'shall', 'should', 'may', 'might', 'can', 'could', 'will', 'would'
        }
        
        # Metni temizle ve kelimelere ayır
        words = re.findall(r'\b[a-z]+\b', text.lower())
        # Stop words'leri filtrele ve 2+ harfli kelimeleri al
        keywords = {w for w in words if w not in stop_words and len(w) > 2}
        return keywords
    
    def _calculate_question_type_score(self, user_q: str, db_q: str) -> float:
        """Calculate score based on question type matching (what, how, when, etc.)."""
        question_words = {'what', 'how', 'when', 'where', 'why', 'who', 'which', 'whom', 'whose'}
        
        user_q_words = set(re.findall(r'\b\w+\b', user_q.lower()))
        db_q_words = set(re.findall(r'\b\w+\b', db_q.lower()))
        
        user_q_type = user_q_words & question_words
        db_q_type = db_q_words & question_words
        
        if user_q_type and db_q_type:
            if user_q_type == db_q_type:
                return 0.2  # Aynı soru tipi bonusu
        return 0.0
    
    def _calculate_keyword_score(self, user_keywords: set, question_keywords: set, 
                                 user_message: str, question: str) -> float:
        """Calculate keyword-based similarity score with weighted importance."""
        if not user_keywords or not question_keywords:
            return 0.0
        
        # Ortak kelimeler
        common = user_keywords & question_keywords
        if not common:
            return 0.0
        
        # Önemli terimler (daha uzun kelimeler ve teknik terimler)
        important_terms = {
            'energy', 'management', 'system', 'performance', 'baseline', 'enpi', 'enpis',
            'objective', 'target', 'action', 'plan', 'review', 'audit', 'policy', 'requirement',
            'significant', 'consumption', 'efficiency', 'improvement', 'continual', 'organization',
            'monitoring', 'measurement', 'compliance', 'legal', 'documentation', 'record',
            'corrective', 'preventive', 'nonconformity', 'procurement', 'design', 'operational',
            'control', 'communication', 'competence', 'training', 'awareness', 'scope', 'boundary'
        }
        
        # Jaccard similarity
        union = user_keywords | question_keywords
        jaccard = len(common) / len(union) if union else 0.0
        
        # Önemli terimler için bonus
        important_matches = common & important_terms
        important_bonus = len(important_matches) * 0.1
        
        # Kelime sırası benzerliği (bigram)
        user_bigrams = set(zip(user_message.split()[:-1], user_message.split()[1:]))
        question_bigrams = set(zip(question.split()[:-1], question.split()[1:]))
        if user_bigrams and question_bigrams:
            bigram_overlap = len(user_bigrams & question_bigrams) / len(user_bigrams | question_bigrams)
            jaccard = max(jaccard, bigram_overlap * 0.7)
        
        return min(jaccard + important_bonus, 1.0)
    
    def _calculate_specificity_bonus(self, user_message: str, question: str) -> float:
        """Calculate bonus for specific question types and patterns."""
        bonus = 0.0
        
        # Soru başlangıcı eşleşmesi - ÇOK ÖNEMLİ
        user_start_words = user_message.split()[:5]  # İlk 5 kelime
        question_start_words = question.split()[:5]
        if len(user_start_words) >= 3 and len(question_start_words) >= 3:
            # İlk 3 kelime eşleşiyorsa büyük bonus
            if user_start_words[:3] == question_start_words[:3]:
                bonus += 0.4
            elif user_start_words[:2] == question_start_words[:2]:
                bonus += 0.3
            elif user_start_words[0] == question_start_words[0]:
                bonus += 0.15
        
        # "What is X?" gibi genel sorular için definition sorularına öncelik
        if re.match(r'^what is\s+\w+', user_message):
            if 'definition' in question or 'define' in question or 'fundamental' in question:
                bonus += 0.3
            if 'what is' in question and 'definition' in question:
                bonus += 0.2
        
        # "What is the primary objective" gibi spesifik sorular
        if 'primary objective' in user_message:
            if 'primary objective' in question:
                bonus += 0.5  # Çok yüksek bonus
            elif 'objective' in question:
                bonus += 0.2
        
        # "To what variables" gibi spesifik sorular
        if 'variables' in user_message and 'applicable' in user_message:
            if 'variables' in question and 'applicable' in question:
                bonus += 0.5
            elif 'variables' in question:
                bonus += 0.3
        
        # "For what purposes" gibi spesifik sorular
        if 'for what purposes' in user_message or 'what purposes' in user_message:
            if 'purposes' in question:
                bonus += 0.4
        
        # "What must X include?" gibi sorular için "include" içeren sorulara öncelik
        if 'must' in user_message and 'include' in user_message:
            if 'include' in question:
                bonus += 0.25
                # Aynı zamanda "must" varsa ekstra bonus
                if 'must' in question:
                    bonus += 0.15
        
        # "How" soruları için "how" içeren sorulara öncelik
        if user_message.startswith('how'):
            if question.startswith('how'):
                bonus += 0.2
        
        # "When" soruları için "when" içeren sorulara öncelik
        if user_message.startswith('when'):
            if question.startswith('when'):
                bonus += 0.2
        
        # "Define" veya "Explain" ile başlayan sorular
        if user_message.startswith('define') or user_message.startswith('explain'):
            if question.startswith('define') or question.startswith('explain'):
                bonus += 0.3
        
        # Kullanıcı sorusundaki anahtar terimler soruda geçiyorsa bonus
        user_important_terms = {'definition', 'purpose', 'requirement', 'must', 'shall', 
                               'include', 'establish', 'maintain', 'implement', 'objective',
                               'variables', 'applicable', 'purposes', 'scope', 'boundary'}
        user_terms_in_msg = {term for term in user_important_terms if term in user_message}
        question_terms = {term for term in user_important_terms if term in question}
        if user_terms_in_msg and question_terms:
            common_important = user_terms_in_msg & question_terms
            bonus += len(common_important) * 0.15  # Artırıldı
        
        return min(bonus, 0.8)  # Maksimum 0.8 bonus (artırıldı)
    
    def _find_best_answer(self, user_message: str, qa_dict: Dict[str, str]) -> str:
        """Find the best matching answer using improved similarity matching."""
        if not qa_dict:
            return None
        
        # Önce tam eşleşme ara
        if user_message in qa_dict:
            return qa_dict[user_message]
        
        # Kullanıcı mesajından anahtar kelimeleri çıkar
        user_keywords = self._extract_keywords(user_message)
        
        # Her soru için skor hesapla
        scored_questions = []
        
        for question, answer in qa_dict.items():
            score = 0.0
            
            # 1. Tam metin benzerliği (SequenceMatcher) - daha yüksek ağırlık
            text_similarity = SequenceMatcher(None, user_message, question).ratio()
            score += text_similarity * 0.6  # Daha da artırıldı
            
            # 2. Soru tipi eşleşmesi
            question_type_score = self._calculate_question_type_score(user_message, question)
            score += question_type_score
            
            # 3. Anahtar kelime benzerliği
            question_keywords = self._extract_keywords(question)
            keyword_score = self._calculate_keyword_score(user_keywords, question_keywords, 
                                                         user_message, question)
            score += keyword_score * 0.5  # Artırıldı
            
            # 4. Spesifiklik bonusu
            specificity_bonus = self._calculate_specificity_bonus(user_message, question)
            score += specificity_bonus
            
            # 5. Özel terim eşleşmesi (tam eşleşme bonusu) - ÖNEMLİ
            user_terms = set(re.findall(r'\b[a-z]+\b', user_message.lower()))
            question_terms = set(re.findall(r'\b[a-z]+\b', question.lower()))
            exact_term_matches = user_terms & question_terms
            
            # Önemli terimler (daha yüksek ağırlık)
            important_terms = {
                'iso', 'standard', 'scope', 'boundary', 'benchmark', 'pdca', 'audit',
                'energy', 'performance', 'baseline', 'enpi', 'policy', 'planning',
                'management', 'review', 'implementation', 'checking', 'objective', 'target',
                'efficiency', 'consumption', 'continual', 'improvement', 'corrective', 'preventive'
            }
            important_matches = exact_term_matches & important_terms
            
            # Kullanıcı sorusundaki önemli terimler soruda varsa büyük bonus
            if len(important_matches) >= 2:
                score += 0.3  # Artırıldı
            elif len(important_matches) >= 1:
                score += 0.2  # Artırıldı
            
            # Spesifik terim eşleşmesi - çok önemli (örn: "energy efficiency" hem soruda hem cevapta)
            specific_phrases = ['energy efficiency', 'energy baseline', 'energy performance', 'continual improvement',
                              'corrective action', 'preventive action', 'energy review', 'energy policy',
                              'energy objective', 'energy target', 'significant energy use', 'energy consumption',
                              'exactly is meant by energy', 'what exactly is meant by', 'exactly is meant by',
                              'scope', 'boundary', 'boundaries', 'scope and boundary', 'scope and boundaries']
            for phrase in specific_phrases:
                if phrase in user_message.lower() and phrase in question.lower():
                    score += 0.5  # Çok yüksek bonus
                    break
            
            # Scope/boundary soruları için özel bonus - ÇOK ÖNEMLİ
            scope_keywords = ['scope', 'boundary', 'boundaries']
            user_has_scope = any(keyword in user_message.lower() for keyword in scope_keywords)
            question_has_scope = any(keyword in question.lower() for keyword in scope_keywords)
            if user_has_scope and question_has_scope:
                # Her iki tarafta da scope/boundary varsa büyük bonus
                score += 0.4  # Scope soruları için özel bonus
                # Eğer aynı scope keyword'ü varsa ekstra bonus
                for keyword in scope_keywords:
                    if keyword in user_message.lower() and keyword in question.lower():
                        score += 0.2
                        break
            
            # Tam ifade eşleşmesi - en yüksek öncelik
            # Kullanıcı sorusundaki önemli ifadeler soruda tam olarak geçiyorsa
            user_important_phrases = []
            if 'exactly is meant by' in user_message.lower():
                user_important_phrases.append('exactly is meant by')
            if 'what is' in user_message.lower()[:10]:
                user_important_phrases.append('what is')
            if 'define' in user_message.lower()[:10]:
                user_important_phrases.append('define')
            if 'explain' in user_message.lower()[:10]:
                user_important_phrases.append('explain')
            
            for phrase in user_important_phrases:
                if phrase in question.lower():
                    score += 0.3
                    break
            
            # Genel terim eşleşmesi
            if len(exact_term_matches) >= len(user_terms) * 0.7:  # %70+ eşleşme (artırıldı)
                score += 0.25  # Artırıldı
            elif len(exact_term_matches) >= len(user_terms) * 0.5:  # %50+ eşleşme
                score += 0.18
            elif len(exact_term_matches) >= 4:  # En az 4 terim eşleşmesi
                score += 0.12
            
            # 6. Soru başlangıcı benzerliği (ilk birkaç kelime) - ÇOK ÖNEMLİ
            user_words = user_message.split()
            question_words = question.split()
            
            # İlk 3-6 kelimeyi karşılaştır
            for i in range(3, 7):
                if len(user_words) >= i and len(question_words) >= i:
                    user_start = ' '.join(user_words[:i])
                    question_start = ' '.join(question_words[:i])
                    if user_start.lower() == question_start.lower():
                        score += 0.5 / (i - 2)  # İlk kelimeler çok daha önemli
                        break
                    elif user_start.lower() in question_start.lower() or question_start.lower() in user_start.lower():
                        score += 0.25 / (i - 2)
                        break
            
            # İlk kelime eşleşmesi - ekstra bonus
            if len(user_words) > 0 and len(question_words) > 0:
                if user_words[0].lower() == question_words[0].lower():
                    score += 0.2
            
            # 7. Soru uzunluğu benzerliği
            length_ratio = min(len(user_message), len(question)) / max(len(user_message), len(question))
            if length_ratio > 0.7:  # 0.6'dan 0.7'ye çıkarıldı
                score += 0.05
            
            # 8. Soru ortası ve sonu benzerliği (yeni)
            user_words = user_message.split()
            question_words = question.split()
            if len(user_words) > 4 and len(question_words) > 4:
                # Ortadaki kelimeleri kontrol et
                user_middle = ' '.join(user_words[2:-2])
                question_middle = ' '.join(question_words[2:-2])
                if user_middle and question_middle:
                    middle_similarity = SequenceMatcher(None, user_middle.lower(), question_middle.lower()).ratio()
                    if middle_similarity > 0.5:
                        score += middle_similarity * 0.15
            
            scored_questions.append((score, question, answer))
        
        # En yüksek skorlu soruları sırala
        scored_questions.sort(reverse=True, key=lambda x: x[0])
        
        if scored_questions:
            best_score, best_question, best_answer = scored_questions[0]
            
            # Minimum eşik değeri - dinamik olarak ayarla
            # Scope/boundary soruları için daha düşük eşik
            scope_keywords = ['scope', 'boundary', 'boundaries']
            user_has_scope = any(keyword in user_message.lower() for keyword in scope_keywords)
            question_has_scope = any(keyword in best_question.lower() for keyword in scope_keywords)
            
            # Eğer soru başlangıcı çok benziyorsa eşiği düşür
            user_start = ' '.join(user_message.split()[:3])
            question_start = ' '.join(best_question.split()[:3])
            threshold = 0.25
            
            # Scope soruları için eşiği düşür
            if user_has_scope or question_has_scope:
                threshold = 0.20  # Scope soruları için daha düşük eşik
                if user_has_scope and question_has_scope:
                    threshold = 0.15  # Her iki tarafta da scope varsa daha da düşük
            
            if user_start.lower() == question_start.lower():
                threshold = min(threshold, 0.15)  # Soru başlangıcı aynıysa eşiği düşür
            elif user_start.lower() in question_start.lower() or question_start.lower() in user_start.lower():
                threshold = min(threshold, 0.20)
            
            if best_score >= threshold:
                # Daha kapsamlı cevap için: yüksek skorlu birden fazla sorunun cevabını birleştir
                # Ana cevabın sonunda nokta olduğundan emin ol
                comprehensive_answer = best_answer.strip()
                if comprehensive_answer and not comprehensive_answer.endswith('.'):
                    comprehensive_answer += '.'
                
                # Top 3-5 sorudan benzer olanları birleştir
                additional_answers = []
                for i in range(1, min(5, len(scored_questions))):
                    score, question, answer = scored_questions[i]
                    
                    # Sadece yeterince yüksek skorlu ve farklı cevapları ekle
                    # En az threshold*0.7 skora sahip olmalı ve cevap farklı olmalı
                    if score >= threshold * 0.7:
                        # Cevabı temizle ve normalize et
                        answer_clean = answer.strip()
                        answer_normalized = answer_clean.lower()
                        best_answer_normalized = best_answer.lower().strip()
                        
                        # Eğer cevap tamamen farklıysa ve çok benzer değilse ekle
                        if answer_normalized != best_answer_normalized:
                            # Cevapların benzerlik oranını kontrol et
                            similarity = SequenceMatcher(None, answer_normalized, best_answer_normalized).ratio()
                            
                            # %70'den az benzer ve yeterince farklıysa ekle (eşik düşürüldü)
                            if similarity < 0.70:
                                # Çok kısa cevapları ekleme (5 kelimeden az)
                                if len(answer_clean.split()) >= 5:
                                    # Cevabın tam olduğundan emin ol
                                    if not answer_clean.endswith('.'):
                                        answer_clean += '.'
                                    additional_answers.append(answer_clean)
                    else:
                        break  # Skorlar çok düştüyse durdur
                
                # Ek cevaplar varsa birleştir
                if additional_answers:
                    # İlk cevabı ana cevap olarak kullan
                    # Diğer cevapları doğrudan ekle (nokta ile ayrılmış)
                    for additional in additional_answers[:2]:  # Maksimum 2 ek cevap
                        # Cevabı doğrudan ekle (her cevap zaten nokta ile bitiyor)
                        comprehensive_answer += f" {additional}"
                
                return comprehensive_answer
        
        return None
    
    def _select_best_response(self, user_message: str, responses: List[Dict], intent: str) -> str:
        """Select the best response based on keywords in the user's question."""
        
        # Keyword mappings: keywords that indicate which response index to prefer
        keyword_mappings = {
            "ask_management_responsibility": {
                0: ["resources", "commitment", "fundamental", "specific resources", "provide", "human", "skills", "technology", "financial"],
                1: ["representative", "management representative", "responsibilities", "team", "composition", "size", "report", "two key areas", "appointing"],
            },
            "ask_energy_policy": {
                0: ["three primary", "commitments", "continual improvement", "resources", "compliance", "legal requirements", "documented", "communicated"],
                1: ["framework", "setting goals", "reviewing", "objectives", "targets", "purchase", "procurement", "design", "products", "services"],
            },
            "ask_energy_planning": {
                0: ["overall goal", "output", "process", "baseline", "enpis", "objectives", "targets", "action plans"],
                1: ["legal requirements", "energy review", "significant energy uses", "baselines", "enpis", "analyze", "identifying"],
            },
            "ask_energy_baseline": {
                0: ["quantitative reference", "characteristics", "time", "normalized", "adjusted", "variables", "production", "temperature", "degree days"],
                1: ["establish", "information", "initial energy review", "data period", "suitable", "adjustments", "three specific conditions", "regulatory"],
            },
            "ask_enpi": {
                0: ["purpose", "monitoring", "measuring", "methodology", "recorded", "reviewed", "identified", "appropriate"],
                1: ["quantitative values", "expressed", "metric", "ratio", "model", "simple", "complex", "consumption per unit"],
            },
        }
        
        # Get keyword mapping for this intent
        keyword_map = keyword_mappings.get(intent, {})
        
        # Score each response based on keyword matches
        scores = [0] * len(responses)
        
        for response_index, keywords in keyword_map.items():
            if response_index < len(responses):
                for keyword in keywords:
                    if keyword in user_message:
                        scores[response_index] += 2
                    # Also check if keyword appears in response text
                    response_text = responses[response_index].get("text", "").lower()
                    if keyword in response_text:
                        scores[response_index] += 1
        
        # If we have scores, select the response with highest score
        if max(scores) > 0:
            best_index = scores.index(max(scores))
            return responses[best_index].get("text", "")
        
        # Fallback: Use hash of user message to consistently select same response for same question
        # This provides variety while being deterministic
        message_hash = abs(hash(user_message)) % len(responses)
        return responses[message_hash].get("text", "")

