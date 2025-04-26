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

matrix_n = kw.cim.normalizer(matrix, normalization=0.5)  # 矩阵归一化
output = kw.cim.simulator_core(
            matrix_n,
            c = 0,
            pump = 0.7,
            noise = 0.01,
            laps = 1000,
            dt = 0.1)

h = kw.sampler.hamiltonian(matrix, output)   #  计算哈密顿量，使用未进行归一化的矩阵进行计算

# # 绘制量子比特演化图与哈密顿量图
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

# 查看最优解，将kaiwu.cim.simulator_core模拟器输出的数据使用如下函数进行二值化
c_set = kw.sampler.binarizer(output)

# 最优解采样，如下数据进行能量排序，越靠前能量越低，解越优
opt = kw.sampler.optimal_sampler(matrix, c_set, 0)

# print(opt) opt=(解集,能量)
best = opt[0][0]
print(best)

max_cut = (np.sum(-matrix)-np.dot(-matrix,best).dot(best))/4
print("The obtained max cut is "+str(max_cut)+".")
