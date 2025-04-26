class EntityManager:
    def _initialize_entities(self):
        """初始化场景中的实体"""
        return {
            'agents': [],
            'objects': [],
            'relationships': {}
        }
        
    def _create_entity_framework(self):
        """创建实体基础框架"""
        return {
            'agents': [],
            'objects': [],
            'relationships': {},
            'properties': {},
            'states': {},
            'metadata': {
                'version': '1.0',
                'created_at': time.time(),
                'last_updated': time.time()
            }
        }
        
    # ... 其他实体相关方法 ...