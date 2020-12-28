import pandas as pd
import matplotlib.pyplot as plt


class Converters:
    def __init__(self, ccm, dcm):
        self.__convs = {"CCM": ccm.info,
                        "DCM": dcm.info}
        self.ccm = ccm
        self.dcm = dcm

    def show_info(self):
        inf = pd.DataFrame(self.__convs)
        print(inf.head(20))

    def plot(self, L=False, C=False, D=False, R=False, S=False):
        """
        Plotar formas de ondas resultantes. Passe apenas um parâmetro a ser plotado como 'True'.
        :param L: 'True' se desejar plotar o comportamento do INDUTOR.
        :param C: 'True' se desejar plotar o comportamento do CAPACITOR.
        :param D: 'True' se desejar plotar o comportamento do DIODO.
        :param R: 'True' se desejar plotar o comportamento do RESISTOR.
        :param S: 'True' se desejar plotar o comportamento do MOSFET.
        """
        c = str()
        if L:
            c = 'l'
        elif C:
            c = 'c'
        elif D:
            c = 'd'
        elif R:
            c = 'r'
        elif S:
            c = 's'
        else:
            print("\n\nPARA PLOTAR AS FORMAS DE ONDA, PASSE UM PARÂMETRO CONFORME A DOCSTRING DESTE MÉTODO. ")
            return None
        plt.subplot(2, 2, 1)
        self.ccm.plot_graphs(q='i' + c)
        plt.subplot(2, 2, 3)
        self.ccm.plot_graphs(q='v' + c)
        plt.subplot(2, 2, 2)
        self.dcm.plot_graphs(q='i' + c)
        plt.subplot(2, 2, 4)
        self.dcm.plot_graphs(q='v' + c)
        plt.show()
