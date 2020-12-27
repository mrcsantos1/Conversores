import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['figure.figsize'] = [25, 30]
plt.rcParams['font.size'] = 20


class Buck:
    def __init__(self, vi, vo, po, f, delta_vo, delta_il, dcm=False, percent_duty=1.0, ccm=False):
        """
        Buck Model.

        :param vi: Tensão de entrada - Vi [Volts]
        :param vo: Tensão de saída - Vo [Volts]
        :param po: Potência desejada para o conversor [W]
        :param f: Frequência de clock deste conversor [Hz]
        :param dcm: True, se é do tipo DCM
        :param percent_duty: Porcentagem do Duty CCM que é atribuída ao duty DCM. Caso a escolha seja o CCM, então este
        duty é 1
        :param ccm: True, se é do tipo CCM
        """
        if dcm:
            self.type = 1
            self.percent_duty = percent_duty
            self.name = "BUCK DCM"
            self.tx = 1.0
        elif ccm:
            self.type = 0
            self.percent_duty = percent_duty
            self.name = "BUCK CCM"
        self.vi = vi
        self.vo = vo
        self.po = po
        self.freq = f
        self.t = 1 / self.freq
        self.duty = self.__set_duty()
        self.__DT__ = self.t * self.duty
        self.io = self.__set_io()
        self.res = self.po / (self.io ** 2)

        self.ind = 1.0
        self.delta_il = delta_il * self.io
        self.il_max = self.__calc_il_max()
        self.il_min = self.__calc_il_min()

        self.cap = 1.0
        self.delta_vo = delta_vo * self.vo

        self.times = []
        self._ixt = []

    def __set_duty(self):
        duty = self.vo / self.vi  # Duty CCM
        if self.type == 1:  # Conversor DCM
            duty *= self.percent_duty
        return duty

    def __set_io(self):
        io = self.po / self.vo  # i = Po / Vo
        return io

    def __calc_il_max(self):
        self.tx = self.vi * self.__DT__ / self.vo
        if self.type == 0:  # CCM
            return self.io + (0.5 * self.delta_il)
        else:  # DCM
            return (self.vi - self.vo) * self.__DT__ / self.ind

    def __calc_il_min(self):
        if self.type == 1:  # DCM
            return 0.0
        else:  # CCM
            return self.io - (0.5 * self.delta_il)

    def set_ind(self):
        self._ixt.clear()
        if self.type == 1:  # DCM
            _l = (self.vi / self.vo) * ((self.vi - self.vo) / self.io) * (pow(self.duty, 2) * self.t / 2)
        else:  # CCM
            _l = ((self.vi - self.vo) / self.delta_il) * self.__DT__

        self.ind = _l
        self.il_max = self.__calc_il_max()

    def set_cap(self):
        if self.type == 1:  # DCM
            _c_min = (self.t / (4 * self.delta_vo)) * (((self.vi - self.vo) * self.duty * self.t / self.ind) - self.io)
        else:  # CCM
            _c_min = (self.delta_il / (self.delta_vo * 8 * self.freq))
        self.cap = _c_min

    def show_info(self):
        print(f"\n===============\t\t{self.name}\t===============")
        print(
            f"\tVo\t\t=\t{'{:.3f}'.format(self.vo)}\t\t[V]"
            f"\n\tVi\t\t=\t{'{:.3f}'.format(self.vi)}\t\t[V]"
            f"\n\tPo\t\t=\t{'{:.3f}'.format(self.po)}\t\t[W]"
            f"\n\tIo\t\t=\t{'{:.3f}'.format(self.io)}\t\t[A]"
            f"\n\tFreq\t\t=\t{'{:2.2e}'.format(self.freq)}\t[Hz]"
            f"\n\tD\t\t=\t{'{:.3f}'.format(self.duty * 100)}\t\t[%]")
        print(f"\tR\t\t=\t{'{:2.3e}'.format(self.res)}\t[Ohm]")
        print(f"\tL\t\t=\t{'{:2.3e}'.format(self.ind)}\t[H]")
        print(f"\tC\t\t=\t{'{:2.3e}'.format(self.cap)}\t[F]")
        print(f"\tiLmax\t\t=\t{'{:.3f}'.format(self.il_max)}\t\t[A]")
        print(f"\tiLmin\t\t=\t{'{:.3f}'.format(self.il_min)}\t\t[A]")

    # PLOT CORRENTE INDUTOR
    def __plot_il_ccm(self):
        x = [0, self.__DT__, self.t, self.t + self.__DT__, 2 * self.t, 2 * self.t + self.__DT__]
        y = [self.il_min, self.il_max, self.il_min, self.il_max, self.il_min, self.il_max]
        plt.plot(x, y, color='b', linewidth=3, label=self.name)
        plt.title('Corrente no Indutor - CCM')
        plt.ylabel('I_L [A]')
        plt.xlabel('Tempo [s]')
        plt.grid(True)
        self.__x_il_ccm = x
        self.__y_il_ccm = y

    def __plot_il_dcm(self):
        x = [0, self.__DT__, self.tx, self.t, self.t + self.__DT__, self.t + self.tx, 2 * self.t,
             2 * self.t + self.__DT__]
        y = [self.il_min, self.il_max, self.il_min, self.il_min, self.il_max, self.il_min, self.il_min, self.il_max]
        plt.plot(x, y, color='b', linewidth=3, label=self.name)
        plt.title('Corrente no Indutor - DCM')
        plt.ylabel('I_L [A]')
        plt.xlabel('Tempo [s]')
        plt.grid(True)
        self.__x_il_dcm = x
        self.__y_il_dcm = y

    def plot_i_ind(self):
        if self.type == 0:
            self.__plot_il_ccm()
        else:
            self.__plot_il_dcm()
        plt.legend()
        plt.show()

    # PLOT TENSÃO INDUTOR
    def __plot_vl_ccm(self):
        j = 1 / pow(self.freq, 2)
        x = [0, self.__DT__,
             self.__DT__ + j, self.t,
             self.t + j, self.t + self.__DT__,
             self.t + self.__DT__ + j, 2 * self.t,
             2 * self.t + j, 2 * self.t + self.__DT__,
             2 * self.t + self.__DT__ + j]
        vi_vo = self.vi - self.vo
        vo = self.vo
        y = [vi_vo, vi_vo,
             -vo, -vo,
             vi_vo, vi_vo,
             -vo, -vo,
             vi_vo, vi_vo,
             -vo]
        plt.plot(x, y, color='b', linewidth=3, label=self.name)
        plt.title('Tensão no Indutor - CCM')
        plt.ylabel('V_L [V]')
        plt.xlabel('Tempo [s]')
        plt.grid(True)

    def __plot_vl_dcm(self):
        x = [0, self.__DT__, self.tx, self.t, self.t + self.__DT__, self.t + self.tx, 2 * self.t,
             2 * self.t + self.__DT__]
        y = [self.il_min, self.il_max, self.il_min, self.il_min, self.il_max, self.il_min, self.il_min, self.il_max]
        plt.plot(x, y, color='b', linewidth=3, label=self.name)
        plt.title('Tensão no Indutor - DCM')
        plt.ylabel('V_L [V]')
        plt.xlabel('Tempo [s]')
        plt.grid(True)

    def plot_v_ind(self):
        if self.type == 0:
            self.__plot_vl_ccm()
        else:
            self.__plot_vl_dcm()
        plt.legend()
        plt.show()

    # PLOT CORRENTE DIODO
    def __plot_id_ccm(self):
        j = 1 / pow(self.freq, 2)
        x = [0, self.__DT__,
             self.__DT__ + j, self.t,
             self.t + j, self.t + self.__DT__,
             self.t + self.__DT__ + j, 2 * self.t,
             2 * self.t + j, 2 * self.t + self.__DT__,
             2 * self.t + self.__DT__ + j]
        y = [0, 0,
             self.il_max, self.il_min,
             0, 0,
             self.il_max, self.il_min,
             0, 0,
             self.il_max
             ]
        plt.plot(x, y, color='b', linewidth=3, label=self.name)
        plt.title('Corrente no Diodo - CCM')
        plt.ylabel('I_D [A]')
        plt.xlabel('Tempo [s]')
        plt.grid(True)

    def __plot_id_dcm(self):
        j = 1 / pow(self.freq, 2)
        x = [0, self.__DT__,
             self.__DT__ + j, self.tx,
             self.t, self.t + self.__DT__,
             self.t + self.__DT__ + j, self.t + self.tx,
             2 * self.t, 2 * self.t + self.__DT__,
             2 * self.t + self.__DT__ + j]
        y = [0, 0,
             self.il_max, 0,
             0, 0,
             self.il_max, 0,
             0, 0,
             self.il_max
             ]
        plt.plot(x, y, color='b', linewidth=3, label=self.name)
        plt.title('Corrente no Diodo - DCM')
        plt.ylabel('I_D [A]')
        plt.xlabel('Tempo [s]')
        plt.grid(True)

    def plot_i_d(self):
        if self.type == 0:
            self.__plot_id_ccm()
        else:
            self.__plot_id_dcm()
        plt.legend()
        plt.show()

    # PLOT TENSÃO DIODO
    def __plot_vd_ccm(self):
        j = 1 / pow(self.freq, 2)
        x = [0, self.__DT__,
             self.__DT__ + j, self.t,
             self.t + j, self.t + self.__DT__,
             self.t + self.__DT__ + j, 2 * self.t,
             2 * self.t + j, 2 * self.t + self.__DT__,
             2 * self.t + self.__DT__ + j]
        y = [self.vi, self.vi,
             0, 0,
             self.vi, self.vi,
             0, 0,
             self.vi, self.vi,
             0
             ]
        plt.plot(x, y, color='b', linewidth=3, label=self.name)
        plt.title('Tensão no Diodo - CCM')
        plt.ylabel('V_D [V]')
        plt.xlabel('Tempo [s]')
        plt.grid(True)

    def __plot_vd_dcm(self):
        j = 1 / pow(self.freq, 2)
        x = [0, self.__DT__,
             self.__DT__ + j, self.tx,
             self.tx + j, self.t,
             self.t + j, self.t + self.__DT__,
             self.t + self.__DT__ + j, self.t + self.tx,
             self.t + self.tx + j, 2 * self.t]
        y = [self.vi, self.vi,
             0, 0,
             self.vo, self.vo,
             self.vi, self.vi,
             0, 0,
             self.vo, self.vo
             ]
        plt.plot(x, y, color='b', linewidth=3, label=self.name)
        plt.title('Tensão no Diodo - DCM')
        plt.ylabel('V_D [V]')
        plt.xlabel('Tempo [s]')
        plt.grid(True)

    def plot_v_d(self):
        if self.type == 0:
            self.__plot_vd_ccm()
        else:
            self.__plot_vd_dcm()
        plt.legend()
        plt.show()

    # PLOT CORRENTE MOSFET
    def __plot_im_ccm(self):
        j = 1 / pow(self.freq, 2)
        x = [0, self.__DT__,
             self.__DT__ + j, self.t,
             self.t + j, self.t + self.__DT__,
             self.t + self.__DT__ + j, 2 * self.t,
             2 * self.t + j, 2 * self.t + self.__DT__,
             2 * self.t + self.__DT__ + j]
        y = [self.il_min, self.il_max,
             0, 0,
             self.il_min, self.il_max,
             0, 0,
             self.il_min, self.il_max,
             0
             ]
        plt.plot(x, y, color='b', linewidth=3, label=self.name)
        plt.title('Corrente no MOSFET - CCM')
        plt.ylabel('I_M [A]')
        plt.xlabel('Tempo [s]')
        plt.grid(True)

    def __plot_im_dcm(self):
        j = 1 / pow(self.freq, 2)
        x = [0, self.__DT__,
             self.__DT__ + j, self.tx,
             self.t, self.t + self.__DT__,
             self.t + self.__DT__ + j, self.t + self.tx,
             2 * self.t, 2 * self.t + self.__DT__,
             2 * self.t + self.__DT__ + j]
        y = [0, self.il_max,
             0, 0,
             0, self.il_max,
             0, 0,
             0, self.il_max,
             0
             ]
        plt.plot(x, y, color='b', linewidth=3, label=self.name)
        plt.title('Corrente no MOSFET - DCM')
        plt.ylabel('I_M [A]')
        plt.xlabel('Tempo [s]')
        plt.grid(True)

    def plot_i_m(self):
        if self.type == 0:
            self.__plot_im_ccm()
        else:
            self.__plot_im_dcm()
        plt.legend()
        plt.show()

    # PLOT TENSÃO MOSFET
    def __plot_vm_ccm(self):
        j = 1 / pow(self.freq, 2)
        x = [0, self.__DT__,
             self.__DT__ + j, self.t,
             self.t + j, self.t + self.__DT__,
             self.t + self.__DT__ + j, 2 * self.t,
             2 * self.t + j, 2 * self.t + self.__DT__,
             2 * self.t + self.__DT__ + j]
        y = [0, 0,
             self.vi, self.vi,
             0, 0,
             self.vi, self.vi,
             0, 0,
             self.vi
             ]
        plt.plot(x, y, color='b', linewidth=3, label=self.name)
        plt.title('Tensão no MOSFET - CCM')
        plt.ylabel('V_M [V]')
        plt.xlabel('Tempo [s]')
        plt.grid(True)

    def __plot_vm_dcm(self):
        j = 1 / pow(self.freq, 2)
        x = [0, self.__DT__,
             self.__DT__ + j, self.tx,
             self.tx + j, self.t,
             self.t + j, self.t + self.__DT__,
             self.t + self.__DT__ + j, self.t + self.tx,
             self.t + self.tx + j, 2 * self.t]
        y = [0, 0,
             self.vi, self.vi,
             (self.vi - self.vo), (self.vi - self.vo),
             0, 0,
             self.vi, self.vi,
             (self.vi - self.vo), (self.vi - self.vo)
             ]
        plt.plot(x, y, color='b', linewidth=3, label=self.name)
        plt.title('Tensão no MOSFET - DCM')
        plt.ylabel('V_M [V]')
        plt.xlabel('Tempo [s]')
        plt.grid(True)

    def plot_v_m(self):
        if self.type == 0:
            self.__plot_vm_ccm()
        else:
            self.__plot_vm_dcm()
        plt.legend()
        plt.show()

    # PLOT CORRENTE CAPACITOR
    def __plot_ic_ccm(self):
        # self.__plot_il_ccm()
        # plt.clf()
        x = self.__x_il_ccm
        y = np.array(self.__y_il_ccm) - self.io
        self.__x_ic_ccm = x
        self.__y_ic_ccm = y
        plt.plot(x, y, color='b', linewidth=3, label=self.name, )
        plt.title('Corrente no CAPACITOR - CCM')
        plt.ylabel('I_C [A]')
        plt.xlabel('Tempo [s]')
        plt.grid(True)

    def __plot_ic_dcm(self):
        # self.__plot_il_dcm()
        # plt.clf()
        x = self.__x_il_dcm
        y = np.array(self.__y_il_dcm) - self.io
        self.__x_ic_dcm = x
        self.__y_ic_dcm = y
        plt.plot(x, y, color='b', linewidth=3, label=self.name)
        plt.title('Corrente no CAPACITOR - DCM')
        plt.ylabel('I_C [A]')
        plt.xlabel('Tempo [s]')
        plt.grid(True)

    def plot_i_c(self):
        if self.type == 0:
            self.__plot_ic_ccm()
        else:
            self.__plot_ic_dcm()
        plt.legend()
        plt.show()

    # PLOT TENSÃO CAPACITOR
    def __plot_vc_ccm(self):
        # self.__plot_ic_ccm()
        # plt.clf()
        x = self.__x_ic_ccm
        y = np.ones(len(x)) * self.io * self.res
        plt.plot(x, y, color='b', linewidth=3, label=self.name)
        plt.title('Tensão no CAPACITOR - CCM')
        plt.ylabel('V_C [V]')
        plt.xlabel('Tempo [s]')
        plt.grid(True)

    def __plot_vc_dcm(self):
        # self.__plot_ic_dcm()
        # plt.clf()
        x = self.__x_ic_dcm
        y = np.ones(len(x)) * self.io * self.res
        plt.plot(x, y, color='b', linewidth=3, label=self.name)
        plt.title('Tensão no CAPACITOR - DCM')
        plt.ylabel('V_C [V]')
        plt.xlabel('Tempo [s]')
        plt.grid(True)

    def plot_v_c(self):
        """
        Método ainda não implementado!
        """
        if self.type == 0:
            self.__plot_vc_ccm()
        else:
            self.__plot_vc_dcm()
        plt.legend()
        plt.show()

    # PLOT CORRENTE CAPACITOR
    def __plot_ir_ccm(self):
        # self.__plot_il_ccm()
        # plt.clf()
        x = self.__x_il_ccm
        y = np.ones(len(self.__y_il_ccm)) * self.io
        self.__x_ir_ccm = x
        self.__y_ir_ccm = y
        plt.plot(x, y, color='b', linewidth=3, label=self.name, )
        plt.title('Corrente no RESISTOR - CCM')
        plt.ylabel('I_R [A]')
        plt.xlabel('Tempo [s]')
        plt.grid(True)

    def __plot_ir_dcm(self):
        # self.__plot_il_dcm()
        # plt.clf()
        x = self.__x_il_dcm
        y = np.ones(len(self.__y_il_dcm)) * self.io
        self.__x_ir_dcm = x
        self.__y_ir_dcm = y
        plt.plot(x, y, color='b', linewidth=3, label=self.name)
        plt.title('Corrente no RESISTOR - DCM')
        plt.ylabel('I_R [A]')
        plt.xlabel('Tempo [s]')
        plt.grid(True)

    def plot_i_r(self):
        if self.type == 0:
            self.__plot_ir_ccm()
        else:
            self.__plot_ir_dcm()
        plt.legend()
        plt.show()

    # PLOT TENSÃO RESISTOR
    def __plot_vr_ccm(self):
        # self.__plot_ic_ccm()
        # plt.clf()
        x = self.__x_ic_ccm
        y = np.ones(len(x)) * self.io * self.res
        plt.plot(x, y, color='b', linewidth=3, label=self.name)
        plt.title('Tensão no RESISTOR - CCM')
        plt.ylabel('V_R [V]')
        plt.xlabel('Tempo [s]')
        plt.grid(True)

    def __plot_vr_dcm(self):
        # self.__plot_ic_dcm()
        # plt.clf()
        x = self.__x_ic_dcm
        y = np.ones(len(x)) * self.io * self.res
        plt.plot(x, y, color='b', linewidth=3, label=self.name)
        plt.title('Tensão no RESISTOR - DCM')
        plt.ylabel('V_R [V]')
        plt.xlabel('Tempo [s]')
        plt.grid(True)

    def plot_v_r(self):
        if self.type == 0:
            self.__plot_vr_ccm()
        else:
            self.__plot_vr_dcm()
        plt.legend()
        plt.show()

    # PLOT TOTAL
    def plot_all(self):
        if self.type == 0:  # CCM
            # MOSFET
            plt.subplot(5, 2, 1)
            self.__plot_im_ccm()
            plt.subplot(5, 2, 2)
            self.__plot_vm_ccm()
            # DIODO
            plt.subplot(5, 2, 3)
            self.__plot_id_ccm()
            plt.subplot(5, 2, 4)
            self.__plot_vd_ccm()
            # INDUTOR
            plt.subplot(5, 2, 5)
            self.__plot_il_ccm()
            plt.subplot(5, 2, 6)
            self.__plot_vl_ccm()
            # CAPACITOR
            plt.subplot(5, 2, 7)
            self.__plot_ic_ccm()
            plt.subplot(5, 2, 8)
            self.__plot_vc_ccm()
            # RESISTOR
            plt.subplot(5, 2, 9)
            self.__plot_ir_ccm()
            plt.subplot(5, 2, 10)
            self.__plot_vr_ccm()
        else:
            # MOSFET
            plt.subplot(5, 2, 1)
            self.__plot_im_dcm()
            plt.subplot(5, 2, 2)
            self.__plot_vm_dcm()
            # DIODO
            plt.subplot(5, 2, 3)
            self.__plot_id_dcm()
            plt.subplot(5, 2, 4)
            self.__plot_vd_dcm()
            # INDUTOR
            plt.subplot(5, 2, 5)
            self.__plot_il_dcm()
            plt.subplot(5, 2, 6)
            self.__plot_vl_dcm()
            # CAPACITOR
            plt.subplot(5, 2, 7)
            self.__plot_ic_dcm()
            plt.subplot(5, 2, 8)
            self.__plot_vc_dcm()
            # RESISTOR
            plt.subplot(5, 2, 9)
            self.__plot_ir_dcm()
            plt.subplot(5, 2, 10)
            self.__plot_vr_dcm()

        plt.subplots_adjust(hspace=0.65)
        plt.legend()
        plt.show()
