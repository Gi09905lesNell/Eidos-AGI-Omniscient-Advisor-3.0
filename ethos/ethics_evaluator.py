# 伦理评估器
class EthicsEvaluator:
    def __init__(self):
        # 基础阈值设置
        self.ethics_threshold = 0.7
        
        # 初始化各类评分权重
        self.content_weight = 0.4
        self.style_weight = 0.3 
        self.context_weight = 0.3
        
        # 敏感内容类别及其权重
        self.sensitive_categories = {
            "violence": 0.25,
            "nudity": 0.2,
            "hate_speech": 0.3,
            "discrimination": 0.25
        }
        
        # 文化背景评估参数
        self.cultural_contexts = {
            "eastern": {
                "modesty_threshold": 0.8,
                "violence_threshold": 0.6,
                "religious_sensitivity": 0.9
            },
            "western": {
                "modesty_threshold": 0.6,
                "violence_threshold": 0.7,
                "religious_sensitivity": 0.7
            }
        }
        
        # 年龄分级标准
        self.age_ratings = {
            "general": {"violence": 0.2, "nudity": 0.1, "language": 0.2},
            "teen": {"violence": 0.4, "nudity": 0.3, "language": 0.4},
            "mature": {"violence": 0.7, "nudity": 0.6, "language": 0.7},
            "adult": {"violence": 0.9, "nudity": 0.9, "language": 0.9}
        }
        
        # 初始化内容分析器
        self.content_analyzer = self._initialize_content_analyzer()
        
    def _initialize_content_analyzer(self):
        """初始化内容分析组件"""
        return {
            "text_analyzer": self._create_text_analyzer(),
            "image_analyzer": self._create_image_analyzer(),
            "context_analyzer": self._create_context_analyzer()
        }
        
    def _create_text_analyzer(self):
        """创建文本分析器"""
        return {
            "profanity_filter": self._create_profanity_filter(),
            "sentiment_analyzer": self._create_sentiment_analyzer(),
            "hate_speech_detector": self._create_hate_speech_detector()
        }
        
    def _create_image_analyzer(self):
        """创建图像分析器"""
        return {
            "nudity_detector": self._create_nudity_detector(),
            "violence_detector": self._create_violence_detector(),
            "symbol_analyzer": self._create_symbol_analyzer()
        }
        
    def _create_context_analyzer(self):
        """创建上下文分析器"""
        return {
            "cultural_analyzer": self._create_cultural_analyzer(),
            "historical_analyzer": self._create_historical_analyzer(),
            "social_impact_analyzer": self._create_social_impact_analyzer()
        }
        
    def evaluate_artwork(self, artwork):
        """评估艺术作品的伦理性"""
        ethics_score = self._calculate_ethics_score(artwork)
        detailed_report = self._generate_evaluation_report(artwork, ethics_score)
        return {
            "is_ethical": ethics_score > self.ethics_threshold,
            "score": ethics_score,
            "report": detailed_report
        }
        
    def _calculate_ethics_score(self, artwork):
        """计算作品的伦理评分"""
        content_score = self._evaluate_content(artwork) * self.content_weight
        style_score = self._evaluate_style(artwork) * self.style_weight
        context_score = self._evaluate_context(artwork) * self.context_weight
        
        return content_score + style_score + context_score
        
    def _evaluate_content(self, artwork):
        """评估作品内容"""
        text_score = self._analyze_text_content(artwork)
        image_score = self._analyze_image_content(artwork)
        semantic_score = self._analyze_semantic_content(artwork)
        
        return (text_score + image_score + semantic_score) / 3
        
    def _analyze_text_content(self, artwork):
        """分析文本内容"""
        if not hasattr(artwork, 'text_content'):
            return 1.0
            
        profanity_score = self._check_profanity(artwork.text_content)
        sentiment_score = self._analyze_sentiment(artwork.text_content)
        hate_speech_score = self._detect_hate_speech(artwork.text_content)
        
        return (profanity_score + sentiment_score + hate_speech_score) / 3
        
    def _check_profanity(self, text):
        """检查不当用语"""
        profanity_level = 0
        weighted_score = 0
        
        # 对不同级别的不当用语进行评分
        for word in text.split():
            if word in self._get_severe_profanity_list():
                profanity_level += 0.8
            elif word in self._get_moderate_profanity_list():
                profanity_level += 0.5
            elif word in self._get_mild_profanity_list():
                profanity_level += 0.2
                
        return max(0, 1 - profanity_level)
        
    def _analyze_sentiment(self, text):
        """分析文本情感"""
        positive_score = self._calculate_positive_sentiment(text)
        negative_score = self._calculate_negative_sentiment(text)
        neutral_score = self._calculate_neutral_sentiment(text)
        
        # 权衡不同情感的影响
        weighted_score = (
            positive_score * 0.4 +
            neutral_score * 0.4 +
            (1 - negative_score) * 0.2
        )
        
        return weighted_score
        
    def _detect_hate_speech(self, text):
        """检测仇恨言论"""
        hate_speech_indicators = self._analyze_hate_speech_patterns(text)
        discrimination_level = self._analyze_discrimination(text)
        extremism_level = self._analyze_extremist_content(text)
        
        # 综合评估仇恨言论程度
        hate_speech_score = 1 - (
            hate_speech_indicators * 0.4 +
            discrimination_level * 0.3 +
            extremism_level * 0.3
        )
        
        return max(0, min(1, hate_speech_score))
        
    def _analyze_image_content(self, artwork):
        """分析图像内容"""
        if not hasattr(artwork, 'image_content'):
            return 1.0
            
        nudity_score = self._detect_nudity(artwork.image_content)
        violence_score = self._detect_violence(artwork.image_content)
        symbol_score = self._analyze_symbols(artwork.image_content)
        
        return (nudity_score + violence_score + symbol_score) / 3
        
    def _detect_nudity(self, image):
        """检测不当内容"""
        exposure_level = self._calculate_exposure_level(image)
        context_appropriateness = self._evaluate_context_appropriateness(image)
        artistic_value = self._evaluate_artistic_merit(image)
        
        # 权衡不同因素
        weighted_score = (
            (1 - exposure_level) * 0.4 +
            context_appropriateness * 0.3 +
            artistic_value * 0.3
        )
        
        return max(0, min(1, weighted_score))
        
    def _detect_violence(self, image):
        """检测暴力内容"""
        violence_level = self._calculate_violence_level(image)
        gore_level = self._calculate_gore_level(image)
        weapon_presence = self._detect_weapons(image)
        
        # 评估暴力程度
        weighted_score = 1 - (
            violence_level * 0.4 +
            gore_level * 0.4 +
            weapon_presence * 0.2
        )
        
        return max(0, min(1, weighted_score))
        
    def _analyze_symbols(self, image):
        """分析符号和象征"""
        hate_symbols = self._detect_hate_symbols(image)
        religious_symbols = self._analyze_religious_symbols(image)
        cultural_symbols = self._analyze_cultural_symbols(image)
        
        # 评估符号的适当性
        symbol_score = 1 - (
            hate_symbols * 0.5 +
            self._evaluate_symbol_sensitivity(religious_symbols) * 0.25 +
            self._evaluate_symbol_sensitivity(cultural_symbols) * 0.25
        )
        
        return max(0, min(1, symbol_score))
        
    def _evaluate_style(self, artwork):
        """评估艺术风格"""
        composition_score = self._analyze_composition(artwork)
        technique_score = self._analyze_technique(artwork)
        innovation_score = self._analyze_innovation(artwork)
        
        return (composition_score + technique_score + innovation_score) / 3
        
    def _evaluate_context(self, artwork):
        """评估作品上下文"""
        cultural_score = self._analyze_cultural_context(artwork)
        historical_score = self._analyze_historical_context(artwork)
        social_score = self._analyze_social_impact(artwork)
        
        return (cultural_score + historical_score + social_score) / 3
        
    def _generate_evaluation_report(self, artwork, ethics_score):
        """生成评估报告"""
        return {
            "overall_score": ethics_score,
            "content_analysis": self._generate_content_report(artwork),
            "style_analysis": self._generate_style_report(artwork),
            "context_analysis": self._generate_context_report(artwork),
            "recommendations": self._generate_recommendations(artwork, ethics_score),
            "age_rating": self._determine_age_rating(artwork),
            "cultural_considerations": self._analyze_cultural_considerations(artwork)
        }
        
    def update_ethics_standards(self, new_standards):
        """更新伦理标准"""
        self.ethics_threshold = new_standards.get('threshold', self.ethics_threshold)
        self.content_weight = new_standards.get('content_weight', self.content_weight)
        self.style_weight = new_standards.get('style_weight', self.style_weight)
        self.context_weight = new_standards.get('context_weight', self.context_weight)
        
        # 更新敏感类别权重
        if 'sensitive_categories' in new_standards:
            self.sensitive_categories.update(new_standards['sensitive_categories'])
            
        # 更新文化背景参数
        if 'cultural_contexts' in new_standards:
            self.cultural_contexts.update(new_standards['cultural_contexts'])
            
        # 更新年龄分级标准
        if 'age_ratings' in new_standards:
            self.age_ratings.update(new_standards['age_ratings'])
            
    def get_ethics_metrics(self):
        """获取当前伦理评估指标"""
        return {
            "threshold": self.ethics_threshold,
            "weights": {
                "content": self.content_weight,
                "style": self.style_weight,
                "context": self.context_weight
            },
            "sensitive_categories": self.sensitive_categories,
            "cultural_contexts": self.cultural_contexts,
            "age_ratings": self.age_ratings
        }
