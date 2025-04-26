# 导入 kaiwu sdk
import kaiwu as kw
import math
import os
import csv
# # 导入 numpy
import numpy as np
# 授权初始化代码
# 示例的user_id和sdk_code无效，需要替换成自己的用户ID和SDK授权码
kw.license.init(user_id="67895880920858626", sdk_code="mEgNKZCZ1EXd0BBneJOAGKewRKujHA")


#
# # 输入的图矩阵取反
# matrix = -np.array([
#                 [0, 1, 0, 1, 1, 0, 0, 1, 1, 0],
#                 [1, 0, 1, 0, 0, 1, 1, 1, 0, 0],
#                 [0, 1, 0, 1, 1, 0, 0, 0, 1, 0],
#                 [1, 0, 1, 0, 0, 1, 1, 0 ,1, 0],
#                 [1, 0, 1, 0, 0, 1, 0, 1, 0, 1],
#                 [0, 1, 0, 1, 1, 0, 0, 0, 1, 1],
#                 [0, 1, 0, 1, 0, 0, 0, 0, 0, 1],
#                 [1, 1, 0, 0, 1, 0, 0, 0, 1, 0],
#                 [1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
#                 [0, 0, 0, 0, 1, 1, 1, 0, 1, 0]])
# # 模拟计算
# output = kw.cim.simulator(
#             matrix,
#             pump = 0.7,
#             noise = 0.01,
#             laps = 50,
#             dt = 0.1,
#             normalization = 0.3,
#             iterations = 10)
#
# # 最优解采样
# opt = kw.sampler.optimal_sampler(matrix, output, 0)
#
# # 输出结果
# best = opt[0][0]
# max_cut = (np.sum(-matrix)-np.dot(-matrix,best).dot(best))/4
# print("The obtained max cut is "+str(max_cut)+".")


