"""
NLP Service for processing job requirements and extracting structured information
"""
import re
import logging
from typing import Dict, List, Any, Tuple
from app.schemas.job_posting import ParsedJobRequirements

logger = logging.getLogger(__name__)


class NLPService:
    """Service class for natural language processing tasks"""

    def __init__(self):
        """Initialize NLP service with skill databases"""
        # Comprehensive skills database for all job sectors
        self.technical_skills_db = {
            # Technology & IT
            'programming_languages': [
                'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby',
                'go', 'rust', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'sql', 'c',
                'objective-c', 'dart', 'perl', 'shell', 'bash'
            ],
            'web_technologies': [
                'html', 'css', 'react', 'angular', 'vue', 'node.js', 'nodejs', 'express',
                'django', 'flask', 'spring', 'laravel', 'bootstrap', 'jquery', 'webpack',
                'sass', 'less', 'tailwind', 'material-ui', 'next.js', 'nuxt.js'
            ],
            'databases': [
                'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'oracle',
                'sqlite', 'cassandra', 'dynamodb', 'firebase', 'mariadb', 'neo4j',
                'influxdb', 'couchdb'
            ],
            'cloud_devops': [
                'aws', 'azure', 'google cloud', 'gcp', 'docker', 'kubernetes', 'terraform',
                'jenkins', 'gitlab', 'github actions', 'circleci', 'ansible', 'chef',
                'puppet', 'vagrant', 'helm'
            ],
            'data_science': [
                'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras',
                'spark', 'hadoop', 'tableau', 'power bi', 'excel', 'jupyter', 'matplotlib',
                'seaborn', 'plotly', 'dask', 'airflow'
            ],
            'mobile': [
                'android', 'ios', 'react native', 'flutter', 'xamarin', 'ionic',
                'cordova', 'swift', 'kotlin', 'objective-c'
            ],
            'testing': [
                'junit', 'pytest', 'selenium', 'cypress', 'jest', 'mocha', 'chai',
                'unittest', 'testng', 'cucumber', 'postman'
            ],

            # Business & Finance
            'finance_accounting': [
                'accounting', 'bookkeeping', 'financial analysis', 'budgeting', 'forecasting',
                'excel', 'quickbooks', 'sap', 'oracle financials', 'gaap', 'ifrs', 'tax preparation',
                'auditing', 'financial reporting', 'cash flow', 'accounts payable', 'accounts receivable',
                'cost accounting', 'financial modeling', 'variance analysis', 'cpa', 'cfa'
            ],
            'business_analysis': [
                'business analysis', 'requirements gathering', 'process improvement', 'stakeholder management',
                'business intelligence', 'data analysis', 'market research', 'competitive analysis',
                'strategic planning', 'process mapping', 'workflow optimization', 'kpi development',
                'project management', 'agile', 'scrum', 'lean', 'six sigma'
            ],
            'consulting': [
                'management consulting', 'strategy consulting', 'change management', 'organizational development',
                'business transformation', 'process optimization', 'performance improvement',
                'stakeholder engagement', 'workshop facilitation', 'presentation skills'
            ],

            # Marketing & Sales
            'digital_marketing': [
                'seo', 'sem', 'google ads', 'facebook ads', 'social media marketing', 'content marketing',
                'email marketing', 'marketing automation', 'google analytics', 'conversion optimization',
                'a/b testing', 'ppc', 'affiliate marketing', 'influencer marketing', 'brand management'
            ],
            'sales': [
                'sales', 'business development', 'lead generation', 'cold calling', 'prospecting',
                'account management', 'customer relationship management', 'crm', 'salesforce',
                'negotiation', 'closing', 'pipeline management', 'territory management', 'b2b sales', 'b2c sales'
            ],
            'marketing_traditional': [
                'brand marketing', 'advertising', 'public relations', 'market research', 'campaign management',
                'event marketing', 'trade shows', 'print advertising', 'radio advertising', 'tv advertising',
                'direct mail', 'outdoor advertising', 'media planning', 'media buying'
            ],

            # Healthcare & Medical
            'medical_clinical': [
                'patient care', 'clinical assessment', 'medical diagnosis', 'treatment planning',
                'medical procedures', 'surgery', 'emergency medicine', 'intensive care', 'radiology',
                'cardiology', 'oncology', 'pediatrics', 'geriatrics', 'psychiatry', 'nursing'
            ],
            'healthcare_admin': [
                'healthcare administration', 'medical billing', 'medical coding', 'hipaa compliance',
                'healthcare regulations', 'patient records', 'electronic health records', 'ehr',
                'medical insurance', 'healthcare quality', 'patient safety', 'clinical workflows'
            ],
            'pharmacy': [
                'pharmaceutical', 'drug dispensing', 'medication therapy management', 'clinical pharmacy',
                'pharmacy operations', 'pharmaceutical calculations', 'drug interactions',
                'pharmacy law', 'controlled substances', 'immunizations'
            ],

            # Education & Training
            'teaching': [
                'curriculum development', 'lesson planning', 'classroom management', 'student assessment',
                'educational technology', 'differentiated instruction', 'special education',
                'learning disabilities', 'educational psychology', 'pedagogy', 'instructional design'
            ],
            'training_development': [
                'training design', 'instructional design', 'e-learning', 'learning management systems',
                'training delivery', 'adult learning', 'training evaluation', 'needs assessment',
                'performance improvement', 'organizational development', 'talent development'
            ],

            # Engineering & Manufacturing
            'mechanical_engineering': [
                'mechanical design', 'cad', 'autocad', 'solidworks', 'inventor', 'catia', 'ansys',
                'finite element analysis', 'thermodynamics', 'fluid mechanics', 'materials science',
                'manufacturing processes', 'quality control', 'lean manufacturing', 'six sigma'
            ],
            'electrical_engineering': [
                'circuit design', 'power systems', 'control systems', 'electronics', 'pcb design',
                'matlab', 'simulink', 'plc programming', 'scada', 'electrical safety', 'power distribution',
                'renewable energy', 'motor control', 'instrumentation'
            ],
            'civil_engineering': [
                'structural design', 'construction management', 'project management', 'autocad',
                'structural analysis', 'concrete design', 'steel design', 'geotechnical engineering',
                'transportation engineering', 'environmental engineering', 'water resources', 'surveying'
            ],
            'chemical_engineering': [
                'process design', 'chemical processes', 'reaction engineering', 'mass transfer', 'heat transfer',
                'thermodynamics', 'fluid mechanics', 'distillation', 'separation processes', 'process control',
                'process safety', 'hysys', 'aspen plus', 'chemcad', 'process simulation', 'process optimization',
                'unit operations', 'chemical kinetics', 'reactor design', 'process equipment design',
                'piping and instrumentation diagrams', 'p&id', 'hazop', 'process hazard analysis',
                'chemical plant design', 'process economics', 'material balance', 'energy balance',
                'process troubleshooting', 'process improvement', 'chemical safety', 'environmental compliance',
                'petrochemicals', 'pharmaceuticals', 'polymer processing', 'catalysis', 'crystallization'
            ],
            'manufacturing': [
                'production planning', 'quality assurance', 'inventory management', 'supply chain',
                'manufacturing processes', 'lean manufacturing', 'continuous improvement', 'safety protocols',
                'equipment maintenance', 'production scheduling', 'cost reduction', 'efficiency optimization'
            ],

            # Legal & Compliance
            'legal': [
                'legal research', 'contract law', 'litigation', 'corporate law', 'employment law',
                'intellectual property', 'regulatory compliance', 'legal writing', 'case management',
                'discovery', 'depositions', 'trial preparation', 'legal analysis', 'due diligence'
            ],
            'compliance': [
                'regulatory compliance', 'risk management', 'audit', 'internal controls', 'policy development',
                'sox compliance', 'gdpr', 'data privacy', 'anti-money laundering', 'kyc', 'risk assessment',
                'compliance monitoring', 'regulatory reporting', 'ethics training'
            ],

            # Human Resources
            'human_resources': [
                'recruitment', 'talent acquisition', 'employee relations', 'performance management',
                'compensation', 'benefits administration', 'hr policies', 'employment law', 'onboarding',
                'training coordination', 'hr analytics', 'workforce planning', 'employee engagement',
                'diversity and inclusion', 'hris', 'payroll'
            ],

            # Operations & Logistics
            'supply_chain': [
                'supply chain management', 'logistics', 'procurement', 'vendor management', 'inventory management',
                'warehouse management', 'transportation', 'distribution', 'demand planning', 'sourcing',
                'contract negotiation', 'cost optimization', 'supplier relationships', 'erp systems'
            ],
            'operations': [
                'operations management', 'process improvement', 'quality management', 'project management',
                'resource planning', 'capacity planning', 'workflow optimization', 'performance metrics',
                'cost control', 'efficiency improvement', 'team management', 'vendor coordination'
            ],

            # Creative & Design
            'graphic_design': [
                'adobe creative suite', 'photoshop', 'illustrator', 'indesign', 'sketch', 'figma',
                'typography', 'branding', 'logo design', 'web design', 'print design', 'ui design',
                'ux design', 'color theory', 'layout design', 'creative direction'
            ],
            'content_creation': [
                'content writing', 'copywriting', 'technical writing', 'creative writing', 'editing',
                'proofreading', 'content strategy', 'storytelling', 'blogging', 'social media content',
                'video production', 'photography', 'content marketing', 'seo writing'
            ],

            # Customer Service & Support
            'customer_service': [
                'customer support', 'customer service', 'call center', 'help desk', 'technical support',
                'customer relations', 'complaint resolution', 'customer satisfaction', 'phone skills',
                'email support', 'chat support', 'ticketing systems', 'customer retention', 'upselling'
            ],

            # Research & Analysis
            'research': [
                'research methodology', 'data collection', 'statistical analysis', 'survey design',
                'qualitative research', 'quantitative research', 'market research', 'academic research',
                'literature review', 'data interpretation', 'research design', 'hypothesis testing'
            ]
        }

        # Flatten technical skills for easier searching
        self.all_technical_skills = []
        for category, skills in self.technical_skills_db.items():
            self.all_technical_skills.extend(skills)

        # Comprehensive soft skills database for all industries
        self.soft_skills_db = [
            # Communication Skills
            'communication', 'verbal communication', 'written communication', 'presentation skills',
            'public speaking', 'active listening', 'interpersonal skills', 'multilingual',
            'cross-cultural communication', 'client communication', 'stakeholder communication',

            # Leadership & Management
            'leadership', 'team leadership', 'people management', 'strategic leadership',
            'change management', 'organizational leadership', 'executive leadership',
            'servant leadership', 'transformational leadership', 'coaching', 'mentoring',
            'delegation', 'team building', 'talent development', 'performance management',

            # Teamwork & Collaboration
            'teamwork', 'collaboration', 'cross-functional collaboration', 'team player',
            'cooperative', 'collective problem solving', 'consensus building',
            'relationship building', 'networking', 'partnership development',

            # Problem Solving & Analytical
            'problem solving', 'analytical thinking', 'critical thinking', 'logical thinking',
            'creative problem solving', 'troubleshooting', 'root cause analysis',
            'decision making', 'strategic thinking', 'systems thinking', 'innovative thinking',

            # Organizational & Time Management
            'time management', 'organization', 'organized', 'detail-oriented', 'attention to detail',
            'multitasking', 'prioritization', 'planning', 'scheduling', 'deadline management',
            'project coordination', 'workflow management', 'resource management',

            # Adaptability & Flexibility
            'adaptable', 'flexible', 'agile', 'resilient', 'change adaptability',
            'learning agility', 'open-minded', 'versatile', 'continuous learning',
            'growth mindset', 'innovation', 'creative', 'entrepreneurial',

            # Customer & Client Focus
            'customer service', 'customer focus', 'client relations', 'customer satisfaction',
            'service orientation', 'empathy', 'patience', 'diplomacy', 'cultural sensitivity',
            'conflict resolution', 'complaint handling', 'relationship management',

            # Sales & Business Development
            'sales skills', 'negotiation', 'persuasion', 'business development',
            'relationship selling', 'consultative selling', 'closing skills',
            'prospecting', 'networking', 'market awareness', 'competitive intelligence',

            # Project Management
            'project management', 'project coordination', 'project planning', 'resource planning',
            'risk management', 'quality management', 'process improvement', 'change management',
            'stakeholder management', 'vendor management', 'budget management',

            # Technical & Industry Specific
            'technical writing', 'documentation', 'training', 'knowledge transfer',
            'quality assurance', 'compliance', 'regulatory knowledge', 'safety consciousness',
            'ethical standards', 'professional integrity', 'confidentiality',

            # Financial & Business Acumen
            'financial acumen', 'business acumen', 'cost consciousness', 'profit awareness',
            'budget management', 'financial analysis', 'business strategy', 'market understanding',
            'commercial awareness', 'business intelligence', 'data-driven decision making',

            # Creative & Innovation
            'creativity', 'innovative', 'design thinking', 'artistic ability', 'visual design',
            'creative writing', 'storytelling', 'brand awareness', 'aesthetic sense',
            'conceptual thinking', 'ideation', 'brainstorming',

            # Healthcare & Medical
            'patient care', 'bedside manner', 'medical ethics', 'compassion', 'empathy',
            'clinical judgment', 'health advocacy', 'patient education', 'medical communication',
            'cultural competency', 'interdisciplinary collaboration',

            # Education & Training
            'teaching', 'curriculum development', 'educational psychology', 'student engagement',
            'learning assessment', 'classroom management', 'educational technology',
            'differentiated instruction', 'inclusive education', 'academic coaching',

            # Legal & Compliance
            'legal research', 'legal writing', 'attention to detail', 'analytical reasoning',
            'ethical reasoning', 'client counseling', 'negotiation', 'advocacy',
            'regulatory compliance', 'risk assessment', 'policy development',

            # Manufacturing & Operations
            'safety consciousness', 'quality focus', 'continuous improvement', 'efficiency optimization',
            'process optimization', 'lean thinking', 'operational excellence', 'troubleshooting',
            'equipment operation', 'maintenance awareness', 'production planning'
        ]

        # Education keywords and patterns
        self.education_keywords = [
            'bachelor', 'master', 'phd', 'doctorate', 'degree', 'university', 'college',
            'institute', 'school', 'education', 'graduated', 'gpa', 'b.s.', 'm.s.',
            'b.a.', 'm.a.', 'b.tech', 'm.tech', 'mba', 'certification', 'diploma'
        ]

        # Experience patterns
        self.experience_patterns = [
            r'(\d+)[\+\-]?\s*years?\s*(of\s*)?(experience|exp)',
            r'(\d+)[\+\-]?\s*yrs?\s*(of\s*)?(experience|exp)',
            r'(minimum|min|at least)\s*(\d+)\s*years?',
            r'(\d+)\s*to\s*(\d+)\s*years?',
            r'(\d+)\s*-\s*(\d+)\s*years?'
        ]

    def parse_job_requirements(self, job_description: str) -> ParsedJobRequirements:
        """
        Parse natural language job description into structured requirements

        Args:
            job_description: Raw job description text

        Returns:
            ParsedJobRequirements: Structured job requirements
        """
        text = job_description.lower()

        # Extract different types of requirements
        required_skills = self._extract_technical_skills(text, required=True)
        preferred_skills = self._extract_technical_skills(text, required=False)
        education_requirements = self._extract_education_requirements(text)
        experience_requirements = self._extract_experience_requirements(text)
        soft_skills = self._extract_soft_skills(text)
        min_years, max_years = self._extract_experience_years(text)

        # Remove duplicates and clean up
        required_skills = list(set(required_skills))
        preferred_skills = list(set(preferred_skills) - set(required_skills))

        return ParsedJobRequirements(
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            education_requirements=education_requirements,
            experience_requirements=experience_requirements,
            soft_skills=soft_skills,
            min_experience_years=min_years,
            max_experience_years=max_years
        )

    def _extract_technical_skills(self, text: str, required: bool = True) -> List[str]:
        """Extract technical skills from job description"""
        found_skills = []

        # Look for skills in the technical skills database
        for skill in self.all_technical_skills:
            if self._is_skill_mentioned(text, skill):
                # Determine if skill is required or preferred
                context = self._get_skill_context(text, skill)
                is_required = self._is_skill_required(context)

                if (required and is_required) or (not required and not is_required):
                    found_skills.append(skill)

        return found_skills

    def _extract_soft_skills(self, text: str) -> List[str]:
        """Extract soft skills from job description"""
        found_skills = []

        for skill in self.soft_skills_db:
            if self._is_skill_mentioned(text, skill):
                found_skills.append(skill)

        return found_skills

    def _extract_education_requirements(self, text: str) -> List[str]:
        """Extract education requirements from job description"""
        requirements = []

        # Common education patterns
        education_patterns = [
            r'bachelor\'?s?\s*(degree|in)',
            r'master\'?s?\s*(degree|in)',
            r'phd|doctorate',
            r'b\.s\.|b\.a\.|m\.s\.|m\.a\.',
            r'university\s*degree',
            r'college\s*degree',
            r'graduate\s*degree',
            r'undergraduate\s*degree'
        ]

        for pattern in education_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Extract more context around the match
                for match in matches:
                    context_match = re.search(
                        rf'.{{0,50}}{re.escape(match)}.{{0,50}}',
                        text,
                        re.IGNORECASE
                    )
                    if context_match:
                        requirements.append(context_match.group().strip())

        # Look for specific fields of study across all disciplines
        field_patterns = [
            # Technology & Engineering
            r'computer science', r'software engineering', r'information technology', r'data science',
            r'electrical engineering', r'mechanical engineering', r'civil engineering', r'chemical engineering',
            r'industrial engineering', r'aerospace engineering', r'biomedical engineering', r'environmental engineering',
            r'systems engineering', r'materials engineering', r'petroleum engineering', r'nuclear engineering',

            # Business & Finance
            r'business administration', r'business management', r'finance', r'accounting', r'economics',
            r'marketing', r'international business', r'entrepreneurship', r'supply chain management',
            r'human resources', r'operations management', r'project management', r'business analytics',
            r'management information systems', r'organizational behavior', r'strategic management',

            # Healthcare & Medical
            r'medicine', r'nursing', r'pharmacy', r'dentistry', r'veterinary medicine', r'public health',
            r'healthcare administration', r'medical technology', r'radiology', r'physical therapy',
            r'occupational therapy', r'speech therapy', r'clinical psychology', r'health sciences',
            r'biomedical sciences', r'epidemiology', r'health informatics', r'nutrition',

            # Sciences & Mathematics
            r'mathematics', r'statistics', r'physics', r'chemistry', r'biology', r'biochemistry',
            r'microbiology', r'biotechnology', r'genetics', r'molecular biology', r'neuroscience',
            r'environmental science', r'geology', r'geography', r'astronomy', r'marine biology',

            # Liberal Arts & Humanities
            r'english literature', r'history', r'philosophy', r'political science', r'sociology',
            r'anthropology', r'psychology', r'linguistics', r'foreign languages', r'international relations',
            r'criminal justice', r'social work', r'religious studies', r'cultural studies',

            # Creative Arts & Design
            r'graphic design', r'fine arts', r'art history', r'music', r'theatre', r'film studies',
            r'creative writing', r'journalism', r'communications', r'media studies', r'digital media',
            r'architecture', r'interior design', r'fashion design', r'industrial design',

            # Education
            r'education', r'elementary education', r'secondary education', r'special education',
            r'educational psychology', r'curriculum and instruction', r'educational leadership',
            r'early childhood education', r'adult education', r'instructional design',

            # Law & Legal Studies
            r'law', r'legal studies', r'criminal law', r'corporate law', r'international law',
            r'constitutional law', r'environmental law', r'intellectual property law', r'tax law',

            # Agriculture & Environmental
            r'agriculture', r'agricultural engineering', r'forestry', r'environmental studies',
            r'sustainability', r'renewable energy', r'marine sciences', r'wildlife management',

            # Sports & Recreation
            r'kinesiology', r'sports management', r'exercise science', r'recreation management',
            r'athletic training', r'sports psychology', r'physical education',

            # Interdisciplinary & Emerging Fields
            r'cybersecurity', r'artificial intelligence', r'machine learning', r'robotics',
            r'renewable energy', r'sustainable development', r'digital humanities', r'bioinformatics',
            r'computational biology', r'cognitive science', r'game design', r'user experience design'
        ]

        for pattern in field_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                requirements.append(f"Degree in {pattern.title()}")

        return list(set(requirements))

    def _extract_experience_requirements(self, text: str) -> List[str]:
        """Extract experience requirements from job description"""
        requirements = []

        # Look for industry experience
        industry_patterns = [
            r'experience in ([a-z\s]+)',
            r'background in ([a-z\s]+)',
            r'knowledge of ([a-z\s]+)',
            r'familiar with ([a-z\s]+)'
        ]

        for pattern in industry_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.split()) <= 4:  # Keep it reasonable
                    requirements.append(f"Experience in {match.strip()}")

        return requirements

    def _extract_experience_years(self, text: str) -> Tuple[int, int]:
        """Extract minimum and maximum experience years"""
        min_years = 0
        max_years = None

        for pattern in self.experience_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # Handle different tuple structures
                    numbers = [m for m in match if m.isdigit()]
                    if len(numbers) >= 2:
                        min_years = max(min_years, int(numbers[0]))
                        max_years = int(numbers[1])
                    elif len(numbers) == 1:
                        min_years = max(min_years, int(numbers[0]))
                else:
                    if match.isdigit():
                        min_years = max(min_years, int(match))

        return min_years, max_years

    def _is_skill_mentioned(self, text: str, skill: str) -> bool:
        """Check if a skill is mentioned in the text"""
        # Use word boundaries to avoid partial matches
        pattern = rf'\b{re.escape(skill.lower())}\b'
        return bool(re.search(pattern, text, re.IGNORECASE))

    def _get_skill_context(self, text: str, skill: str) -> str:
        """Get context around a skill mention"""
        pattern = rf'.{{0,100}}\b{re.escape(skill.lower())}\b.{{0,100}}'
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group() if match else ""

    def _is_skill_required(self, context: str) -> bool:
        """Determine if a skill is required based on context"""
        required_indicators = [
            'required', 'must', 'essential', 'mandatory', 'need', 'necessary',
            'should have', 'should be', 'proficient'
        ]

        preferred_indicators = [
            'preferred', 'nice to have', 'bonus', 'plus', 'advantage',
            'would be great', 'ideal', 'desirable'
        ]

        context_lower = context.lower()

        # Check for preferred indicators first (more specific)
        for indicator in preferred_indicators:
            if indicator in context_lower:
                return False

        # Check for required indicators
        for indicator in required_indicators:
            if indicator in context_lower:
                return True

        # Default to required if no specific indicators found
        return True

    def extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from text for matching"""
        # Simple key phrase extraction
        # In production, you might use more sophisticated NLP
        sentences = re.split(r'[.!?]+', text)
        key_phrases = []

        for sentence in sentences:
            # Extract noun phrases (simplified)
            words = sentence.strip().split()
            if 2 <= len(words) <= 5:  # Reasonable phrase length
                key_phrases.append(sentence.strip())

        return key_phrases[:10]  # Limit to top 10 phrases

    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings"""
        # Simple word-based similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0