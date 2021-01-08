import sympy as sp
import matplotlib.pyplot as plt

plt.rcParams['figure.figsize'] = [25, 30]
plt.rcParams['font.size'] = 20


class BuckBoost:
    def __init__(self, vi, vo, po, freq, percent_delt_il, percent_delt_vo, is_dcm):
        self.vi = vi
        self.vo = vo
        self.po = po
        self.io = self.po / self.vo
        self.ii = self.po / self.vi
        self.is_dcm = is_dcm
        if self.is_dcm:
            self.d = (self.vo / (self.vi + self.vo)) * 0.85  # 90% de D do CCM
            self.tx = 1.0
            self.modo = "DCM"
        else:
            self.d = self.vo / (self.vi + self.vo)
            self.modo = "CCM"

        self.f = freq
        self.t = 1 / self.f

        self.__il_max = 1.0
        self.__il_min = 1.0

        self.il = self.io / (1 - self.d)
        self.delt_il_percent = percent_delt_il

        self.delt_vo = percent_delt_vo * self.vo

        self.delt_il = self.__calc_delt_il()

        self.__DT__ = self.d * self.t

        self.L = 1.0
        self.C = 1.0
        self.R = self.po / pow(self.io, 2)

        self.efi = self.po / (self.vi * self.ii)

        self.info = {
            "Nome": "BuckBoost",
            "Modo": self.modo,
            "Vi": self.vi,
            "Ii": self.ii,
            "Vo": self.vo,
            "Io": self.io,
            "Po": self.po,
            "Eficiência": self.efi,
            "D": self.d,
            "DT": self.__DT__,
            "deltaVo": self.delt_vo,
            "deltaIl": self.delt_il, "iL_min": self.__il_min, "iL_max": self.__il_max, "iL": self.il,
            "F": self.f,
            "T": self.t,
            "L": self.L,
            "C": self.C,
            "Ro": self.R
        }

        self.set_ind()
        self.set_cap()

        self.__calc_il_min()
        self.__calc_il_max()

    def __calc_delt_il(self):
        return self.il * self.delt_il_percent

    def set_ind(self):
        if self.is_dcm:
            self.L = self.vi * pow(self.d, 2) * self.t / (2 * self.ii)
            self.info["L"] = self.L
            # return self.L
        else:
            self.L = self.vi * self.d * self.t / self.delt_il
            self.info["L"] = self.L
            # return self.L

    def set_cap(self):
        self.C = self.io * self.d * self.t / self.delt_vo
        self.info["C"] = self.C
        # return self.C

    def __calc_il_min(self):
        if self.is_dcm:
            self.tx = self.vi * self.__DT__ / self.vo
            self.__il_min = 0
        else:
            self.__il_min = self.il - 0.5 * self.delt_il

        self.info["iL_min"] = self.__il_min

    def __calc_il_max(self):
        if self.is_dcm:
            self.tx = self.vi * self.__DT__ / self.vo
            self.__il_max = self.vi * self.__DT__ / self.L
        else:
            self.__il_max = self.il + 0.5 * self.delt_il

        self.info["iL_max"] = self.__il_max

    def __il_integral(self):
        t = sp.Symbol("t")
        var = (1 / self.L) * self.vi

        return sp.integrate(var, (t, 0, self.__DT__))

    def __plot_is(self):
        k = 1e-9
        if self.is_dcm:
            x = [0, self.__DT__, self.__DT__ + k, self.tx, self.t, self.t + self.__DT__,
                 self.t + self.__DT__ + k, self.t + self.tx, 2 * self.t]
            y = [0, self.__il_max, 0, 0, 0, self.__il_max, 0, 0, 0]
            plt.plot(x, y, color='b', linewidth=3, label=str(self.modo))
            plt.title('Corrente em S - ' + self.modo)
            plt.ylabel('I_s [A]')
            plt.xlabel('Tempo [s]')
            plt.xticks()
            plt.grid(True)
        else:
            x = [0, 0 + k, self.__DT__, self.__DT__ + k, self.t, self.t + k, self.t + self.__DT__,
                 self.t + self.__DT__ + k, 2 * self.t]
            y = [0, self.__il_min, self.__il_max, 0, 0, self.__il_min, self.__il_max, 0, 0]
            plt.plot(x, y, color='b', linewidth=3, label=str(self.modo))
            plt.title('Corrente em S - ' + self.modo)
            plt.ylabel('I_s [A]')
            plt.xlabel('Tempo [s]')
            plt.xticks()
            plt.grid(True)

    def __plot_vs(self):
        k = 1e-9
        if self.is_dcm:
            x2 = [0, self.__DT__, self.__DT__ + k, self.tx, self.tx + k, self.t, self.t + k, self.t + self.__DT__,
                  self.t + self.__DT__ + k, self.t + self.tx, self.t + self.tx + k, 2 * self.t, 2 * self.t + k]
            y2 = [0, 0, self.vi + self.vo, self.vi + self.vo, self.vi, self.vi, 0, 0, self.vi + self.vo,
                  self.vi + self.vo, self.vi, self.vi, 0]
            plt.plot(x2, y2, color='g', linewidth=3, label=str(self.modo))
            plt.title('Tensão em S - ' + self.modo)
            plt.ylabel('V_s [A]')
            plt.xlabel('Tempo [s]')
            plt.grid(True)
        else:
            x2 = [0, self.__DT__, self.__DT__ + k, self.t, self.t + k, self.t + self.__DT__, self.t + self.__DT__ + k,
                  2 * self.t, 2 * self.t + k]
            y2 = [0, 0, self.vi + self.vo, self.vi + self.vo, 0, 0, self.vi + self.vo, self.vi + self.vo, 0]
            plt.plot(x2, y2, color='g', linewidth=3, label=str(self.modo))
            plt.title('Tensão em S - ' + self.modo)
            plt.ylabel('V_s [A]')
            plt.xlabel('Tempo [s]')
            plt.grid(True)

    def __plot_il(self):
        if self.is_dcm:
            x = [0, self.__DT__, self.tx, self.t, self.t + self.__DT__,
                 self.t + self.tx, 2 * self.t]
            y = [0, self.__il_max, 0, 0, self.__il_max, 0, 0]
            plt.plot(x, y, color='b', linewidth=3, label=str(self.modo))
            plt.title('Corrente em L - ' + self.modo)
            plt.ylabel('I_L [A]')
            plt.xlabel('Tempo [s]')
            plt.grid(True)
        else:
            x = [0, self.__DT__, self.t, self.t + self.__DT__, 2 * self.t]
            y = [self.__il_min, self.__il_max, self.__il_min, self.__il_max, self.__il_min]
            plt.plot(x, y, color='b', linewidth=3, label=str(self.modo))
            plt.title('Corrente em L - ' + self.modo)
            plt.ylabel('I_L [A]')
            plt.xlabel('Tempo [s]')
            plt.grid(True)

    def __plot_vl(self):
        k = 1e-9
        if self.is_dcm:
            x = [0, 0 + k, self.__DT__, self.__DT__ + k, self.tx, self.tx + k, self.t, self.t + k, self.t + self.__DT__,
                 self.t + self.__DT__ + k, self.t + self.tx, self.t + self.tx + k, 2 * self.t]
            y = [0, self.vi, self.vi, -self.vo, -self.vo, 0, 0, self.vi, self.vi, -self.vo, -self.vo, 0, 0]
            plt.plot(x, y, color='g', linewidth=3, label=str(self.modo))
            plt.title('Tensão em L - ' + self.modo)
            plt.ylabel('V_L [A]')
            plt.xlabel('Tempo [s]')
            plt.grid(True)
        else:
            x = [0, 0 + k, self.__DT__, self.__DT__ + k, self.t, self.t + k, self.t + self.__DT__,
                 self.t + self.__DT__ + k, 2 * self.t]
            y = [0, self.vi, self.vi, 0, 0, self.vi, self.vi, 0, 0]
            plt.plot(x, y, color='g', linewidth=3, label=str(self.modo))
            plt.title('Tensão em L - ' + self.modo)
            plt.ylabel('V_L [A]')
            plt.xlabel('Tempo [s]')
            plt.grid(True)

    def __plot_id(self):
        k = 1e-9
        if self.is_dcm:
            x = [0, self.__DT__, self.__DT__ + k, self.tx, self.t, self.t + self.__DT__,
                 self.t + self.__DT__ + k, self.t + self.tx, 2 * self.t]
            y = [0, 0, self.__il_max, 0, 0, 0, self.__il_max, 0, 0]
            plt.plot(x, y, color='b', linewidth=3, label=str(self.modo))
            plt.title('Corrente em D - ' + self.modo)
            plt.ylabel('I_D [A]')
            plt.xlabel('Tempo [s]')
            plt.grid(True)
        else:
            x = [0, self.__DT__, self.__DT__ + k, self.t, self.t + k, self.t + self.__DT__,
                 self.t + self.__DT__ + k, 2 * self.t, 2 * self.t + k]
            y = [0, 0, self.__il_max, self.__il_min, 0, 0, self.__il_max, self.__il_min, 0]
            plt.plot(x, y, color='b', linewidth=3, label=str(self.modo))
            plt.title('Corrente em D - ' + self.modo)
            plt.ylabel('I_D [A]')
            plt.xlabel('Tempo [s]')
            plt.grid(True)

    def __plot_vd(self):
        k = 1e-9
        if self.is_dcm:
            x = [0, self.__DT__, self.__DT__ + k, self.tx, self.tx + k, self.t, self.t + k, self.t + self.__DT__,
                 self.t + self.__DT__ + k, self.t + self.tx, self.t + self.tx + k, 2 * self.t, 2 * self.t + k]
            y = [-self.vi - self.vo, -self.vi - self.vo, 0, 0, -self.vo, -self.vo, -self.vi - self.vo,
                 -self.vi - self.vo, 0, 0, -self.vo, -self.vo, -self.vi - self.vo]
            plt.plot(x, y, color='g', linewidth=3, label=str(self.modo))
            plt.title('Tensão em D - ' + self.modo)
            plt.ylabel('V_D [A]')
            plt.xlabel('Tempo [s]')
            plt.grid(True)
        else:
            x = [0, self.__DT__, self.__DT__ + k, self.t, self.t + k, self.t + self.__DT__,
                 self.t + self.__DT__ + k, 2 * self.t, 2 * self.t + k]
            y = [-self.vi - self.vo, -self.vi - self.vo, 0, 0, -self.vi - self.vo, -self.vi - self.vo, 0, 0,
                 -self.vi - self.vo]
            plt.plot(x, y, color='g', linewidth=3, label=str(self.modo))
            plt.title('Tensão em D - ' + self.modo)
            plt.ylabel('V_D [A]')
            plt.xlabel('Tempo [s]')
            plt.grid(True)

    def __plot_ic(self):
        k = 1e-9
        if self.is_dcm:
            x = [0, self.__DT__, self.__DT__ + k, self.tx, self.t, self.t + self.__DT__,
                 self.t + self.__DT__ + k, self.t + self.tx, 2 * self.t]
            y = [-self.io, -self.io, self.__il_max - self.io, - self.io, -self.io, -self.io,
                 self.__il_max - self.io, - self.io, -self.io]
            plt.plot(x, y, color='b', linewidth=3, label=str(self.modo))
            plt.title('Corrente em C - ' + self.modo)
            plt.ylabel('I_C [A]')
            plt.xlabel('Tempo [s]')
            plt.grid(True)
        else:
            x = [0, self.__DT__, self.__DT__ + k, self.t, self.t + k, self.t + self.__DT__,
                 self.t + self.__DT__ + k, 2 * self.t, 2 * self.t + k]
            y = [-self.io, -self.io, self.__il_max - self.io, self.__il_min - self.io, -self.io, -self.io,
                 self.__il_max - self.io, self.__il_min - self.io, 0]
            plt.plot(x, y, color='b', linewidth=3, label=str(self.modo))
            plt.title('Corrente em C - ' + self.modo)
            plt.ylabel('I_C [A]')
            plt.xlabel('Tempo [s]')
            plt.grid(True)

    def __plot_vc(self):
        if self.is_dcm:
            minn = self.vo - 0.5 * self.delt_vo
            maxx = self.vo + 0.5 * self.delt_vo
            x = [0, self.__DT__, self.t, self.t + self.__DT__, 2 * self.t]
            y = [maxx, minn, maxx, minn, maxx]
            plt.plot(x, y, color='g', linewidth=3, label=str(self.modo))
            plt.title('Tensão em C - ' + self.modo)
            plt.ylabel('V_C [A]')
            plt.xlabel('Tempo [s]')
            plt.grid(True)
        else:
            minn = self.vo - 0.5 * self.delt_vo
            maxx = self.vo + 0.5 * self.delt_vo
            x = [0, self.__DT__, self.t, self.t + self.__DT__, 2 * self.t]
            y = [maxx, minn, maxx, minn, maxx]
            plt.plot(x, y, color='g', linewidth=3, label=str(self.modo))
            plt.title('Tensão em C - ' + self.modo)
            plt.ylabel('V_C [A]')
            plt.xlabel('Tempo [s]')
            plt.grid(True)

    def __plot_ir(self):
        if self.is_dcm:
            x = [0, self.t, 2 * self.t]
            y = [self.io, self.io, self.io]
            plt.plot(x, y, color='b', linewidth=3, label=str(self.modo))
            plt.title('Corrente em R - ' + self.modo)
            plt.ylabel('I_R [A]')
            plt.xlabel('Tempo [s]')
            plt.grid(True)
        else:
            x = [0, self.t, 2 * self.t]
            y = [self.io, self.io, self.io]
            plt.plot(x, y, color='b', linewidth=3, label=str(self.modo))
            plt.title('Corrente em R - ' + self.modo)
            plt.ylabel('I_R [A]')
            plt.xlabel('Tempo [s]')
            plt.grid(True)

    def __plot_vr(self):
        k = 1e-9
        if self.is_dcm:
            minn = self.vo - 0.5 * self.delt_vo
            maxx = self.vo + 0.5 * self.delt_vo
            x = [0, self.__DT__, self.t, self.t + self.__DT__, 2 * self.t]
            y = [maxx, minn, maxx, minn, maxx]
            plt.plot(x, y, color='g', linewidth=3, label=str(self.modo))
            plt.title('Tensão em R - ' + self.modo)
            plt.ylabel('V_R [A]')
            plt.xlabel('Tempo [s]')
            plt.grid(True)
        else:
            minn = self.vo - 0.5 * self.delt_vo
            maxx = self.vo + 0.5 * self.delt_vo
            x = [0, self.__DT__, self.t, self.t + self.__DT__, 2 * self.t]
            y = [maxx, minn, maxx, minn, maxx]
            plt.plot(x, y, color='g', linewidth=3, label=str(self.modo))
            plt.title('Tensão em R - ' + self.modo)
            plt.ylabel('V_R [A]')
            plt.xlabel('Tempo [s]')
            plt.grid(True)

    def plot_graphs(self, q):
        if q == 'is':
            return self.__plot_is()
        elif q == 'vs':
            return self.__plot_vs()
        elif q == 'il':
            return self.__plot_il()
        elif q == 'vl':
            return self.__plot_vl()
        elif q == 'id':
            return self.__plot_id()
        elif q == 'vd':
            return self.__plot_vd()
        elif q == 'ic':
            return self.__plot_ic()
        elif q == 'vc':
            return self.__plot_vc()
        elif q == 'ir':
            return self.__plot_ir()
        elif q == 'vr':
            return self.__plot_vr()

    def calc_vd_max(self):
        """
        Vd_max = Vi + Vo

        :return: Vd_max
        """
        if self.is_dcm:
            return self.vi + self.vo
        else:
            return self.vi + self.vo

    def calc_id_avg(self):
        """
        Se CCM:
        Id_avg = (1/T)(integral[0,T] id(t) dt)

        id(t) = 0, 0 <= t < DT e iL DT <= t < T

        :return: Ids_rms

        Se DCM:

        :return: Io
        """
        if self.is_dcm:
            return self.io
        else:
            integral = self.il * (self.t - self.__DT__)

            return integral / self.t

    def calc_id_max(self):
        """
        Se CCM:
        Id_max = Il_max

        :return: Ids_max

        Se DCM:
        :return: Vi DT / L
        """
        if self.is_dcm:
            return self.vi * self.__DT__ / self.L
        else:
            return self.__il_max

    def calc_vds_max(self):
        """
        Vds_max = Vi + Vo

        :return: Vds_max
        """
        if self.is_dcm:
            return self.vi + self.vo
        else:
            return self.vi + self.vo

    def calc_ids_rms(self):
        """
        Se CCM:

        Ids_rms = (1/T)sqrt(integral[0,T] is(t)^2 dt)

        is(t) = iL, 0 <= t < DT e 0 DT <= t < T

        Se DCM:

        Ids_rms = Vi DT sqrt(D/3) / L

        :return: Ids_rms
        """

        if self.is_dcm:
            return self.vi * self.__DT__ * sp.sqrt(self.d / 3) / self.L
        else:

            integral = (self.il ** 2) * self.__DT__ / self.t
            return sp.sqrt(integral)

    def calc_ids_max(self):
        """
        Se CCM:
        Ids_max = Il_max

        Se DCM:
        Ids_max = Vi DT / L
        :return: Ids_max
        """
        if self.is_dcm:
            return self.vi * self.__DT__ / self.L
        else:
            return self.__il_max
