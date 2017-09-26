__title__     = "phuzzy"
__author__    = "lepy"
__email__     = "lepy@mailbox.org"
__description__ = """Fuzzy stuff"""
__long_description__ = """
fuzzy number tools
"""
__url__       = 'https://github.com/lepy/phuzzy'
__copyright__ = "Copyright (C) 2017-"
__version__   = "0.1.0"
__status__    = "3 - Alpha"
__credits__   = [""]
__license__   = """MIT"""

import logging
import os
import collections
import numpy as np
import pandas as pd
from scipy.stats import truncnorm, norm
import copy

logger = logging.getLogger("phuzzy")

class FuzzyNumber(object):
    """convex fuzzy number"""
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "x")
        self._df = pd.DataFrame(columns=["alpha", "min", "max"])
        self._number_of_alpha_levels = kwargs.get("number_of_alpha_levels", 10)
        self.df = kwargs.get("df")

    def _get_number_of_alpha_levels(self):
        return self._number_of_alpha_levels
    def _set_number_of_alpha_levels(self, value):
        self._number_of_alpha_levels = int(value)
    number_of_alpha_levels = property(fget=_get_number_of_alpha_levels, fset=_set_number_of_alpha_levels, doc="number of alpha levels")

    def _get_df(self):
        return self._df
    def _set_df(self, value):
        self._df = value
    df = property(fget=_get_df, fset=_set_df, doc="number of alpha levels")

    def convert_df(self, alpha_levels=None, zero=1e-10):
        df = self.df.copy()
        if alpha_levels is not None:
            self.number_of_alpha_levels = alpha_levels
        df.sort_values(['alpha'], ascending=[True], inplace=True)
        # print("!",df)
        xs_l = df["min"].values
        xs_l[xs_l==0] = zero
        alphas_l = df["alpha"].values
        xs_r = df["max"].values[::-1]
        xs_r[xs_r==0] = zero
        alphas_r = df["alpha"].values[::-1]

        alphas_new = np.linspace(0., 1., self.number_of_alpha_levels)
        xs_l_new = np.interp(alphas_new, alphas_l, xs_l)
        xs_r_new = np.interp(alphas_new, alphas_r[::-1], xs_r[::-1])
        #
        # print((xs_l, alphas_l, xs_l_new))
        # print((xs_r, alphas_r, xs_r_new))
        #
        # print((np.vstack((alphas_new, xs_l_new, xs_r_new[::-1]))))
        data = np.vstack((alphas_new, xs_l_new, xs_r_new)).T
        self.df = pd.DataFrame(columns=["alpha", "min", "max"], data=data, dtype=np.float)

    def _unify(self, other):
        old0 = copy.deepcopy(self)
        old1 = copy.deepcopy(other)
        levels = max(len(old0.df), len(old1.df))
        old0.convert_df(levels)
        old1.convert_df(levels)
        return old0, old1

    def __add__(self, other):
        new = FuzzyNumber()
        old0, old1 = self._unify(other)
        quotients = np.vstack([old0.df["min"] + old1.df["min"],
                               old0.df["min"] + old1.df["max"],
                               old0.df["max"] + old1.df["min"],
                               old0.df["max"] + old1.df["max"]])
        new.df = pd.DataFrame.from_dict({"alpha":old0.df.alpha,
                                         "min":np.nanmin(quotients, axis=0),
                                         "max":np.nanmax(quotients, axis=0)} )
        return new

    def __sub__(self, other):
        new = FuzzyNumber()
        old0, old1 = self._unify(other)
        quotients = np.vstack([old0.df["min"] - old1.df["min"],
                               old0.df["min"] - old1.df["max"],
                               old0.df["max"] - old1.df["min"],
                               old0.df["max"] - old1.df["max"]])
        new.df = pd.DataFrame.from_dict({"alpha":old0.df.alpha,
                                         "min":np.nanmin(quotients, axis=0),
                                         "max":np.nanmax(quotients, axis=0)} )
        return new

    def __mul__(self, other):
        # fixme: zeros, infs, nans
        new = FuzzyNumber()
        old0, old1 = self._unify(other)
        quotients = np.vstack([old0.df["min"] * old1.df["min"],
                               old0.df["min"] * old1.df["max"],
                               old0.df["max"] * old1.df["min"],
                               old0.df["max"] * old1.df["max"]])
        new.df = pd.DataFrame.from_dict({"alpha":old0.df.alpha,
                                         "min":np.nanmin(quotients, axis=0),
                                         "max":np.nanmax(quotients, axis=0)} )
        return new


    def __div__(self, other):
        # fixme: zeros, infs, nans
        new = FuzzyNumber()
        old0, old1 = self._unify(other)
        quotients = np.vstack([old0.df["min"] / old1.df["min"],
                               old0.df["min"] / old1.df["max"],
                               old0.df["max"] / old1.df["min"],
                               old0.df["max"] / old1.df["max"]])
        new.df = pd.DataFrame.from_dict({"alpha":old0.df.alpha,
                                         "min":np.nanmin(quotients, axis=0),
                                         "max":np.nanmax(quotients, axis=0)} )
        return new

    def __pow__(self, other):
        # fixme: zeros, infs, nans
        new = FuzzyNumber()
        if isinstance(other, (int, float)):
            other = Trapezoid(alpha0=[other,other], alpha1=[other, other], number_of_alpha_levels=len(self.df))
        old0, old1 = self._unify(other)
        quotients = np.vstack([old0.df["min"] ** old1.df["min"],
                               old0.df["min"] ** old1.df["max"],
                               old0.df["max"] ** old1.df["min"],
                               old0.df["max"] ** old1.df["max"]])
        new.df = pd.DataFrame.from_dict({"alpha":old0.df.alpha,
                                         "min":np.nanmin(quotients, axis=0),
                                         "max":np.nanmax(quotients, axis=0)} )
        new.make_convex()
        return new


    def make_convex(self):
        for i in self.df.index:

            self.df.loc[i, "min"] = self.df.loc[i:, "min"].min()
            self.df.loc[i, "max"] = self.df.loc[i:, "max"].max()
            # self.df.loc[i, "min"] = np.nanmin(self.df.loc[i:, "min"])
            # self.df.loc[i, "max"] = np.nanmax(self.df.loc[i:, "max"])
            # print(i, self.df.loc[i:, "min"].min(), self.df.loc[i:, "max"].max())

    @property
    def alpha0(self):
        """row for alpha=0"""
        if self.df is not None:
            return self.df.iloc[0]

    @property
    def alpha1(self):
        """row for alpha=1"""
        if self.df is not None:
            return self.df.iloc[-1]

    @property
    def area(self):
        A = ((self.alpha0["max"] - self.alpha0["min"]) - (self.df["max"].values - self.df["min"].values)).sum()
        return A

    def import_csv(self, fh):
        if isinstance(fh, str):
            fh = open(fh, "r")

        self.df = pd.DataFrame.from_csv(fh)
        print((self.df.head()))

    def export_csv(self, filepath):
        logger.info("export df '%s'" % filepath)
        if self.df is not None:
            self.df.to_csv(filepath)

    def __str__(self):
        return "({0.__class__.__name__}({0.name}))".format(self)

    def __repr__(self):
        return "(%s)" % self.name

