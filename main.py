from buck import Buck
from buck_boost import BuckBoost
from converters import Converters
#
# ccm = BuckBoost(vi=200, vo=25, po=100, freq=10e3, percent_delt_il=0.1, percent_delt_vo=0.1, is_dcm=False)
# dcm = BuckBoost(vi=300, vo=100, po=100, freq=10e3, percent_delt_il=0.1, percent_delt_vo=0.0166, is_dcm=True)
#
# Converters(ccm=ccm, dcm=dcm).show_info()

"""
O valor do capacitor em DCM é dado como o mínimo! Sendo que na simulação, aparentemente, houve um bom resultado 
para um valor cerca de 10 vezes maior que o calculado aqui. Ou seja, de 1.51111e-05 F para 10e-5 F. 
"""

# Converters(ccm=ccm, dcm=dcm).plot(R=True)


ccm = Buck(vi=50, vo=10, po=100, f=50e3, delta_il=0.1, delta_vo=0.1, ccm=True)
dcm = Buck(vi=500, vo=10, po=100, f=50e3, delta_il=0.1, delta_vo=1, dcm=True)

ccm.set_ind()
ccm.set_cap()
dcm.set_ind()
dcm.set_cap()

ccm.show_info()
dcm.show_info()

print("calc_vd_max = ", ccm.calc_vd_max())
print("calc_id_avg = ", ccm.calc_id_avg())
print("calc_id_max = ", ccm.calc_id_max())
print("calc_vds_max = ", ccm.calc_vds_max())
print("calc_ids_rms = ", ccm.calc_ids_rms())
print("calc_ids_max = ", ccm.calc_ids_max())
