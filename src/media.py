import mitsuba

mitsuba.set_variant("llvm_ad_rgb")

class Mist(mitsuba.Medium):
    def __init__(self, props):
        super().__init__(props)

    def phase_function(self):
        return super().phase_function()

    def sample_interaction(self, ray, sample, channel, active):
        return super().sample_interaction(ray, sample, channel, active)
    def transmittance_eval_pdf(self, mi, si, active):
        return super().transmittance_eval_pdf(mi, si, active)