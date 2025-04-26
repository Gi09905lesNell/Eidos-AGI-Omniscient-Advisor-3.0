# 艺术粒子生成器
import torch
import numpy as np
from typing import Tuple, Optional
import math
class ArtParticleGenerator:
    def __init__(self, 
                 particle_dim: int = 128,
                 device: str = 'cuda' if torch.cuda.is_available() else 'cpu',
                 seed: Optional[int] = None):
        """
        初始化艺术粒子生成器
        
        Args:
            particle_dim: 粒子维度
            device: 运行设备
            seed: 随机种子
        """
        self.particle_dim = particle_dim
        self.device = device
        if seed is not None:
            torch.manual_seed(seed)
            np.random.seed(seed)
        
    def generate_particles(self, 
                         n_particles: int,
                         temperature: float = 1.0) -> torch.Tensor:
        """
        生成艺术粒子
        
        Args:
            n_particles: 生成粒子数量
            temperature: 温度参数,控制随机性
            
        Returns:
            normalized_particles: 归一化后的粒子张量
        """
        # 生成基础随机粒子
        particles = torch.randn(n_particles, self.particle_dim, device=self.device)
        particles = particles * temperature
        
        # 归一化
        normalized_particles = particles / torch.norm(particles, dim=1, keepdim=True)
        
        return normalized_particles
    
    def generate_structured_particles(self,
                                   n_particles: int,
                                   n_clusters: int = 4) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        生成具有聚类结构的艺术粒子
        
        Args:
            n_particles: 总粒子数量
            n_clusters: 聚类数量
            
        Returns:
            particles: 生成的粒子
            cluster_labels: 聚类标签
        """
        # 计算每个聚类的粒子数
        particles_per_cluster = n_particles // n_clusters
        
        particles_list = []
        labels_list = []
        
        for i in range(n_clusters):
            # 为每个聚类生成中心点
            cluster_center = torch.randn(1, self.particle_dim, device=self.device)
            cluster_center = cluster_center / torch.norm(cluster_center)
            
            # 在中心点周围生成粒子
            cluster_particles = torch.randn(particles_per_cluster, self.particle_dim, device=self.device)
            cluster_particles = cluster_particles + cluster_center
            
            # 归一化
            cluster_particles = cluster_particles / torch.norm(cluster_particles, dim=1, keepdim=True)
            
            particles_list.append(cluster_particles)
            labels_list.append(torch.full((particles_per_cluster,), i, device=self.device))
            
        # 合并所有粒子和标签
        particles = torch.cat(particles_list, dim=0)
        labels = torch.cat(labels_list, dim=0)
        
        return particles, labels
    
    def interpolate_particles(self,
                            particle1: torch.Tensor,
                            particle2: torch.Tensor,
                            steps: int = 10) -> torch.Tensor:
        """
        在两个粒子之间进行插值
        
        Args:
            particle1: 起始粒子
            particle2: 结束粒子
            steps: 插值步数
            
        Returns:
            interpolated: 插值后的粒子序列
        """
        # 确保输入是规范化的
        particle1 = particle1 / torch.norm(particle1)
        particle2 = particle2 / torch.norm(particle2)
        
        # 计算插值权重
        weights = torch.linspace(0, 1, steps, device=self.device)
        
        # 球面插值
        omega = torch.acos(torch.dot(particle1.flatten(), particle2.flatten()))
        sin_omega = torch.sin(omega)
        
        interpolated = []
        for w in weights:
            # 使用球面线性插值(SLERP)
            if sin_omega > 0:
                interp = (torch.sin((1-w)*omega)/sin_omega * particle1 + 
                         torch.sin(w*omega)/sin_omega * particle2)
            else:
                interp = particle1
                
            interpolated.append(interp)
            
        return torch.stack(interpolated)
