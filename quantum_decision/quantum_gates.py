# 量子门操作模块
import torch
import numpy as np
from typing import Union, Optional, List, Tuple
import cmath
class QuantumGates:
    """量子门操作类,实现各种量子门的矩阵表示和应用"""
    
    def __init__(self):
        # 初始化基本量子门矩阵
        self.hadamard_matrix = torch.tensor([[1, 1], [1, -1]], dtype=torch.complex64) / np.sqrt(2)
        self.pauli_x = torch.tensor([[0, 1], [1, 0]], dtype=torch.complex64)
        self.pauli_y = torch.tensor([[0, -1j], [1j, 0]], dtype=torch.complex64)
        self.pauli_z = torch.tensor([[1, 0], [0, -1]], dtype=torch.complex64)
        self.identity = torch.eye(2, dtype=torch.complex64)
        
        # 相位门
        self.s_gate = torch.tensor([[1, 0], [0, 1j]], dtype=torch.complex64)
        self.t_gate = torch.tensor([[1, 0], [0, cmath.exp(1j * np.pi/4)]], dtype=torch.complex64)
        
        # CNOT门
        self.cnot = torch.tensor([[1, 0, 0, 0],
                                [0, 1, 0, 0],
                                [0, 0, 0, 1],
                                [0, 0, 1, 0]], dtype=torch.complex64)
        
        # SWAP门
        self.swap = torch.tensor([[1, 0, 0, 0],
                                [0, 0, 1, 0],
                                [0, 1, 0, 0],
                                [0, 0, 0, 1]], dtype=torch.complex64)

    def apply_hadamard(self, q_state: torch.Tensor) -> torch.Tensor:
        """应用Hadamard门"""
        return torch.matmul(q_state, self.hadamard_matrix)
    
    def apply_pauli_x(self, q_state: torch.Tensor) -> torch.Tensor:
        """应用Pauli-X门(NOT门)"""
        return torch.matmul(q_state, self.pauli_x)
    
    def apply_pauli_y(self, q_state: torch.Tensor) -> torch.Tensor:
        """应用Pauli-Y门"""
        return torch.matmul(q_state, self.pauli_y)
    
    def apply_pauli_z(self, q_state: torch.Tensor) -> torch.Tensor:
        """应用Pauli-Z门"""
        return torch.matmul(q_state, self.pauli_z)
    
    def apply_s_gate(self, q_state: torch.Tensor) -> torch.Tensor:
        """应用S门(π/2相位门)"""
        return torch.matmul(q_state, self.s_gate)
    
    def apply_t_gate(self, q_state: torch.Tensor) -> torch.Tensor:
        """应用T门(π/4相位门)"""
        return torch.matmul(q_state, self.t_gate)
    
    def apply_rotation(self, q_state: torch.Tensor, angle: float, axis: str) -> torch.Tensor:
        """应用任意轴旋转门
        
        Args:
            q_state: 量子态
            angle: 旋转角度(弧度)
            axis: 旋转轴('x', 'y' 或 'z')
        """
        cos = np.cos(angle/2)
        sin = np.sin(angle/2)
        
        if axis.lower() == 'x':
            matrix = torch.tensor([[cos, -1j*sin],
                                 [-1j*sin, cos]], dtype=torch.complex64)
        elif axis.lower() == 'y':
            matrix = torch.tensor([[cos, -sin],
                                 [sin, cos]], dtype=torch.complex64)
        elif axis.lower() == 'z':
            matrix = torch.tensor([[cmath.exp(-1j*angle/2), 0],
                                 [0, cmath.exp(1j*angle/2)]], dtype=torch.complex64)
        else:
            raise ValueError("轴必须是 'x', 'y' 或 'z'")
            
        return torch.matmul(q_state, matrix)
    
    def apply_cnot(self, q_states: torch.Tensor) -> torch.Tensor:
        """应用CNOT门到两量子比特态"""
        return torch.matmul(q_states, self.cnot)
    
    def apply_swap(self, q_states: torch.Tensor) -> torch.Tensor:
        """应用SWAP门到两量子比特态"""
        return torch.matmul(q_states, self.swap)
    
    def apply_controlled_u(self, q_states: torch.Tensor, u_matrix: torch.Tensor) -> torch.Tensor:
        """应用受控U门
        
        Args:
            q_states: 两量子比特态
            u_matrix: 2x2幺正矩阵
        """
        controlled_u = torch.zeros((4, 4), dtype=torch.complex64)
        controlled_u[:2, :2] = self.identity
        controlled_u[2:, 2:] = u_matrix
        return torch.matmul(q_states, controlled_u)
    
    def apply_toffoli(self, q_states: torch.Tensor) -> torch.Tensor:
        """应用Toffoli门(CCNOT)到三量子比特态"""
        toffoli = torch.eye(8, dtype=torch.complex64)
        toffoli[6:8, 6:8] = self.pauli_x
        return torch.matmul(q_states, toffoli)
    
    def apply_phase(self, q_state: torch.Tensor, phase: float) -> torch.Tensor:
        """应用任意相位门"""
        phase_matrix = torch.tensor([[1, 0],
                                   [0, cmath.exp(1j*phase)]], dtype=torch.complex64)
        return torch.matmul(q_state, phase_matrix)
    
    def create_bell_state(self) -> torch.Tensor:
        """创建Bell态(最大纠缠态)"""
        # 初始化为|00⟩态
        state = torch.tensor([1, 0, 0, 0], dtype=torch.complex64)
        # 对第一个量子比特应用Hadamard门
        state = self.apply_hadamard(state.view(1, -1)).view(-1)
        # 应用CNOT门
        return self.apply_cnot(state.view(1, -1)).view(-1)
    
    def measure(self, q_state: torch.Tensor, shots: int = 1000) -> dict:
        """测量量子态
        
        Args:
            q_state: 量子态向量
            shots: 测量次数
        
        Returns:
            测量结果的统计字典
        """
        probs = torch.abs(q_state) ** 2
        outcomes = torch.multinomial(probs, shots, replacement=True)
        result = {}
        for i in range(len(probs)):
            binary = format(i, f'0{int(np.log2(len(probs)))}b')
            count = (outcomes == i).sum().item()
            if count > 0:
                result[binary] = count / shots
        return result
    
    def apply_custom_gate(self, q_state: torch.Tensor, matrix: torch.Tensor) -> torch.Tensor:
        """应用自定义量子门
        
        Args:
            q_state: 量子态
            matrix: 自定义门的矩阵表示
        """
        return torch.matmul(q_state, matrix)
    
    def apply_grover_diffusion(self, q_state: torch.Tensor) -> torch.Tensor:
        """应用Grover扩散算子"""
        n_qubits = int(np.log2(len(q_state)))
        # 构建2^n x 2^n的Hadamard门
        h_n = self.hadamard_matrix
        for _ in range(n_qubits-1):
            h_n = torch.kron(h_n, self.hadamard_matrix)
        # 应用H⊗n
        state = torch.matmul(q_state, h_n)
        # 应用条件相位反转
        state = 2 * torch.mean(state) - state
        # 再次应用H⊗n
        return torch.matmul(state, h_n)
