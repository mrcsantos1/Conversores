from buck_boost import BuckBoost
from converters import Converters

ccm = BuckBoost(vi=25, vo=200, po=100, freq=10e3, percent_delt_il=0.1, percent_delt_vo=0.1, is_dcm=False)
dcm = BuckBoost(vi=200, vo=25, po=100, freq=10e3, percent_delt_il=0.1, percent_delt_vo=0.1, is_dcm=True)

Converters(ccm=ccm, dcm=dcm).show_info()

"""
O valor do capacitor em DCM é dado como o mínimo! Sendo que na simulação, aparentemente, houve um bom resultado 
para um valor cerca de 10 vezes maior que o calculado aqui. Ou seja, de 1.51111e-05 F para 10e-5 F. 
"""

Converters(ccm=ccm, dcm=dcm).plot()
