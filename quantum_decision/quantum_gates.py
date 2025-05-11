# Quantum Gate Operations Module
import torch
import numpy as np
from typing import Union, Optional, List, Tuple
import cmath
class QuantumGates:
    """Quantum gate operations class, implementing matrix representations and applications of various quantum gates"""
    
    def __init__(self):
        # Initialize basic quantum gate matrices
        self.hadamard_matrix = torch.tensor([[1, 1], [1, -1]], dtype=torch.complex64) / np.sqrt(2)
        self.pauli_x = torch.tensor([[0, 1], [1, 0]], dtype=torch.complex64)
        self.pauli_y = torch.tensor([[0, -1j], [1j, 0]], dtype=torch.complex64)
        self.pauli_z = torch.tensor([[1, 0], [0, -1]], dtype=torch.complex64)
        self.identity = torch.eye(2, dtype=torch.complex64)
        
        # Phase gates
        self.s_gate = torch.tensor([[1, 0], [0, 1j]], dtype=torch.complex64)
        self.t_gate = torch.tensor([[1, 0], [0, cmath.exp(1j * np.pi/4)]], dtype=torch.complex64)
        
        # CNOT gate
        self.cnot = torch.tensor([[1, 0, 0, 0],
                                [0, 1, 0, 0],
                                [0, 0, 0, 1],
                                [0, 0, 1, 0]], dtype=torch.complex64)
        
        # SWAP gate
        self.swap = torch.tensor([[1, 0, 0, 0],
                                [0, 0, 1, 0],
                                [0, 1, 0, 0],
                                [0, 0, 0, 1]], dtype=torch.complex64)

    def apply_hadamard(self, q_state: torch.Tensor) -> torch.Tensor:
        """Apply Hadamard gate"""
        return torch.matmul(q_state, self.hadamard_matrix)
    
    def apply_pauli_x(self, q_state: torch.Tensor) -> torch.Tensor:
        """Apply Pauli-X gate (NOT gate)"""
        return torch.matmul(q_state, self.pauli_x)
    
    def apply_pauli_y(self, q_state: torch.Tensor) -> torch.Tensor:
        """Apply Pauli-Y gate"""
        return torch.matmul(q_state, self.pauli_y)
    
    def apply_pauli_z(self, q_state: torch.Tensor) -> torch.Tensor:
        """Apply Pauli-Z gate"""
        return torch.matmul(q_state, self.pauli_z)
    
    def apply_s_gate(self, q_state: torch.Tensor) -> torch.Tensor:
        """Apply S gate (π/2 phase gate)"""
        return torch.matmul(q_state, self.s_gate)
    
    def apply_t_gate(self, q_state: torch.Tensor) -> torch.Tensor:
        """Apply T gate (π/4 phase gate)"""
        return torch.matmul(q_state, self.t_gate)
    
    def apply_rotation(self, q_state: torch.Tensor, angle: float, axis: str) -> torch.Tensor:
        """Apply arbitrary axis rotation gate
        
        Args:
            q_state: Quantum state
            angle: Rotation angle (radians)
            axis: Rotation axis ('x', 'y' or 'z')
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
            raise ValueError("Axis must be 'x', 'y' or 'z'")
            
        return torch.matmul(q_state, matrix)
    
    def apply_cnot(self, q_states: torch.Tensor) -> torch.Tensor:
        """Apply CNOT gate to two-qubit state"""
        return torch.matmul(q_states, self.cnot)
    
    def apply_swap(self, q_states: torch.Tensor) -> torch.Tensor:
        """Apply SWAP gate to two-qubit state"""
        return torch.matmul(q_states, self.swap)
    
    def apply_controlled_u(self, q_states: torch.Tensor, u_matrix: torch.Tensor) -> torch.Tensor:
        """Apply controlled-U gate
        
        Args:
            q_states: Two-qubit state
            u_matrix: 2x2 unitary matrix
        """
        controlled_u = torch.zeros((4, 4), dtype=torch.complex64)
        controlled_u[:2, :2] = self.identity
        controlled_u[2:, 2:] = u_matrix
        return torch.matmul(q_states, controlled_u)
    
    def apply_toffoli(self, q_states: torch.Tensor) -> torch.Tensor:
        """Apply Toffoli gate (CCNOT) to three-qubit state"""
        toffoli = torch.eye(8, dtype=torch.complex64)
        toffoli[6:8, 6:8] = self.pauli_x
        return torch.matmul(q_states, toffoli)
    
    def apply_phase(self, q_state: torch.Tensor, phase: float) -> torch.Tensor:
        """Apply arbitrary phase gate"""
        phase_matrix = torch.tensor([[1, 0],
                                   [0, cmath.exp(1j*phase)]], dtype=torch.complex64)
        return torch.matmul(q_state, phase_matrix)
    
    def create_bell_state(self) -> torch.Tensor:
        """Create Bell state (maximally entangled state)"""
        # Initialize to |00⟩ state
        state = torch.tensor([1, 0, 0, 0], dtype=torch.complex64)
        # Apply Hadamard gate to first qubit
        state = self.apply_hadamard(state.view(1, -1)).view(-1)
        # Apply CNOT gate
        return self.apply_cnot(state.view(1, -1)).view(-1)
    
    def measure(self, q_state: torch.Tensor, shots: int = 1000) -> dict:
        """Measure quantum state
        
        Args:
            q_state: Quantum state vector
            shots: Number of measurements
        
        Returns:
            Dictionary of measurement statistics
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
        """Apply custom quantum gate
        
        Args:
            q_state: Quantum state
            matrix: Matrix representation of custom gate
        """
        return torch.matmul(q_state, matrix)
    
    def apply_grover_diffusion(self, q_state: torch.Tensor) -> torch.Tensor:
        """Apply Grover diffusion operator"""
        n_qubits = int(np.log2(len(q_state)))
        # Construct 2^n x 2^n Hadamard gate
        h_n = self.hadamard_matrix
        for _ in range(n_qubits-1):
            h_n = torch.kron(h_n, self.hadamard_matrix)
        # Apply H⊗n
        state = torch.matmul(q_state, h_n)
        # Apply conditional phase flip
        state = 2 * torch.mean(state) - state
        # Apply H⊗n again
        return torch.matmul(state, h_n)