class Triangle(FuzzyNumber):
    """triange fuzzy number"""

    def __init__(self, **kwargs):
        FuzzyNumber.__init__(self, **kwargs)
        alpha0 = kwargs.get("alpha0")
        alpha1 = kwargs.get("alpha1")
        self.discretize(alpha0=alpha0, alpha1=alpha1, alpha_levels=self.number_of_alpha_levels)

    def discretize(self, alpha0, alpha1, alpha_levels):
        assert isinstance(alpha0, collections.Sequence) and len(alpha0) == 2
        assert isinstance(alpha1, collections.Sequence) and len(alpha1) > 0
        self.df = pd.DataFrame(columns=["alpha", "min", "max"], data=[[0., alpha0[0], alpha0[1]], [1., alpha1[0], alpha1[0]]], dtype=np.float)
        self.df.sort_values(['alpha'], ascending=[True], inplace=True)
        self.convert_df(alpha_levels=alpha_levels)

class Trapezoid(FuzzyNumber):
    """triange fuzzy number"""

    def __init__(self, **kwargs):
        FuzzyNumber.__init__(self, **kwargs)
        alpha0 = kwargs.get("alpha0")
        alpha1 = kwargs.get("alpha1")
        self.discretize(alpha0=alpha0, alpha1=alpha1, alpha_levels=self.number_of_alpha_levels)

    def discretize(self, alpha0, alpha1, alpha_levels):
        assert isinstance(alpha0, collections.Sequence) and len(alpha0) == 2
        assert isinstance(alpha1, collections.Sequence) and len(alpha1) == 2
        self.df = pd.DataFrame(columns=["alpha", "min", "max"], data=[[0., alpha0[0], alpha0[1]], [1., alpha1[0], alpha1[1]]], dtype=np.float)
        self.df.sort_values(['alpha'], ascending=[True], inplace=True)
        self.convert_df(alpha_levels=alpha_levels)

