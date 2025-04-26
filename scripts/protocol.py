class ProtocolManager:
    def _load_ethics_protocol(self, world_id):
        """加载特定世界的伦理协议"""
        self.ethics_protocols[world_id] = {
            'moral_principles': self._generate_moral_principles(),
            'consequence_weights': self._calculate_weights(),
            'risk_threshold': 0.7
        }
        
    def _generate_moral_principles(self):
        """生成基础道德准则"""
        return {
            'harm_prevention': 0.9,
            'fairness': 0.8,
            'autonomy': 0.7,
            'beneficence': 0.8
        }
        
    # ... 其他协议相关方法 ...