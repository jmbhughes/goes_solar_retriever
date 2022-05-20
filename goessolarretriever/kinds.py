from enum import Enum, unique, auto


@unique
class Satellite(Enum):
    GOES16 = auto()
    GOES17 = auto()


@unique
class Product(Enum):
    mag_l1b_geof = auto()
    seis_l1b_ehis = auto()
    seis_l1b_mpsh = auto()
    seis_l1b_mpsl = auto()
    seis_l1b_sgps = auto()
    suvi_l1b_fe094 = auto()
    suvi_l1b_fe131 = auto()
    suvi_l1b_fe171 = auto()
    suvi_l1b_fe195 = auto()
    suvi_l1b_fe284 = auto()
    suvi_l1b_he304 = auto()
    magn_l2_avg1m = auto()
    magn_l2_hires = auto()
    mpsh_l2_avg1m = auto()
    mpsh_l2_avg5m = auto()
    suvi_l2_ci094 = auto()
    suvi_l2_ci131 = auto()
    suvi_l2_ci171 = auto()
    suvi_l2_ci195 = auto()
    suvi_l2_ci284 = auto()
    suvi_l2_ci304 = auto()
    suvi_l2_thmap = auto()