class TruncNorm(FuzzyNumber):
    """abgeschnittene Normalverteilung"""
    def __init__(self, **kwargs):#, mean=0., std=1., clip=None, ppf=None):
        FuzzyNumber.__init__(self, **kwargs)
        alpha0 = kwargs.get("alpha0")
        alpha1 = kwargs.get("alpha1")
        self.clip = kwargs.get("alpha0") or [0, np.inf]
        self.ppf = kwargs.get("ppf") or [.001, .999]
        self._loc = kwargs.get("mean") or np.array(alpha0).mean()
        self._scale = kwargs.get("std") or (alpha0[1]-alpha0[0])/6.
        # print("!", (alpha0[1]-alpha0[0])/6)
        self._distr = None
        self.discretize(alpha0=self.clip, alpha1=alpha1, alpha_levels=self.number_of_alpha_levels)

    # def __str__(self):
    #     return "tnorm(%s [%.3g,%.3g])" % (self.did, self.loc, self.std)
    #
    # __repr__ = __str__

    def _get_loc(self):
        return self._loc
    def _set_loc(self, value):
        self._loc = value
    mean = loc = property(fget=_get_loc, fset=_set_loc)

    def _get_scale(self):
        return self._scale
    def _set_scale(self, value):
        self._scale = value
    std = scale = property(fget=_get_scale, fset=_set_scale)

    @property
    def distr(self):
        if self._distr is None:
            a, b = (self.clip[0] - self.loc) / self.std, (self.clip[1] - self.loc) / self.std
            self._distr = truncnorm(a=a, b=b, loc=self.mean, scale=self.std)
#             print "set_distr", self._distr, self.mean, self.std
        return self._distr

    def discretize(self, alpha0, alpha1, alpha_levels):
        assert isinstance(alpha0, collections.Sequence) and len(alpha0) == 2
        # assert isinstance(alpha1, collections.Sequence) and len(alpha1) > 0
        nn = 501
        pp = np.linspace(0,1,nn)
        ppf = self.distr.ppf(pp)
        x = np.linspace(alpha0[0],alpha0[1],nn)
        pdf = self.distr.pdf(x)
        # alphas = np.linspace(0,pdf/pdf.max(),alpha_levels)
        alphas = pdf/pdf.max()
        data = []
        for i in range(len(x)//2):
            data.append([alphas[i], x[i], x[::-1][i]])
        data.append([alphas[i+1], x[i+1], x[::-1][i+1]])
        # print(alphas)
        # print(self.distr.mean(), self.distr.std())
        # print("x", x)
        # print("ppf", ppf)
        # print("pdf", pdf)
        self.df = pd.DataFrame(columns=["alpha", "min", "max"], data=data, dtype=np.float)
        self.convert_df(alpha_levels)
        self.df.sort_values(['alpha'], ascending=[True], inplace=True)
        self.convert_df(alpha_levels=alpha_levels)
