import phuzzy
from phuzzy.mpl import mix_mpl


def atest_add():


    t = phuzzy.TruncNorm(alpha0=[1, 3], alpha1=[2], number_of_alpha_levels=15)
    print(t)
    assert len(t.df)==15

    p = phuzzy.Trapezoid(alpha0=[1, 4], alpha1=[2, 3], number_of_alpha_levels=5)
    print(p)
    assert len(p.df)==5

    a = t + p

    print(a)
    print(a.df)
    mix_mpl(t)
    mix_mpl(p)
    mix_mpl(a)
    t.plot()
    p.plot()
    a.plot(show=True)

def atest_sub():


    t = phuzzy.TruncNorm(alpha0=[1, 3], alpha1=[2], number_of_alpha_levels=15, name="t")
    print(t)
    assert len(t.df)==15

    p = phuzzy.Trapezoid(alpha0=[1, 4], alpha1=[2, 3], number_of_alpha_levels=5, name="p")
    print(p)
    assert len(p.df)==5

    a = t - p
    a.name = "t-p"

    print(a)
    print(a.df)
    mix_mpl(t)
    mix_mpl(p)
    mix_mpl(a)
    t.plot()
    p.plot()
    a.plot()
    print(a.df)
    a.df.iloc[10, a.df.columns.get_loc("high")] = 1.5
    a.make_convex()
    a.name +="!"

    print(a.df)
    a.plot(show=True)


def atest_mul():


    t = phuzzy.TruncNorm(alpha0=[1, 3], alpha1=[2], number_of_alpha_levels=15, name="t")
    print(t)
    assert len(t.df)==15

    p = phuzzy.Trapezoid(alpha0=[1, 4], alpha1=[2, 3], number_of_alpha_levels=5, name="p")
    print(p)
    assert len(p.df)==5

    a = t * p
    a.name = "t*p"

    print(a)
    print(a.df)
    mix_mpl(t)
    mix_mpl(p)
    mix_mpl(a)
    t.plot()
    p.plot()
    a.plot()
    print(a.df)
    a.df.iloc[10, a.df.columns.get_loc("high")] = 8.5
    # a.make_convex()
    a.name +="!"

    print(a.df)
    a.plot(show=True)


def test_div():


    t = phuzzy.TruncNorm(alpha0=[2, 3], alpha1=[], number_of_alpha_levels=15, name="t")
    print(t)
    assert len(t.df)==15

    p = phuzzy.Trapezoid(alpha0=[0, 4], alpha1=[2, 3], number_of_alpha_levels=5, name="p")
    print(p)
    assert len(p.df)==5

    a = t ** p
    a = p ** t
    a.name = "t**p"

    print(a)
    print(a.df)
    mix_mpl(t)
    mix_mpl(p)
    mix_mpl(a)
    t.plot()
    p.plot()
    a.plot()
    print(a.df)
    # a.df.iloc[10, a.df.columns.get_loc("max")] = 8.5
    # a.make_convex()
    a.name +="!"

    print(a.df)
    a.plot(show=True)




