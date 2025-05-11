import numpy as np
import kaiwu as kw
kw.license.init(user_id="67895880920858626", sdk_code="mEgNKZCZ1EXd0BBneJOAGKewRKujHA")
# Import the plotting library
import matplotlib.pyplot as plt

# invert input graph matrix
matrix = -np.array([
                [0, 1, 0, 1, 1, 0, 0, 1, 1, 0],
                [1, 0, 1, 0, 0, 1, 1, 1, 0, 0],
                [0, 1, 0, 1, 1, 0, 0, 0, 1, 0],
                [1, 0, 1, 0, 0, 1, 1, 0 ,1, 0],
                [1, 0, 1, 0, 0, 1, 0, 1, 0, 1],
                [0, 1, 0, 1, 1, 0, 0, 0, 1, 1],
                [0, 1, 0, 1, 0, 0, 0, 0, 0, 1],
                [1, 1, 0, 0, 1, 0, 0, 0, 1, 0],
                [1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
                [0, 0, 0, 0, 1, 1, 1, 0, 1, 0]])

matrix_n = kw.cim.normalizer(matrix, normalization=0.5)  # Matrix normalization
output = kw.cim.simulator_core(
            matrix_n,
            c = 0,
            pump = 0.7,
            noise = 0.01,
            laps = 1000,
            dt = 0.1)

h = kw.sampler.hamiltonian(matrix, output)   # Calculate Hamiltonian using unnormalized matrix

# # Plot quantum bit evolution and Hamiltonian diagrams
# plt.figure(figsize=(10, 10))
#
# # pulsing diagram
# plt.subplot(211)
# plt.plot(output, linewidth=1)
# plt.title("Pulse Phase")
# plt.ylabel("Phase")
# plt.xlabel("T")
#
#
# # Energy diagram
# plt.subplot(212)
# plt.plot(h, linewidth=1)
# plt.title("Hamiltonian")
# plt.ylabel("H")
# plt.xlabel("T")
#
# plt.show()

# View optimal solution, binarize the simulator output data using the following function
c_set = kw.sampler.binarizer(output)

# Optimal solution sampling, sort by energy (lower energy = better solution)
opt = kw.sampler.optimal_sampler(matrix, c_set, 0)

# print(opt) opt=(solution set, energy)
best = opt[0][0]
print(best)

max_cut = (np.sum(-matrix)-np.dot(-matrix,best).dot(best))/4
print("The obtained max cut is "+str(max_cut)+".")
