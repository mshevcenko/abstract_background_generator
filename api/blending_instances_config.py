from api.algorithm_instances_config import AlgorithmInstancesEnum
from image_generator.blendings.alpha_blending import AlphaBlending
from image_generator.blendings.zone_blending import ZoneBlending, ZoneBlendingNamed

alpha_blending = AlphaBlending(visible_name="Transparency blending")
zone_blending = ZoneBlending(visible_name="TMP Zone blending")
zone_blending_wfc = ZoneBlendingNamed(zone_gen_fun=AlgorithmInstancesEnum.wfc.value, visible_name="Zone blending")
zone_blending_wave = ZoneBlendingNamed(zone_gen_fun=AlgorithmInstancesEnum.smooth_wave.value, visible_name="Zone blending")
zone_blending_hex = ZoneBlendingNamed(zone_gen_fun=AlgorithmInstancesEnum.hex_pattern.value, visible_name="Zone blending")
zone_blending_voronoi = ZoneBlendingNamed(zone_gen_fun=AlgorithmInstancesEnum.voronoi.value, visible_name="Zone blending")

blending_instances_list = [
    alpha_blending,
    zone_blending,
    zone_blending_wfc,
    zone_blending_wave,
    zone_blending_hex,
    zone_blending_voronoi
]
