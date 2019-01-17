#!/usr/bin/python
# coding:utf-8

import numpy as np
import pandas as pd
import tushare as ts
from prepare_data import *
from constant import *
from scipy.sparse import lil_matrix
import robust_optimizer
import matplotlib.pyplot as plt


class Portfolio:
    def __init__(self, num=N, rho=0.1, eps=0.05, rep=50, kappa=9.5):
        self.pro =  \
             ts.pro_api("7a7a28e59757d5f8ed48cf7254f2185340f2b528e334ff888a394948")
        self.codes = []
        self.returns = None
        self.rep = rep
        self.kappa = kappa
        self.num = num
        self.rhos = []
        self.rho = rho
        self.epss = []
        self.eps = eps
        self.param_nominal = {}
        self.param_robust = {}
        self.mu = None
        self.cov = None
        self.robust_vars0 = None
        self.robust_vars1 = None
        self.nominal_vars0 = None
        self.nominal_vars1 = None

    def __call__(self):
        pass

    def get_codes(self):
        self.codes = get_codes(self.num)

    def get_returns(self):
        self.returns = get_all_returns(self.pro, self.codes, START_DATE, END_DATE)

    def set_rhos(self):
        self.rhos = np.linspace(0.0, 0.2, num=self.rep, endpoint=True)

    def set_eps(self):
        self.epss = np.linspace(0.0, 0.25, num=self.rep, endpoint=True)

    @staticmethod
    def kappa(eps):
        return ((1 - eps) / eps) ** 0.5

    def get_mu_cov(self):
        # stocks codes
        self.get_codes()
        # returns
        self.get_returns()
        self.mu = pd.DataFrame.mean(self.returns).values
        self.cov = pd.DataFrame.cov(self.returns).values

    @staticmethod
    def sparse_matrix(matrix):
        q = lil_matrix(matrix)
        q_data = q.data
        q_rows = q.rows
        qsubi = []
        qsubj = []
        qval = []
        for i in range(len(q_rows)):
            for j in range(len(q_rows[i])):
                if q_rows[i][j] <= i:
                    qsubi.append(i)
                    qsubj.append(q_rows[i][j])
                    qval.append(q_data[i][j])
        return {"qsubi": qsubi, "qsubj": qsubj, "qval": qval}

    def nominal_portfolio(self, kappa):

        self.param_nominal.update({"mu_plus": self.mu,
                                   "mu_minus": self.mu,
                                   "cov_plus": self.sparse_matrix(self.cov),
                                   "cov_minus": self.sparse_matrix(self.cov),
                                   "rho": 0.,
                                   "kappa": kappa})

    def robust_portfolio(self, kappa, rho=0.1):

        self.param_robust.update({"mu_plus": self.mu + np.abs(self.mu) * rho *10,
                                  "mu_minus": self.mu - np.abs(self.mu) * rho * 10,
                                  "cov_plus": self.sparse_matrix(self.cov + rho * np.abs(self.cov)),
                                  "cov_minus": self.sparse_matrix(self.cov - rho * np.abs(self.cov)),
                                  "rho": rho,
                                  "kappa": kappa})
        opt_var = robust_optimizer.optimizer(self.param_robust)
        return opt_var

    def run_robust(self, typ):
        robust_vars = []
        if not typ:
            for i in range(self.rep):
                robust_vars.append(self.robust_portfolio(self.kappa, self.rhos[i]))
            self.robust_vars0 = robust_vars
        else:
            for i in range(self.rep):
                robust_vars.append(self.robust_portfolio(Portfolio.kappa(self.epss[i]), self.rho))
            self.robust_vars1 = robust_vars

    def run_nominal(self, typ):
        nominal_vars = []
        if not typ:
            for i in range(self.rep):
                nominal_vars.append(self.robust_portfolio(self.kappa, self.rhos[i]))
            self.nominal_vars0 = nominal_vars
        else:
            for i in range(self.rep):
                nominal_vars.append(self.robust_portfolio(Portfolio.kappa(self.epss[i]), self.rho))
            self.nominal_vars1 = nominal_vars

    def plot_fix_eps(self):
        plt.figure()
        plt.xlabel("Relative uncertainty size rho (%)")
        plt.ylabel("VaR(%)")
        plt.plot(self.rhos, self.robust_vars0, color="red",
                 label="Worst-case VaR of the robust portfolio")
        plt.plot(self.rhos, self.nominal_vars0, color="skyblue",
                 label="Worst-case VaR of the nominal portfolio")
        plt.legend()
        plt.title("Epsilon=0.05")
        plt.savefig("C:/Users/Maggie/Pictures/fix_eps.png")

    def plot_fix_rho(self):
        plt.figure()
        plt.xlabel("epsilon")
        plt.ylabel("VaR(%)")
        plt.plot(self.epss, self.robust_vars1, color="red",
                 label="Worst-case VaR of the robust portfolio")
        plt.plot(self.epss, self.nominal_vars1, color="skyblue",
                 label="Worst-case VaR of the nominal portfolio")
        plt.legend()
        plt.title("Uncertainty level rho=10%")
        plt.savefig("C:/Users/Maggie/Pictures/fix_rho.png")


if __name__ == "__main__":
    port = Portfolio()
    port.get_codes()
    port.get_returns()
    port.set_eps()
    port.set_rhos()
    port.get_mu_cov()
    port.run_robust(typ=0)
    port.run_robust(typ=1)
    port.run_nominal(typ=0)
    port.run_nominal(typ=1)
    port.plot_fix_eps()
    port.plot_fix_rho()