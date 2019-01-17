#!/usr/bin/python
# coding:utf-8

from constant import *
import sys
import mosek

inf = 0.0

def streamprinter(text):
    sys.stdout.write(text)
    sys.stdout.flush()


def optimizer(param):
    with mosek.Env() as env:
        with env.Task(0, 0) as task:
            task.set_Stream(mosek.streamtype.log, streamprinter)
            # bound keys for constraints
            bkc = [mosek.boundkey.fx] * N
            bkv = [mosek.boundkey.fr] + [mosek.boundkey.lo] * 2 * N + [mosek.boundkey.fr] * N
            # bound values for constraints
            blc = [inf] * len(bkc)
            buc = [inf] * len(bkc)
            # linear target coef
            cj = [param["kappa"]**2] + \
                 list(param["mu_plus"]) + \
                 list(param["mu_minus"]*(-1)) + \
                 [0.0] * N
            # sparse matrix representation of Gamma(C)
            # num
            numvar = N * 3 + 1
            numcon = len(bkc)
            BARVRDIM = [N] * 2
            # linear constraint coeff matrix stored by row
            asub = []
            aval = [[-1., 1., -1.]] * N
            for k in range(N):
                asub.append([k+1, N+k+1, 2*N+k])

            # feed data
            task.appendvars(numvar)
            task.appendcons(numcon)
            task.appendbarvars(BARVRDIM)
            for j in range(len(cj)):
                task.putcj(j, cj[j])
            for j in range(numvar):
                task.putvarbound(j, bkv[j], -inf, +inf)
            for i in range(numcon):
                task.putconbound(i, bkc[i], blc[i], buc[i])
                task.putarow(i, asub[i], aval[i])
            symc0 = task.appendsparsesymmat(BARVRDIM[0], *param["cov_plus"].values())
            symc1 = task.appendsparsesymmat(BARVRDIM[1], *param["cov_minus"].values())
            # syma0 = task.appendsparsesymmat(BARVRDIM[2], *param["ones"])
            # syma1 = task.appendsparsesymmat(BARVRDIM[3], *param["ones"])
            task.putbarcj(0, [symc0], [1.0])
            task.putbarcj(1, [symc1], [-1.0])
            # task.putbaraij(N, 0, [syma0], [1.])
            # task.putbaraij(N, 1, [syma1], [-1.])

            # objective sense
            task.putobjsense(mosek.objsense.minimize)
            task.optimize()
            task.solutionsummary(mosek.streamtype.msg)
            # Get status information about the solution
            prosta = task.getprosta(mosek.soltype.itr)
            solsta = task.getsolsta(mosek.soltype.itr)
            obj = 0.
            if (solsta == mosek.solsta.optimal or
                    solsta == mosek.solsta.near_optimal):
                obj = task.primalobj(mosek.soltype)
            elif (solsta == mosek.solsta.dual_infeas_cer or
                  solsta == mosek.solsta.prim_infeas_cer or
                  solsta == mosek.solsta.near_dual_infeas_cer or
                  solsta == mosek.solsta.near_prim_infeas_cer):
                print("Primal or dual infeasibility certificate found.\n")
            elif solsta == mosek.solsta.unknown:
                print("Unknown solution status")
            else:
                print("Other solution status")
            return obj




