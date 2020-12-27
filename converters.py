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

    def plot(self):
        plt.subplot(2, 2, 1)
        self.ccm.plot_graphs(q='ir')
        plt.subplot(2, 2, 3)
        self.ccm.plot_graphs(q='vr')
        plt.subplot(2, 2, 2)
        self.dcm.plot_graphs(q='ir')
        plt.subplot(2, 2, 4)
        self.dcm.plot_graphs(q='vr')
        plt.show()
