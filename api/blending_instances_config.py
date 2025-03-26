from api.algorithm_instances_config import AlgorithmInstancesEnum
from image_generator.blendings.alpha_blending import AlphaBlending
from image_generator.blendings.zone_blending import ZoneBlending, ZoneBlendingNamed

alpha_blending = AlphaBlending()
zone_blending = ZoneBlending()
zone_blending_wfc = ZoneBlendingNamed(zone_gen_fun=AlgorithmInstancesEnum.wfc.value)
zone_blending_wave = ZoneBlendingNamed(zone_gen_fun=AlgorithmInstancesEnum.smooth_wave.value)
zone_blending_hex = ZoneBlendingNamed(zone_gen_fun=AlgorithmInstancesEnum.hex_pattern.value)
zone_blending_voronoi = ZoneBlendingNamed(zone_gen_fun=AlgorithmInstancesEnum.voronoi.value)

blending_instances_list = [
    alpha_blending,
    zone_blending,
    zone_blending_wfc,
    zone_blending_wave,
    zone_blending_hex,
    zone_blending_voronoi
]