# 定义CIMSolver类
class CIMSolver:
    # 初始化数据
    def prepare_data(self, path, CAP_EDGE=10):
        cloud_path = os.path.join("C:/Users/26250/Desktop/量子计算/Attachment 4_Cloud Facilities Data.csv", 'Attachment 4_Cloud Facilities Data.csv')
        edge_path = os.path.join("C:/Users/26250/Desktop/量子计算/Attachment 3_Candidate Edge Facilities Data.csv", 'Attachment 3_Candidate Edge Facilities Data.csv')
        user_path = os.path.join("C:/Users/26250/Desktop/量子计算/Attachment 2_Computational Demand Distribution Data.csv", 'Attachment 2_Computational Demand Distribution Data.csv')

        # 初始化云服务器成本
        C_FIX_CLOUD = {}
        LOC_SET_OUTTER = []
        with open("C:/Users/26250/Desktop/量子计算/Attachment 4_Cloud Facilities Data.csv", 'r') as f:
            reader = csv.reader(f, delimiter=',', quotechar='|')
            next(f)
            for row in reader:
                C_FIX_CLOUD[row[0] + ',' + row[1]] = int(row[2])
                LOC_SET_OUTTER.append(row[0] + ',' + row[1])

        self.C_FIX_CLOUD = C_FIX_CLOUD
        self.LOC_SET_OUTTER = LOC_SET_OUTTER

        # 初始化边缘服务器成本
        C_FIX_EDGE = {}
        self.LOC_EDGE = []
        with open("C:/Users/26250/Desktop/量子计算/Attachment 3_Candidate Edge Facilities Data.csv", 'r') as f:
            reader = csv.reader(f, delimiter=',', quotechar='|')
            next(f)
            for row in reader:
                C_FIX_EDGE[row[0] + ',' + row[1]] = int(row[2])
                self.LOC_EDGE.append(row[0] + ',' + row[1])

        self.C_FIX_EDGE = C_FIX_EDGE

        # 初始化变量成本
        C_VAR_CLOUD = 1
        C_VAR_EDGE = 2

        self.C_VAR_CLOUD = C_VAR_CLOUD
        self.C_VAR_EDGE = C_VAR_EDGE

        # 初始化用户需求
        DEM = {}
        LOC_SET_INNER = []
        LOC_SET_INNER_full = []
        with open("C:/Users/26250/Desktop/量子计算/Attachment 2_Computational Demand Distribution Data.csv", 'r') as f:
            reader = csv.reader(f, delimiter=',', quotechar='|')
            next(f)
            for row in reader:
                LOC_SET_INNER_full.append(row[0] + ',' + row[1])
                if int(row[2]):
                    DEM[row[0] + ',' + row[1]] = int(row[2])
                    LOC_SET_INNER.append(row[0] + ',' + row[1])

        self.DEM = DEM
        self.LOC_SET_INNER = LOC_SET_INNER

        # 初始化传输成本
        C_TRAN_ij = 1  # 端到边
        C_TRAN_ik = 2  # 端到云
        C_TRAN_jk = 1  # 边到云

        self.C_TRAN_ij = C_TRAN_ij
        self.C_TRAN_ik = C_TRAN_ik
        self.C_TRAN_jk = C_TRAN_jk

        # 全部节点
        LOC_SET = LOC_SET_INNER_full + LOC_SET_OUTTER
        self.LOC_SET = LOC_SET

        self.num_cloud = len(self.LOC_SET_OUTTER)
        self.num_edge = len(self.LOC_EDGE)
        self.num_user = len(self.LOC_SET_INNER)

        # 计算距离
        DIST = {}
        for i in LOC_SET:
            for j in LOC_SET:
                DIST[(i, j)] = round(np.sqrt((int(i.split(',')[0]) - int(j.split(',')[0])) ** 2 + (
                        int(i.split(',')[1]) - int(j.split(',')[1])) ** 2), 2)
        self.DIST = DIST

        # 边缘计算节点覆盖半径
        RANGE = 3
        self.RANGE = RANGE

        # 计算覆盖关系
        ALPHA = {}
        for i in LOC_SET:
            for j in LOC_SET:
                if DIST[(i, j)] <= RANGE:
                    ALPHA[(i, j)] = 1
                else:
                    ALPHA[(i, j)] = 0
        self.ALPHA = ALPHA
        self.CAP_EDGE = CAP_EDGE

    # 准备模型
    def prepare_model(self, lam_equ = None, lam = None):
        # 设置等式约束的惩罚系数，默认值为[10000, 10000, 10000]
        if lam_equ is None:
            lam_equ = [10000, 10000, 10000]
        if lam is None:
            lam = [10000, 10000]
        self.lam_equ = lam_equ

        # 设置不等式约束的惩罚系数
        self.lam = lam

        # 计算每条边的最大需求
        self.max_ujk = []
        for j in self.LOC_EDGE:
            self.max_ujk.append(sum(self.DEM[i] * self.ALPHA[i, j] for i in self.LOC_SET_INNER))
        # print('self.max_ujk', self.max_ujk)

        # 初始化决策变量
        self.x_edge = kw.qubo.ndarray(self.num_edge, 'x_edge', kw.qubo.binary)
        self.yij = kw.qubo.ndarray((self.num_user, self.num_edge), 'yij', kw.qubo.binary)
        self.yjk = kw.qubo.ndarray((self.num_edge, self.num_cloud), 'yjk', kw.qubo.binary)
        self.yik = kw.qubo.ndarray((self.num_user, self.num_cloud), 'yik', kw.qubo.binary)

        # 对于每条边，如果最大需求不超过边的容量，设置对应的yjk为0
        for j in range(self.num_edge):
            if self.max_ujk[j] <= self.CAP_EDGE:
                self.yjk[j][0] = 0

        # 约束2：初始化约束表达式
        self.constraint2 = 0
        for i in range(self.num_user):
            for j in range(self.num_edge):
                if self.ALPHA[(self.LOC_SET_INNER[i], self.LOC_EDGE[j])] == 0:
                    self.yij[i][j] = 0
                else:
                    self.constraint2 += self.yij[i][j] * (1 - self.x_edge[j])

        # 初始化ujk相关变量
        self.ujk = np.zeros(shape=(self.num_edge, self.num_cloud), dtype=kw.qubo.QuboExpression)
        self.ujk_residual = np.zeros(shape=self.num_edge, dtype=kw.qubo.QuboExpression)
        for j in range(self.num_edge):
            self.ujk_residual[j] = sum(
                self.DEM[self.LOC_SET_INNER[i]] * self.yij[i][j] for i in range(self.num_user)) - self.CAP_EDGE
            for k in range(self.num_cloud):
                self.ujk[j][k] = self.yjk[j][k] * self.ujk_residual[j]

        # 目标函数
        self.c_fix = sum(self.C_FIX_EDGE[self.LOC_EDGE[j]] * self.x_edge[j] for j in range(self.num_edge))

        self.c_var = self.C_VAR_CLOUD * sum(sum(self.DEM[self.LOC_SET_INNER[i]] * self.yik[i][k]
                                                for i in range(self.num_user)) for k in range(self.num_cloud))
        self.c_var += self.C_VAR_EDGE * sum(
            sum(self.DEM[self.LOC_SET_INNER[i]] * self.yij[i][j] for i in range(self.num_user))
            for j in range(self.num_edge))
        self.c_var += (self.C_VAR_CLOUD - self.C_VAR_EDGE) * sum(sum(self.ujk[j][k] for j in range(self.num_edge)) for k
                                                                in range(self.num_cloud))

        self.c_tran = self.C_TRAN_ij * sum(
            sum(self.DEM[self.LOC_SET_INNER[i]] * self.DIST[(self.LOC_SET_INNER[i], self.LOC_EDGE[j])] * self.yij[i][j]
                for i in range(self.num_user)) for j in range(self.num_edge))
        self.c_tran += self.C_TRAN_ik * sum(sum(
            self.DEM[self.LOC_SET_INNER[i]] * self.DIST[(self.LOC_SET_INNER[i], self.LOC_SET_OUTTER[k])] * self.yik[i][k]
            for i in range(self.num_user)) for k in range(self.num_cloud))
        self.c_tran += self.C_TRAN_jk * sum(sum(self.DIST[(self.LOC_EDGE[j], self.LOC_SET_OUTTER[k])] * self.ujk[j][k]
                                                for j in range(self.num_edge)) for k in range(self.num_cloud))
        self.obj = self.c_fix + self.c_var + self.c_tran

        # 约束1：确保每个用户的服务需求仅被分配到一个位置（边侧或云侧）
        self.constraint1 = 0
        for i in range(self.num_user):
            self.constraint1 += (sum(self.yij[i][j] for j in range(self.num_edge))
                                 + sum(self.yik[i][k] for k in range(self.num_cloud)) - 1) ** 2

        # 不等式约束1：需求减去边的最大容量后，应该满足yjk约束
        self.ineq_constraint1 = []
        self.ineq_qubo1 = 0
        self.len_slack1 = math.ceil(math.log2(max(self.max_ujk) + 1))
        self.slack1 = kw.qubo.ndarray((self.num_edge, self.num_cloud, self.len_slack1), 'slack1', kw.qubo.binary)

        for j in range(self.num_edge):
            self.ineq_constraint1.append([])
            for k in range(self.num_cloud):
                if self.yjk[j][k] == 0:
                    self.ineq_constraint1[j].append(0)
                else:
                    self.ineq_constraint1[j].append(
                        self.ujk_residual[j] - (self.max_ujk[j] - self.CAP_EDGE) * self.yjk[j][k])
                    self.ineq_qubo1 += (self.ineq_constraint1[j][k] + sum(
                        self.slack1[j][k][_] * (2 ** _) for _ in range(self.len_slack1))) ** 2

        # 不等式约束2：边的容量应大于等于需求
        self.ineq_qubo2 = 0
        self.ineq_constraint2 = []
        self.len_slack2 = math.ceil(math.log2(max(self.max_ujk) + 1))
        self.slack2 = kw.qubo.ndarray((self.num_edge, self.num_cloud, self.len_slack2), 'slack2', kw.qubo.binary)

        for j in range(self.num_edge):
            self.ineq_constraint2.append([])
            for k in range(self.num_cloud):
                if self.yjk[j][k] == 0:
                    self.ineq_constraint2[j].append(0)
                else:
                    self.ineq_constraint2[j].append(self.yjk[j][k] * self.CAP_EDGE -
                                                    sum(self.DEM[self.LOC_SET_INNER[i]] * self.yij[i][j] for i in
                                                        range(self.num_user)))
                    self.ineq_qubo2 += (self.ineq_constraint2[j][k] + sum(self.slack2[j][k][_] * (2 ** _)
                                                                          for _ in range(self.len_slack2))) ** 2

        # 约束3：确保yjk与x_edge之间的关系
        self.constraint3 = 0
        for j in range(self.num_edge):
            for k in range(self.num_cloud):
                self.constraint3 += self.yjk[j][k] * (1 - self.x_edge[j])

        # 构建最终模型
        self.model = self.obj
        self.model += self.lam_equ[0] * self.constraint1 + self.lam_equ[1] * self.constraint2 \
                      + self.lam_equ[2] * self.constraint3
        self.model += self.lam[0] * self.ineq_qubo1 + self.lam[1] * self.ineq_qubo2

        # 将模型转换为Ising模型
        Q = self.model
        Q = kw.qubo.make(Q)
        print(Q)
        ci = kw.qubo.cim_ising_model(Q)
        q=kw.qubo.qubo_model_to_qubo_matrix(Q)
        print(q['qubo_matrix'])
        print(q['qubo_matrix'].shape)
        with open('example.csv','w',encoding='uft-8') as file:
            for line in range(q['qubo_matrix']):
                file.write(line)
                file.write('\n')

        ising = ci.get_ising()
        self.matrix = ising["ising"]
        bias = ising["bias"]

    def sa(self, max_iter, ss = None, T_init = 1000, alpha = 0.99, T_min = 0.0001, iterations_per_T = 10):
        """
        执行模拟退火算法来寻找问题的最优解。

        参数:
        - max_iter: 最大迭代次数
        - T_init: 初始温度
        - alpha: 温度衰减系数
        - T_min: 最低温度
        - iter_per_t: 每个温度下的迭代次数
        - size_limit: 解的大小限制
        """
        iter = 0
        current_best = math.inf  # 初始化当前最佳解为无穷大
        opt_obj = 0  # 期望的最优目标值（可以根据具体问题调整）
        init_solution = None  # 初始化解
        cimsolver=kw.cim.SimulatedCIMOptimizer(pump=1.0, noise=0.1, laps=1000, delta_time=0.1, normalization=0.5, iterations=1, size_limit=100)

        '''csolver=kw.classical.SimulatedAnnealingOptimizer(initial_temperature=1000,
        alpha=0.99, cutoff_temperature=0.001, iterations_per_t=100, size_limit=100)'''
        while (iter < max_iter and current_best > opt_obj):
            print(f'第 {iter} 次迭代开始,当前最佳解 = {current_best}')
            # print('当前最佳解 = ', current_best)
            '''csolver.set_matrix(self.matrix)
            # 执行模拟退火算法S
            output = csolver.solve(self.matrix)'''
            cimsolver.set_matrix(self.matrix)
            cimsolver.solve(self.matrix)
            # 从模拟退火输出中获取最优解
            opt = kw.sampler.optimal_sampler(self.matrix, output, bias=0, negtail_ff=True)
            for vec in opt[0]:
                # 恢复解并计算目标值
                flag, val_obj = self.recovery(vec)
                if flag:
                    # print('可行解，目标值:', val_obj)
                    current_best = min(current_best, val_obj)  # 更新当前最佳解
            iter += 1
            # print(self.recovery(opt[0][0]))
        print('最优解:', current_best)

    def recovery(self, best):
        """
        恢复最优解并计算约束条件和目标值。

        参数:
        - best: 最优解向量

        返回:
        - (flag, val_obj): flag表示解是否可行，val_obj是目标值或不等式违反的数量
        """
        vars = self.obj_ising.get_variables()  # 获取变量集合
        sol_dict = kw.qubo.get_sol_dict(best, vars)  # 获取解的字典表示
        self.val_eq1 = kw.qubo.get_val(self.constraint1, sol_dict)  # 计算约束1的值
        self.val_eq2 = kw.qubo.get_val(self.constraint2, sol_dict)  # 计算约束2的值
        self.val_eq3 = kw.qubo.get_val(self.constraint3, sol_dict)  # 计算约束3的值
        num_ineq_vio = 0  # 不等式违反数量计数器
        Flag = True  # 标记解是否可行

        # 检查等式约束
        if self.val_eq1 + self.val_eq2 + self.val_eq3:
            Flag = False

        # 检查不等式约束1
        for j in range(self.num_edge):
            for k in range(self.num_cloud):
                if self.ineq_constraint1[j][k] != 0 and kw.qubo.get_val(self.ineq_constraint1[j][k], sol_dict) > 0:
                    Flag = False
                    num_ineq_vio += 1

        # 检查不等式约束2
        for j in range(self.num_edge):
            for k in range(self.num_cloud):
                if self.ineq_constraint2[j][k] != 0 and kw.qubo.get_val(self.ineq_constraint2[j][k], sol_dict) > 0:
                    Flag = False
                    num_ineq_vio += 1

        # 返回结果：如果解可行，返回目标值，否则返回不等式违反数量
        return (True, kw.qubo.get_val(self.obj, sol_dict)) if Flag else (False, num_ineq_vio)

def main():
    # 创建 CIMSolver 类的实例
    solver = CIMSolver()

    # 准备数据, 路径为存放数据的文件夹Data
    path = 'C:/Users/admin/Desktop/try/kaiwu-sdk-enterprise/Data'
    solver.prepare_data(path)

    # 准备 QUBO 模型，设置惩罚系数 lambda
    solver.prepare_model()

    # 使用模拟退火算法寻找最优解
    max_iter = 200
    # solver.sa(max_iter)

if __name__ == "__main__":
    main()

worker=kw.classical.SimulatedAnnealingOptimizer(
    inital_temperature=1000,
    alpha=0.99,
    cutoff_temperature=0.001,
    interations_per_t=500,
    size_limit=200
)
